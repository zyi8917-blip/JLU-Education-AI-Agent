"use client";

import Link from "next/link";
import { FormEvent, useMemo, useState } from "react";
import { ChatPanel, type ChatMessage } from "@/components/chat-panel";
import { readSession } from "@/lib/demo-session";
import { formatRatingSummary, labelDimension } from "@/lib/assessment/dimension-labels";
import type { PortraitData } from "@/lib/assessment/transform-report";

const STARTER_PROMPTS = [
  "我的学习力短板在哪里？",
  "给我制定一个本周学习计划",
  "怎样提高元认知能力？",
];

export function PortraitChat() {
  const session = useMemo(() => readSession(), []);
  const portraitData = session.portraitData as PortraitData | undefined;
  const studentName = portraitData?.student_name ?? session.assessmentReport?.basic_info.user_name ?? "同学";
  const hasPortrait = Boolean(Object.keys(portraitData?.total_dict ?? {}).length);

  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "portrait-intro",
      role: "agent",
      speaker: "学习力画像助手",
      content: hasPortrait
        ? `你好，${studentName}。我已了解你的测评结果，可以一起聊聊学习策略、薄弱项和本周计划。`
        : `你好，${studentName}。暂未读取到完整测评数据，你仍可向我提问；完成测评后建议会更贴合你的情况。`,
    },
  ]);

  const ratingSummary = formatRatingSummary(portraitData?.rating_dict, 5);

  async function sendMessage(text: string) {
    const trimmed = text.trim();
    if (!trimmed || busy) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      speaker: studentName,
      content: trimmed,
    };

    const history = messages
      .filter((m) => m.role === "user" || m.role === "agent")
      .map((m) => ({
        role: (m.role === "user" ? "user" : "assistant") as "user" | "assistant",
        content: m.content,
      }));

    setMessages((prev) => [...prev, userMsg]);
    setDraft("");
    setBusy(true);

    try {
      const res = await fetch("/api/portrait/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          student_id: portraitData?.student_id ?? "demo-001",
          student_name: studentName,
          message: trimmed,
          portrait_data: portraitData ?? {
            total_dict: {},
            rating_dict: {},
            feedback_dict: {},
            ready_for_chat: false,
          },
          chat_history: history,
        }),
      });

      const payload = (await res.json()) as { reply?: string };
      const reply = payload.reply ?? "暂时无法回复，请稍后再试。";

      setMessages((prev) => [
        ...prev,
        {
          id: `agent-${Date.now()}`,
          role: "agent",
          speaker: "学习力画像助手",
          content: reply,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: `agent-err-${Date.now()}`,
          role: "agent",
          speaker: "学习力画像助手",
          content: "网络不太稳定，请稍后再试。",
        },
      ]);
    } finally {
      setBusy(false);
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void sendMessage(draft);
  }

  const dimensions = Object.entries(portraitData?.total_dict ?? {}).sort(
    ([, a], [, b]) => Number(b) - Number(a),
  );

  return (
    <div className="portrait-layout">
      <aside className="card portrait-sidebar">
        <p className="soft-label">画像摘要</p>
        <h2>{studentName} 的学习力画像</h2>
        {ratingSummary ? (
          <p className="card-description">{ratingSummary}</p>
        ) : (
          <p className="empty-hint">完成测评后，这里会展示各维度评级。</p>
        )}

        {portraitData?.feedback_dict?.overall ? (
          <div className="portrait-feedback-block">
            <p className="soft-label">综合反馈</p>
            <p>{portraitData.feedback_dict.overall}</p>
          </div>
        ) : null}

        <div className="portrait-dimension-list">
          <p className="soft-label">维度得分</p>
          {dimensions.length ? (
            dimensions.map(([key, value]) => (
              <div className="metric-row" key={key}>
                <span>{labelDimension(key)}</span>
                <strong>{Number(value).toFixed(0)}</strong>
              </div>
            ))
          ) : (
            <p className="empty-hint">
              暂无得分数据。
              {!hasPortrait ? (
                <>
                  {" "}
                  <Link href="/assessment">去测评</Link>
                </>
              ) : null}
            </p>
          )}
        </div>

        <div className="portrait-starters">
          <p className="soft-label">快捷提问</p>
          {STARTER_PROMPTS.map((prompt) => (
            <button
              key={prompt}
              className="ghost-button portrait-starter-btn"
              disabled={busy}
              onClick={() => void sendMessage(prompt)}
              type="button"
            >
              {prompt}
            </button>
          ))}
        </div>
      </aside>

      <ChatPanel
        title="学习力画像助手"
        description="基于你的测评结果，提供个性化的学习策略与行动计划建议"
        messages={messages}
        composer={
          <form className="chat-input-row" onSubmit={handleSubmit}>
            <input
              value={draft}
              disabled={busy}
              onChange={(e) => setDraft(e.target.value)}
              placeholder="输入你想了解的学习问题..."
            />
            <button className="primary-button" disabled={busy || !draft.trim()} type="submit">
              {busy ? "思考中..." : "发送"}
            </button>
          </form>
        }
      />
    </div>
  );
}
