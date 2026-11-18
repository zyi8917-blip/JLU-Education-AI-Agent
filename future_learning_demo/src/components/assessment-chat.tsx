"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useMemo, useState } from "react";
import { assessmentQuestions } from "@/data/assessment-questions";
import { saveAssessmentResult } from "@/lib/demo-session";
import { submitAssessmentAnswers } from "@/lib/assessment/submit";
import { ChatPanel, type ChatMessage } from "@/components/chat-panel";

export function AssessmentChat() {
  const router = useRouter();
  const [index, setIndex] = useState(0);
  const [draft, setDraft] = useState("");
  const [answers, setAnswers] = useState<
    Array<{ question_id: string; prompt: string; answer: string; dimension: string }>
  >([]);
  const [submitting, setSubmitting] = useState(false);

  const currentQuestion = assessmentQuestions[index];

  const messages = useMemo<ChatMessage[]>(() => {
    const base: ChatMessage[] = [
      {
        id: "intro",
        role: "agent",
        speaker: "测评智能体",
        content:
          "接下来我们会用 10 个问题了解你的学习状态。请像聊天一样自然回答即可。",
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

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!draft.trim() || !currentQuestion || submitting) {
      return;
    }

    const nextAnswers = [
      ...answers,
      {
        question_id: currentQuestion.id,
        prompt: currentQuestion.prompt,
        answer: draft.trim(),
        dimension: currentQuestion.dimension,
      },
    ];
    setAnswers(nextAnswers);
    setDraft("");

    if (index === assessmentQuestions.length - 1) {
      setSubmitting(true);
      try {
        const result = await submitAssessmentAnswers(nextAnswers);
        saveAssessmentResult({
          report: result.report,
          portrait_data: result.portrait_data,
          source: result.source,
        });
        router.push("/assessment/result");
      } catch {
        setSubmitting(false);
      }
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
            <button className="primary-button" disabled={submitting} type="submit">
              {submitting
                ? "生成报告中..."
                : index === assessmentQuestions.length - 1
                  ? "提交并查看结果"
                  : "提交下一题"}
            </button>
          </div>
        </form>
      }
    />
  );
}
