import { NextRequest, NextResponse } from "next/server";
import { flaskFetch } from "@/lib/flask/client";
import {
  buildFallbackPortrait,
  buildFallbackReport,
  hasValidScores,
  transformFlaskToReport,
  type PortraitData,
} from "@/lib/assessment/transform-report";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type CompleteBody = {
  student_id?: string;
  student_name?: string;
  evaluation_type?: string;
  answers: Array<{
    question_id: string;
    prompt: string;
    answer: string;
    dimension?: string;
  }>;
};

export async function POST(req: NextRequest) {
  let body: CompleteBody;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  if (!Array.isArray(body.answers) || body.answers.length === 0) {
    return NextResponse.json({ error: "answers required" }, { status: 400 });
  }

  const studentName = body.student_name?.trim() || "小明";
  const studentId = body.student_id?.trim() || "demo-001";
  const normalizedAnswers = body.answers.map((a) => ({
    prompt: a.prompt,
    answer: a.answer,
    dimension: a.dimension ?? "综合表现",
  }));
  const pairs = body.answers.map((a) => ({
    question_id: a.question_id,
    question_content: a.prompt,
    answer_content: a.answer,
  }));

  const flask = await flaskFetch<{
    final_scores: Record<string, number>;
    total_score: number;
    grade_level: string;
    feedback: Record<string, unknown>;
    portrait_data: PortraitData;
    workflow_ms: number;
    error?: string;
  }>("/api/v1/assessments/quick-complete", {
    method: "POST",
    body: JSON.stringify({
      student_id: studentId,
      student_name: studentName,
      evaluation_type: body.evaluation_type || "learning_motivation",
      question_answer_pairs: pairs,
    }),
  });

  if (flask.ok && flask.data) {
    const scoresOk = hasValidScores(flask.data.final_scores, flask.data.total_score);
    const portraitOk = hasValidScores(flask.data.portrait_data?.total_dict, flask.data.portrait_data?.total_score);

    if (scoresOk || portraitOk) {
      const answerReport = buildFallbackReport(studentName, normalizedAnswers);
      const report = transformFlaskToReport({
        studentName,
        final_scores: scoresOk
          ? flask.data.final_scores
          : flask.data.portrait_data?.total_dict,
        total_score: flask.data.total_score || flask.data.portrait_data?.total_score,
        grade_level: flask.data.grade_level,
        feedback: flask.data.feedback,
        portrait_data: flask.data.portrait_data,
        workflow_ms: flask.data.workflow_ms,
      });

      // 面谈题维度与后端 rubric 不一致时，用作答聚合维度展示更贴近用户感知
      report.macro_ability_map = answerReport.macro_ability_map;
      report.challenges_and_experience = answerReport.challenges_and_experience;
      if (!report.basic_info.core_description || report.basic_info.overall_level <= 0) {
        report.basic_info.core_description = answerReport.basic_info.core_description;
        report.basic_info.overall_level = answerReport.basic_info.overall_level;
        report.basic_info.overall_grade = answerReport.basic_info.overall_grade;
      }

      let portrait_data = portraitOk
        ? flask.data.portrait_data
        : buildFallbackPortrait(studentName, report);
      if (portraitOk) {
        portrait_data = {
          ...portrait_data,
          ...buildFallbackPortrait(studentName, report),
          feedback_dict: {
            ...buildFallbackPortrait(studentName, report).feedback_dict,
            ...portrait_data.feedback_dict,
          },
        };
      }

      return NextResponse.json({
        source: "ai",
        report,
        portrait_data,
        workflow_ms: flask.data.workflow_ms,
      });
    }
  }

  const report = buildFallbackReport(studentName, normalizedAnswers);
  const portrait_data = buildFallbackPortrait(studentName, report);

  return NextResponse.json({
    source: "answers",
    report,
    portrait_data,
  });
}
