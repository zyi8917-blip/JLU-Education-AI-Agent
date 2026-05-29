"use client";

import {
  FormEvent,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { ChatPanel, type ChatMessage } from "@/components/chat-panel";
import { buildCourseChatMessages } from "@/lib/chat/build-messages";
import { streamCourseChat } from "@/lib/chat/stream-client";
import { courseQaData } from "@/data/demo-data";

type CourseQaEntry = {
  id: string;
  question: string;
  keywords: string[];
  answer: string;
};

function matchAnswer(input: string, entries: CourseQaEntry[]) {
  const normalized = input.trim().toLowerCase();
  return entries.find((entry) =>
    entry.keywords.some((keyword) => normalized.includes(keyword.toLowerCase())),
  );
}

const LS_LLM_KEY = "future-learning-use-llm";

function envForcesLlm(): boolean {
  return process.env.NEXT_PUBLIC_USE_LLM === "true";
}

type CourseQaPanelProps = {
  slideContext: string;
};

export function CourseQaPanel({ slideContext }: CourseQaPanelProps) {
  const envLlm = envForcesLlm();
  const [storageLlm, setStorageLlm] = useState(false);
  const [busy, setBusy] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;
    setStorageLlm(window.localStorage.getItem(LS_LLM_KEY) === "true");
  }, []);

  const useLlm = envLlm || storageLlm;

  const introContent = useLlm
    ? "推荐问题或自由提问。大模型模式已开启：服务端 /api/chat 流式输出，并结合 Chroma RAG 检索课件与 QA 知识库（需 npm run rag:index）。"
    : "你可以点选推荐问题，也可以直接补充提问。当前为脚本演示模式；勾选下方「大模型模式」并配置 .env.local 后切换为真实模型。";

  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "course-agent-intro",
      role: "agent",
      speaker: "课堂 Agent",
      content: introContent,
    },
  ]);

  useEffect(() => {
    setMessages((prev) => {
      if (prev.length === 0 || prev[0].id !== "course-agent-intro") return prev;
      const [, ...rest] = prev;
      return [
        {
          id: "course-agent-intro",
          role: "agent",
          speaker: "课堂 Agent",
          content: introContent,
        },
        ...rest,
      ];
    });
  }, [introContent]);

  const entries = courseQaData.entries as CourseQaEntry[];
  const suggestedQuestions = courseQaData.suggestedQuestions as string[];

  const setLlmPreference = useCallback((enabled: boolean) => {
    if (typeof window === "undefined") return;
    if (enabled) window.localStorage.setItem(LS_LLM_KEY, "true");
    else window.localStorage.removeItem(LS_LLM_KEY);
    setStorageLlm(enabled);
  }, []);

  const stopGeneration = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    setBusy(false);
  }, []);

  const submitScript = useCallback(
    (trimmed: string) => {
      const matched = matchAnswer(trimmed, entries);
      setMessages((current) => [
        ...current,
        {
          id: `user-${current.length + 1}`,
          role: "user",
          speaker: "你",
          content: trimmed,
        },
        {
          id: `agent-${current.length + 2}`,
          role: "agent",
          speaker: "课堂 Agent",
          content: matched?.answer ?? courseQaData.fallbackAnswer,
        },
      ]);
    },
    [entries],
  );

  const submitLlm = useCallback(
    async (trimmed: string) => {
      const userMsg: ChatMessage = {
        id: `user-${Date.now()}`,
        role: "user",
        speaker: "你",
        content: trimmed,
      };
      const agentId = `agent-${Date.now() + 1}`;

      setMessages((prev) => [
        ...prev,
        userMsg,
        {
          id: agentId,
          role: "agent",
          speaker: "课堂 Agent",
          content: "",
        },
      ]);

      const apiMessages = buildCourseChatMessages(
        [...messages, userMsg],
        slideContext,
      );

      const ac = new AbortController();
      abortRef.current = ac;
      setBusy(true);

      await streamCourseChat(
        { mode: "course", messages: apiMessages, userQuery: trimmed },
        {
          signal: ac.signal,
          onDelta: (delta) => {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === agentId ? { ...m, content: m.content + delta } : m,
              ),
            );
          },
          onError: (err) => {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === agentId
                  ? {
                      ...m,
                      content:
                        m.content ||
                        `[请求失败] ${err}。请检查 .env.local 与网络，或改用脚本模式。`,
                    }
                  : m,
              ),
            );
          },
        },
      );

      abortRef.current = null;
      setBusy(false);
    },
    [messages, slideContext],
  );

  const submitQuestion = useCallback(
    async (question: string) => {
      const trimmed = question.trim();
      if (!trimmed || busy) return;

      setDraft("");

      if (!useLlm) {
        submitScript(trimmed);
        return;
      }

      await submitLlm(trimmed);
    },
    [busy, submitLlm, submitScript, useLlm],
  );

  useEffect(() => {
    return () => {
      abortRef.current?.abort();
    };
  }, []);

  const composer = useMemo(
    () => (
      <div className="qa-composer">
        <div className="suggestion-row" style={{ alignItems: "center", gap: 12 }}>
          {!envLlm ? (
            <label className="muted-text" style={{ display: "flex", gap: 8 }}>
              <input
                type="checkbox"
                checked={storageLlm}
                onChange={(e) => setLlmPreference(e.target.checked)}
              />
              大模型模式（写入 localStorage）
            </label>
          ) : (
            <span className="muted-text">已通过 NEXT_PUBLIC_USE_LLM 强制大模型</span>
          )}
          {busy ? (
            <button className="ghost-button" type="button" onClick={stopGeneration}>
              停止生成
            </button>
          ) : null}
        </div>
        <div className="suggestion-row">
          {suggestedQuestions.map((question) => (
            <button
              key={question}
              className="tag-button"
              onClick={() => void submitQuestion(question)}
              type="button"
              disabled={busy}
            >
              {question}
            </button>
          ))}
        </div>
        <form
          className="composer-form"
          onSubmit={(event: FormEvent<HTMLFormElement>) => {
            event.preventDefault();
            void submitQuestion(draft);
          }}
        >
          <textarea
            rows={4}
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder="补充提问，例如：这两页内容和智能体有什么关系？"
            disabled={busy}
          />
          <div className="composer-actions">
            <span className="muted-text">
              {useLlm ? "流式输出中可点击「停止生成」" : "脚本模式输出稳定，适合无 Key 演示"}
            </span>
            <button className="primary-button" type="submit" disabled={busy}>
              发送问题
            </button>
          </div>
        </form>
      </div>
    ),
    [
      busy,
      draft,
      envLlm,
      setLlmPreference,
      stopGeneration,
      storageLlm,
      submitQuestion,
      suggestedQuestions,
      useLlm,
    ],
  );

  return (
    <ChatPanel
      title="课堂问答 Agent"
      description="脚本模式 / 大模型流式 + Chroma RAG"
      messages={messages}
      composer={composer}
    />
  );
}
