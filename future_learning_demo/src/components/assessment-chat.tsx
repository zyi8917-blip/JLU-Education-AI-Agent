"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useMemo, useState } from "react";
import { assessmentQuestions } from "@/data/assessment-questions";
import { completeAssessment } from "@/lib/demo-session";
import { ChatPanel, type ChatMessage } from "@/components/chat-panel";

export function AssessmentChat() {
  const router = useRouter();
  const [index, setIndex] = useState(0);
  const [draft, setDraft] = useState("");
  const [answers, setAnswers] = useState<Array<{ prompt: string; answer: string }>>(
    [],
  );

  const currentQuestion = assessmentQuestions[index];

  const messages = useMemo<ChatMessage[]>(() => {
    const base: ChatMessage[] = [
      {
        id: "intro",
        role: "agent",
        speaker: "测评智能体",
        content:
          "接下来我们会用 10 个问题快速了解你的学习状态。整个过程不做真实评分，你只需要自然回答即可。",
      },
    ];

    answers.forEach((item, answerIndex) => {
      base.push({
        id: `question-${answerIndex}`,
        role: "agent",
        speaker: "测评智能体",
        content: item.prompt,
      });
      base.push({
        id: `answer-${answerIndex}`,
        role: "user",
        speaker: "你",
        content: item.answer,
      });
    });

    if (currentQuestion) {
      base.push({
        id: currentQuestion.id,
        role: "agent",
        speaker: `测评智能体 / ${currentQuestion.dimension}`,
        content: currentQuestion.prompt,
      });
    }

    return base;
  }, [answers, currentQuestion]);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!draft.trim() || !currentQuestion) {
      return;
    }

    const nextAnswers = [
      ...answers,
      { prompt: currentQuestion.prompt, answer: draft.trim() },
    ];
    setAnswers(nextAnswers);
    setDraft("");

    if (index === assessmentQuestions.length - 1) {
      completeAssessment();
      router.push("/assessment/result");
      return;
    }

    setIndex(index + 1);
  }

  return (
    <ChatPanel
      title="学习力面试式测评"
      description={`共 ${assessmentQuestions.length} 题，当前第 ${Math.min(index + 1, assessmentQuestions.length)} 题`}
      messages={messages}
      composer={
        <form className="composer-form" onSubmit={handleSubmit}>
          <textarea
            rows={4}
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder={currentQuestion?.placeholder ?? "请输入你的回答"}
          />
          <div className="composer-actions">
            <span className="muted-text">
              当前维度：{currentQuestion?.dimension ?? "已完成"}
            </span>
            <button className="primary-button" type="submit">
              {index === assessmentQuestions.length - 1 ? "提交并查看结果" : "提交下一题"}
            </button>
          </div>
        </form>
      }
    />
  );
}
