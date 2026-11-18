import type { PortraitData, StoredAssessmentReport } from "@/lib/assessment/transform-report";

export type AssessmentAnswerPayload = {
  question_id: string;
  prompt: string;
  answer: string;
  dimension: string;
};

export type AssessmentCompleteResult = {
  source: string;
  report: StoredAssessmentReport;
  portrait_data: PortraitData;
};

export async function submitAssessmentAnswers(
  answers: AssessmentAnswerPayload[],
  options?: { student_name?: string; student_id?: string },
): Promise<AssessmentCompleteResult> {
  const res = await fetch("/api/assessments/complete", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      student_name: options?.student_name ?? "小明",
      student_id: options?.student_id ?? "demo-001",
      evaluation_type: "learning_motivation",
      answers,
    }),
  });

  const payload = (await res.json()) as {
    source?: string;
    report?: StoredAssessmentReport;
    portrait_data?: PortraitData;
    error?: string;
  };

  if (!res.ok || !payload.report || !payload.portrait_data) {
    throw new Error(payload.error || "生成报告失败，请稍后重试");
  }

  return {
    source: payload.source ?? "unknown",
    report: payload.report,
    portrait_data: payload.portrait_data,
  };
}
