'use client';

import { useMemo, useState, useTransition } from 'react';
import type {
  KitQuizAnswerMap,
  KitQuizQuestion,
  KitQuizQuestionResult,
  KitQuizScene,
  KitSceneRendererProps,
} from '../types';

function joinClassNames(...values: Array<string | undefined>) {
  return values.filter(Boolean).join(' ');
}

function normalizeAnswers(value: string | string[] | undefined) {
  if (!value) return [];
  return Array.isArray(value) ? value : [value];
}

function arraysEqual(left: string[], right: string[]) {
  if (left.length !== right.length) return false;
  const sortedLeft = [...left].sort();
  const sortedRight = [...right].sort();
  return sortedLeft.every((value, index) => value === sortedRight[index]);
}

function gradeQuestion(question: KitQuizQuestion, answers: KitQuizAnswerMap): KitQuizQuestionResult {
  const expected = normalizeAnswers(question.answer);
  const actual = normalizeAnswers(answers[question.id]);
  const points = question.points ?? 1;
  const gradable = question.type !== 'short_answer' && expected.length > 0;

  if (!gradable) {
    return {
      questionId: question.id,
      earned: actual.length > 0 ? points : 0,
      correct: null,
      feedback: question.analysis,
    };
  }

  const correct = arraysEqual(actual, expected);
  return {
    questionId: question.id,
    earned: correct ? points : 0,
    correct,
    feedback: question.analysis,
  };
}

type QuizSceneProps = Omit<KitSceneRendererProps, 'scene'> & {
  scene: KitQuizScene;
};

export function QuizScene({ scene: quizScene, className, style, quiz }: QuizSceneProps) {
  const [answers, setAnswers] = useState<KitQuizAnswerMap>({});
  const [results, setResults] = useState<Record<string, KitQuizQuestionResult>>({});
  const [summary, setSummary] = useState<string | undefined>();
  const [isPending, startTransition] = useTransition();

  const allAnswered = useMemo(() => {
    return quizScene.content.questions.every((question) => {
      const value = answers[question.id];
      if (!value) return false;
      if (Array.isArray(value)) return value.length > 0;
      return value.trim().length > 0;
    });
  }, [answers, quizScene.content.questions]);

  const totalScore = Object.values(results).reduce((sum, item) => sum + item.earned, 0);
  const totalPoints = quizScene.content.questions.reduce((sum, item) => sum + (item.points ?? 1), 0);

  const handleSingleChange = (questionId: string, value: string) => {
    setAnswers((current) => ({ ...current, [questionId]: value }));
  };

  const handleMultipleChange = (questionId: string, value: string) => {
    setAnswers((current) => {
      const currentValues = normalizeAnswers(current[questionId]);
      const nextValues = currentValues.includes(value)
        ? currentValues.filter((item) => item !== value)
        : [...currentValues, value];
      return { ...current, [questionId]: nextValues };
    });
  };

  const handleShortAnswerChange = (questionId: string, value: string) => {
    setAnswers((current) => ({ ...current, [questionId]: value }));
  };

  const handleSubmit = () => {
    startTransition(async () => {
      if (quiz?.onSubmit) {
        const outcome = await quiz.onSubmit({ scene: quizScene, answers });
        setResults(
          Object.fromEntries(outcome.results.map((item) => [item.questionId, item])),
        );
        setSummary(outcome.feedback?.summary ?? outcome.feedback?.heading);
        return;
      }

      const localResults = Object.fromEntries(
        quizScene.content.questions.map((question) => [question.id, gradeQuestion(question, answers)]),
      );
      setResults(localResults);
      setSummary(`Score ${Object.values(localResults).reduce((sum, item) => sum + item.earned, 0)} / ${totalPoints}`);
    });
  };

  const handleRetry = () => {
    setAnswers({});
    setResults({});
    setSummary(undefined);
  };

  const hasResults = Object.keys(results).length > 0;

  return (
    <section className={joinClassNames('scenekit-quiz', className)} style={style}>
      <div className="scenekit-quiz__header">
        <span className="scenekit-quiz__badge">Quiz</span>
        <div>
          <h2>{quizScene.title}</h2>
          <p>{quizScene.content.questions.length} question(s)</p>
        </div>
      </div>

      {summary ? (
        <div className="scenekit-quiz__summary">
          <strong>
            {totalScore} / {totalPoints}
          </strong>
          <span>{summary}</span>
        </div>
      ) : null}

      <div className="scenekit-quiz__questions">
        {quizScene.content.questions.map((question, index) => {
          const result = results[question.id];
          return (
            <article key={question.id} className="scenekit-quiz__card">
              <div className="scenekit-quiz__prompt">
                <span>{index + 1}</span>
                <div>
                  <h3>{question.question}</h3>
                  <p>
                    {question.type} - {question.points ?? 1} point(s)
                  </p>
                </div>
              </div>

              {question.type === 'short_answer' ? (
                <textarea
                  className="scenekit-quiz__textarea"
                  value={typeof answers[question.id] === 'string' ? (answers[question.id] as string) : ''}
                  onChange={(event) => handleShortAnswerChange(question.id, event.target.value)}
                  disabled={hasResults}
                  placeholder="Type your answer..."
                />
              ) : (
                <div className="scenekit-quiz__options">
                  {question.options?.map((option) => {
                    const selected = normalizeAnswers(answers[question.id]).includes(option.value);
                    return (
                      <label key={option.value} className="scenekit-quiz__option">
                        <input
                          type={question.type === 'multiple' ? 'checkbox' : 'radio'}
                          name={question.id}
                          value={option.value}
                          checked={selected}
                          disabled={hasResults}
                          onChange={() =>
                            question.type === 'multiple'
                              ? handleMultipleChange(question.id, option.value)
                              : handleSingleChange(question.id, option.value)
                          }
                        />
                        <span>{option.value}</span>
                        <span>{option.label}</span>
                      </label>
                    );
                  })}
                </div>
              )}

              {result ? (
                <div className="scenekit-quiz__feedback">
                  <strong>
                    {result.correct === null ? 'Reviewed' : result.correct ? 'Correct' : 'Incorrect'}
                  </strong>
                  <span>
                    {result.earned} / {question.points ?? 1}
                  </span>
                  {result.feedback ? <p>{result.feedback}</p> : null}
                </div>
              ) : null}
            </article>
          );
        })}
      </div>

      <div className="scenekit-quiz__actions">
        {hasResults ? (
          <button type="button" onClick={handleRetry}>
            {quiz?.retryLabel ?? 'Try Again'}
          </button>
        ) : (
          <button type="button" onClick={handleSubmit} disabled={!allAnswered || isPending}>
            {isPending ? 'Submitting...' : quiz?.submitLabel ?? 'Submit'}
          </button>
        )}
      </div>
    </section>
  );
}
