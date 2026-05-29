"use client";

import { FormEvent, useMemo, useState } from "react";
import { completeProject } from "@/lib/demo-session";
import { ChatPanel, type ChatMessage } from "@/components/chat-panel";
import { projectScenario } from "@/data/demo-data";
import { ProjectFeedbackModal } from "@/components/project-feedback-modal";

const agentResponses = [
  "我们先明确服务对象。这个课堂助教 Agent 是服务全体学生、教师，还是只服务课堂中跟不上节奏的学习者？",
  "很好，接下来补全核心功能。建议至少覆盖课前导学、课中答疑和课后反馈三个环节。",
  "现在请你把使用流程讲清楚：学生和教师在一节课里分别如何与 Agent 互动？",
  "最后补一条风险提醒，例如错误答案、注意力依赖或隐私提示，这会让你的方案更完整。",
];

export function ProjectChat() {
  const [draft, setDraft] = useState("");
  const [round, setRound] = useState(0);
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "project-intro",
      role: "agent",
      speaker: "课程教练 Agent",
      content:
        "我们会一起完成一个课堂助教 Agent 方案。你可以按自己的思路回答，也可以直接围绕左侧里程碑逐步补全。",
    },
  ]);

  const nextPrompt = agentResponses[Math.min(round, agentResponses.length - 1)];

  function handleSend(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!draft.trim()) {
      return;
    }

    const nextRound = Math.min(round + 1, agentResponses.length - 1);
    setMessages((current) => [
      ...current,
      {
        id: `project-user-${current.length + 1}`,
        role: "user",
        speaker: "你",
        content: draft.trim(),
      },
      {
        id: `project-agent-${current.length + 2}`,
        role: "agent",
        speaker:
          nextRound < 2 ? "方案设计 Agent" : nextRound < 3 ? "课程教练 Agent" : "评估反馈 Agent",
        content: agentResponses[nextRound],
      },
    ]);
    setDraft("");
    setRound(nextRound);
  }

  function handleSubmitPlan() {
    completeProject();
    setOpen(true);
  }

  const composer = useMemo(
    () => (
      <div className="qa-composer">
        <div className="suggestion-row">
          {projectScenario.starterPrompts.map((prompt) => (
            <button
              className="tag-button"
              key={prompt}
              onClick={() => setDraft(prompt)}
              type="button"
            >
              {prompt}
            </button>
          ))}
        </div>
        <form className="composer-form" onSubmit={handleSend}>
          <textarea
            rows={5}
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder={nextPrompt}
          />
          <div className="composer-actions">
            <span className="muted-text">完成几轮对话后，可直接提交成果触发演示反馈</span>
            <div className="inline-actions">
              <button className="ghost-button" type="submit">
                发送想法
              </button>
              <button className="primary-button" onClick={handleSubmitPlan} type="button">
                提交成果
              </button>
            </div>
          </div>
        </form>
      </div>
    ),
    [draft, nextPrompt, projectScenario.starterPrompts],
  );

  return (
    <>
      <ChatPanel
        title="PBL 对话推进区"
        description="通过几轮固定对话，把模糊需求整理成可展示的课堂助教 Agent 方案"
        messages={messages}
        composer={composer}
      />
      <ProjectFeedbackModal onClose={() => setOpen(false)} open={open} />
    </>
  );
}
