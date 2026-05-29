"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { assessmentQuestions } from "@/data/assessment-questions";
import { completeAssessment } from "@/lib/demo-session";

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
  const [answers, setAnswers] = useState<Array<{ prompt: string; answer: string }>>(
    [],
  );
  const [isRecording, setIsRecording] = useState(false);
  const [interimText, setInterimText] = useState("");
  const [speechSupported, setSpeechSupported] = useState(false);
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
    if (typeof window === "undefined" || !currentQuestion?.prompt) {
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
  }, [currentQuestion?.id, currentQuestion?.prompt]);

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
    setInterimText("");

    if (index === assessmentQuestions.length - 1) {
      completeAssessment();
      router.push("/assessment/result");
      return;
    }

    setIndex(index + 1);
  }

  return (
    <section className="assessment-interview-shell">
      <aside className="assessment-side-panel">
        <p className="soft-label">测评说明</p>
        <h2>一对一学习力面谈</h2>
        <p>
          参考 `learning_power` 的语音面谈节奏，当前页面聚焦单题作答。你可以直接输入，也可以点击语音按钮进行识别。
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
            {isRecording ? "正在倾听你的回答..." : "当前问题已朗读，可开始作答"}
          </p>
        </div>

        <div className="assessment-question-card">
          <p className="soft-label">当前问题</p>
          <h3>{currentQuestion.prompt}</h3>
          <p>
            保持自然表达即可。本 Demo 不做真实计算，重点展示学习者与智能体的一对一测评体验。
          </p>
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
              disabled={!speechSupported}
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

          <textarea
            rows={8}
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder={currentQuestion.placeholder}
          />

          <div className="assessment-submit-row">
            <span className="input-tip">第 {index + 1} 题完成后将自动进入下一题</span>
            <button className="primary-button" type="submit">
              {index === assessmentQuestions.length - 1 ? "提交并生成结果" : "提交当前回答"}
            </button>
          </div>
        </form>
      </section>
    </section>
  );
}
