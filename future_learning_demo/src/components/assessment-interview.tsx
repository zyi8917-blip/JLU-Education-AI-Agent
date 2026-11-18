"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { assessmentQuestions } from "@/data/assessment-questions";
import { saveAssessmentResult } from "@/lib/demo-session";
import { submitAssessmentAnswers } from "@/lib/assessment/submit";

type SpeechRecognitionLike = {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onresult: ((event: unknown) => void) | null;
  onend: (() => void) | null;
  onerror: (() => void) | null;
  start: () => void;
  stop: () => void;
};

type RecognitionWindow = Window & {
  SpeechRecognition?: new () => SpeechRecognitionLike;
  webkitSpeechRecognition?: new () => SpeechRecognitionLike;
};

type RecognitionResultEvent = {
  results: ArrayLike<{
    0: { transcript: string };
    isFinal: boolean;
    length: number;
  }>;
};

export function AssessmentInterview() {
  const router = useRouter();
  const [index, setIndex] = useState(0);
  const [draft, setDraft] = useState("");
  const [answers, setAnswers] = useState<
    Array<{ question_id: string; prompt: string; answer: string; dimension: string }>
  >([]);
  const [isRecording, setIsRecording] = useState(false);
  const [interimText, setInterimText] = useState("");
  const [speechSupported, setSpeechSupported] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState("");
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);

  const currentQuestion = assessmentQuestions[index];

  useEffect(() => {
    const browserWindow = window as RecognitionWindow;
    const Recognition =
      browserWindow.SpeechRecognition ?? browserWindow.webkitSpeechRecognition;

    if (!Recognition) {
      setSpeechSupported(false);
      return;
    }

    setSpeechSupported(true);
    const recognition = new Recognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "zh-CN";

    recognition.onresult = (rawEvent) => {
      const event = rawEvent as RecognitionResultEvent;
      let finalText = "";
      let preview = "";

      for (let i = 0; i < event.results.length; i += 1) {
        const segment = event.results[i]?.[0]?.transcript ?? "";
        if (event.results[i]?.isFinal) {
          finalText += segment;
        } else {
          preview += segment;
        }
      }

      if (finalText) {
        setDraft((current) => `${current}${finalText}`.trimStart());
      }

      setInterimText(preview);
    };

    recognition.onend = () => {
      setIsRecording(false);
      setInterimText("");
    };

    recognition.onerror = () => {
      setIsRecording(false);
      setInterimText("");
    };

    recognitionRef.current = recognition;

    return () => {
      recognition.stop();
      recognitionRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (typeof window === "undefined" || !currentQuestion?.prompt || submitting) {
      return;
    }

    const utterance = new SpeechSynthesisUtterance(currentQuestion.prompt);
    utterance.lang = "zh-CN";
    utterance.rate = 1;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);

    return () => {
      window.speechSynthesis.cancel();
    };
  }, [currentQuestion?.id, currentQuestion?.prompt, submitting]);

  const recentHighlights = useMemo(() => answers.slice(-3).reverse(), [answers]);

  function toggleRecording() {
    if (!recognitionRef.current) {
      return;
    }

    if (isRecording) {
      recognitionRef.current.stop();
      setIsRecording(false);
      return;
    }

    recognitionRef.current.start();
    setIsRecording(true);
  }

  async function finalizeAssessment(
    allAnswers: Array<{
      question_id: string;
      prompt: string;
      answer: string;
      dimension: string;
    }>,
  ) {
    setSubmitting(true);
    setSubmitError("");

    try {
      const result = await submitAssessmentAnswers(allAnswers);
      saveAssessmentResult({
        report: result.report,
        portrait_data: result.portrait_data,
        source: result.source,
      });
      router.push("/assessment/result");
    } catch (error) {
      setSubmitError(
        error instanceof Error ? error.message : "提交失败，请检查网络后重试",
      );
      setSubmitting(false);
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
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
    setInterimText("");

    if (index === assessmentQuestions.length - 1) {
      void finalizeAssessment(nextAnswers);
      return;
    }

    setIndex(index + 1);
  }

  return (
    <section className="assessment-interview-shell">
      {submitting ? (
        <div className="center-screen assessment-submit-overlay">
          <div className="loading-card">
            <p className="soft-label">正在分析</p>
            <strong>正在生成你的学习力报告…</strong>
            <p>请稍候，通常需要几秒到一分钟</p>
          </div>
        </div>
      ) : null}

      <aside className="assessment-side-panel">
        <p className="soft-label">测评说明</p>
        <h2>一对一学习力面谈</h2>
        <p>
          共 10 道题，涵盖学习动机、学习体验、延迟满足、问题解决与学习策略。请尽量结合真实经历作答。
        </p>

        <div className="assessment-progress-card">
          <span className="progress-step">
            {index + 1} / {assessmentQuestions.length}
          </span>
          <strong>{currentQuestion.dimension}</strong>
          <p>当前聚焦维度</p>
        </div>

        <div className="assessment-side-block">
          <p className="soft-label">最近完成</p>
          {recentHighlights.length ? (
            <ul className="summary-list">
              {recentHighlights.map((item, itemIndex) => (
                <li key={`${item.prompt}-${itemIndex}`}>
                  <strong>{item.prompt}</strong>
                  <span>{item.answer}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="empty-hint">完成作答后，这里会展示你最近的回答摘要。</p>
          )}
        </div>
      </aside>

      <section className="assessment-main-stage">
        <div className="assessment-agent-panel">
          <div className="agent-orbit" aria-hidden="true" />
          <div className="agent-avatar">
            <div className="agent-avatar-core">AI</div>
          </div>
          <p className="agent-name">学习力测评官</p>
          <p className="agent-status">
            {submitting
              ? "正在汇总你的回答并生成画像..."
              : isRecording
                ? "正在倾听你的回答..."
                : "当前问题已朗读，可开始作答"}
          </p>
        </div>

        <div className="assessment-question-card">
          <p className="soft-label">当前问题</p>
          <h3>{currentQuestion.prompt}</h3>
          <p>保持自然表达即可。最后一题提交后，系统将自动生成报告与画像。</p>
        </div>

        <form className="assessment-answer-card" onSubmit={handleSubmit}>
          <div className="assessment-answer-header">
            <div>
              <p className="soft-label">你的回答</p>
              <p className="input-tip">
                支持文本输入；若浏览器支持，也可以使用语音识别补充内容。
              </p>
            </div>
            <button
              className={isRecording ? "voice-trigger voice-trigger-active" : "voice-trigger"}
              disabled={!speechSupported || submitting}
              onClick={toggleRecording}
              type="button"
            >
              {speechSupported ? (isRecording ? "停止录音" : "语音输入") : "浏览器不支持语音"}
            </button>
          </div>

          {isRecording || interimText ? (
            <div className="recording-banner">
              <div className="recording-dots" aria-hidden="true">
                <span />
                <span />
                <span />
              </div>
              <span>{interimText || "正在识别，请继续说话..."}</span>
            </div>
          ) : null}

          {submitError ? <p className="error-hint">{submitError}</p> : null}

          <textarea
            rows={8}
            value={draft}
            disabled={submitting}
            onChange={(event) => setDraft(event.target.value)}
            placeholder={currentQuestion.placeholder}
          />

          <div className="assessment-submit-row">
            <span className="input-tip">第 {index + 1} 题完成后将自动进入下一题</span>
            <button className="primary-button" disabled={submitting} type="submit">
              {index === assessmentQuestions.length - 1 ? "提交并生成结果" : "提交当前回答"}
            </button>
          </div>
        </form>
      </section>
    </section>
  );
}
