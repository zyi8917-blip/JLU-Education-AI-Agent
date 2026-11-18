"use client";

import {
  FormEvent,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { completeProject } from "@/lib/demo-session";
import { ChatPanel, type ChatMessage } from "@/components/chat-panel";
import { projectScenario } from "@/data/demo-data";
import { ProjectFeedbackModal } from "@/components/project-feedback-modal";
import { ProjectMilestoneList } from "@/components/project-milestone-list";
import {
  buildProjectChatMessages,
  buildProjectSummaryMessages,
} from "@/lib/chat/build-messages";
import { streamCourseChat } from "@/lib/chat/stream-client";
import {
  getProjectAgentName,
  resolveProjectPhase,
} from "@/lib/chat/project-prompts";

const LS_LLM_KEY = "future-learning-use-llm";

const scriptReplies = {
  coach: "我们先明确服务对象。这个课堂助教 Agent 是服务全体学生、教师，还是只服务课堂中跟不上节奏的学习者？请结合具体场景说明。",
  design:
    "很好。接下来请补全至少 3 个核心功能，建议覆盖课前导学、课中答疑和课后反馈，并简要说明每个功能解决什么问题。",
  review:
    "现在请把课堂使用流程讲清楚：学生和教师在一节课里分别如何与 Agent 互动？最后补充 1 条风险提醒（如幻觉、隐私或过度依赖）。",
};

function envForcesLlm(): boolean {
  return process.env.NEXT_PUBLIC_USE_LLM === "true";
}

async function streamToText(
  messages: ReturnType<typeof buildProjectSummaryMessages>,
  signal?: AbortSignal,
): Promise<string> {
  let text = "";
  await streamCourseChat(
    { mode: "project", messages, userQuery: "生成方案摘要" },
    {
      signal,
      onDelta: (delta) => {
        text += delta;
      },
    },
  );
  return text.trim();
}

export function ProjectChat() {
  const envLlm = envForcesLlm();
  const [storageLlm, setStorageLlm] = useState(false);
  const [busy, setBusy] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [open, setOpen] = useState(false);
  const [deliverable, setDeliverable] = useState("");
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;
    setStorageLlm(window.localStorage.getItem(LS_LLM_KEY) === "true");
  }, []);

  const useLlm = envLlm || storageLlm;

  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "project-intro",
      role: "agent",
      speaker: "课程教练 Agent",
      content:
        "欢迎进入 PBL 项目实践。我们将一起完成「课堂助教 Agent 应用方案」。你可以按左侧里程碑逐步回答，也可以自由表达想法。",
    },
  ]);

  const userTurns = messages.filter((m) => m.role === "user").length;
  const currentPhase = resolveProjectPhase(userTurns);
  const currentAgent = getProjectAgentName(currentPhase);

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
    setSubmitting(false);
  }, []);

  const submitScript = useCallback(
    (trimmed: string, turnAfter: number) => {
      const phase = resolveProjectPhase(turnAfter);
      setMessages((current) => [
        ...current,
        {
          id: `project-user-${current.length + 1}`,
          role: "user",
          speaker: "你",
          content: trimmed,
        },
        {
          id: `project-agent-${current.length + 2}`,
          role: "agent",
          speaker: getProjectAgentName(phase),
          content: scriptReplies[phase],
        },
      ]);
    },
    [],
  );

  const submitLlm = useCallback(
    async (trimmed: string) => {
      const userMsg: ChatMessage = {
        id: `project-user-${Date.now()}`,
        role: "user",
        speaker: "你",
        content: trimmed,
      };
      const turnAfter = userTurns + 1;
      const agentName = getProjectAgentName(resolveProjectPhase(turnAfter));
      const agentId = `project-agent-${Date.now() + 1}`;

      setMessages((prev) => [
        ...prev,
        userMsg,
        { id: agentId, role: "agent", speaker: agentName, content: "" },
      ]);

      const apiMessages = buildProjectChatMessages([...messages, userMsg]);
      const ac = new AbortController();
      abortRef.current = ac;
      setBusy(true);

      await streamCourseChat(
        { mode: "project", messages: apiMessages, userQuery: trimmed },
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
                        `[请求失败] ${err}。请检查 .env.local 或改用脚本模式。`,
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
    [messages, userTurns],
  );

  const handleSend = useCallback(
    async (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      const trimmed = draft.trim();
      if (!trimmed || busy) return;
      setDraft("");

      if (!useLlm) {
        submitScript(trimmed, userTurns + 1);
        return;
      }
      await submitLlm(trimmed);
    },
    [busy, draft, submitLlm, submitScript, useLlm, userTurns],
  );

  const handleSubmitPlan = useCallback(async () => {
    if (submitting) return;
    setSubmitting(true);

    let summary = "";
    if (useLlm) {
      try {
        const ac = new AbortController();
        abortRef.current = ac;
        summary = await streamToText(
          buildProjectSummaryMessages(messages),
          ac.signal,
        );
      } catch {
        summary = "";
      }
      abortRef.current = null;
    }

    if (!summary) {
      summary = `# 课堂助教 Agent 方案摘要（脚本整理）

## 1. 服务对象与场景
基于你的对话：${messages.filter((m) => m.role === "user").map((m) => m.content).slice(0, 1).join("") || "待补充"}

## 2. 三个核心功能
${projectScenario.milestones[1]}

## 3. 课堂使用流程
${projectScenario.milestones[2]}

## 4. 风险提醒与优化建议
${projectScenario.milestones[3]}

## 5. 学习力提升点
- 问题结构化能力
- 学习路径设计意识
- AI 使用边界意识`;
    }

    completeProject(summary);
    setDeliverable(summary);
    setOpen(true);
    setSubmitting(false);
  }, [messages, submitting, useLlm]);

  useEffect(() => {
    return () => abortRef.current?.abort();
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
              大模型模式（多 Agent 流式协作）
            </label>
          ) : (
            <span className="muted-text">大模型模式已开启</span>
          )}
          <span className="muted-text">当前 Agent：{currentAgent}</span>
          {busy || submitting ? (
            <button className="ghost-button" type="button" onClick={stopGeneration}>
              停止生成
            </button>
          ) : null}
        </div>
        <div className="suggestion-row">
          {projectScenario.starterPrompts.map((prompt) => (
            <button
              className="tag-button"
              key={prompt}
              onClick={() => setDraft(prompt)}
              type="button"
              disabled={busy}
            >
              {prompt}
            </button>
          ))}
        </div>
        <form className="composer-form" onSubmit={(e) => void handleSend(e)}>
          <textarea
            rows={5}
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder={`向 ${currentAgent} 补充你的想法…`}
            disabled={busy}
          />
          <div className="composer-actions">
            <span className="muted-text">
              已完成 {userTurns} 轮对话 · 提交后自动生成方案摘要
            </span>
            <div className="inline-actions">
              <button className="ghost-button" type="submit" disabled={busy}>
                发送想法
              </button>
              <button
                className="primary-button"
                disabled={busy || submitting || userTurns === 0}
                onClick={() => void handleSubmitPlan()}
                type="button"
              >
                {submitting ? "生成摘要中…" : "提交成果"}
              </button>
            </div>
          </div>
        </form>
      </div>
    ),
    [
      busy,
      currentAgent,
      draft,
      envLlm,
      handleSend,
      handleSubmitPlan,
      setLlmPreference,
      stopGeneration,
      storageLlm,
      submitting,
      userTurns,
    ],
  );

  return (
    <>
      <div className="project-chat-stack">
        <section className="card milestone-card compact-card">
          <p className="card-label">里程碑进度</p>
          <ProjectMilestoneList messages={messages} />
        </section>
        <ChatPanel
          title="PBL 对话推进区"
          description="课程教练 / 方案设计 / 评估反馈 · 服务端 SSE + 上下文工程"
          messages={messages}
          composer={composer}
        />
      </div>
      <ProjectFeedbackModal
        deliverable={deliverable}
        onClose={() => setOpen(false)}
        open={open}
      />
    </>
  );
}
