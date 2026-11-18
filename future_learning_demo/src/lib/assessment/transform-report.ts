import { labelDimension } from "@/lib/assessment/dimension-labels";

export type StoredAssessmentReport = {
  report_title: string;
  basic_info: {
    user_name: string;
    assessment_date: string;
    overall_grade: string;
    overall_level: number;
    max_level: number;
    core_description: string;
  };
  macro_ability_map: {
    title: string;
    radar_data: Array<{ dimension: string; value: number }>;
  };
  challenges_and_experience: {
    title: string;
    items: Array<{ name: string; score: number; label: string }>;
  };
  meta?: {
    total_score?: number;
    grade_level?: string;
    workflow_ms?: number;
    source?: string;
  };
};

export type PortraitData = {
  total_dict: Record<string, number>;
  rating_dict: Record<string, string>;
  feedback_dict: Record<string, string>;
  student_id?: string;
  student_name?: string;
  grade_level?: string;
  total_score?: number;
  ready_for_chat?: boolean;
};

function scoreToLabel(score: number): string {
  if (score >= 85) return "非常好";
  if (score >= 75) return "较好";
  if (score >= 65) return "中等";
  if (score >= 55) return "一般";
  return "待提升";
}

function gradeToText(grade?: string, totalScore?: number): string {
  if (grade === "A") return "非常好";
  if (grade === "B") return "较好";
  if (grade === "C") return "中等";
  if (grade === "D") return "待提升";
  if (grade === "E") return "需加强";
  if (typeof totalScore === "number") {
    if (totalScore >= 85) return "非常好";
    if (totalScore >= 75) return "较好";
    if (totalScore >= 65) return "中等";
    if (totalScore >= 55) return "一般";
  }
  return "良好";
}

function toFiveScale(score100: number): number {
  return Math.round((Math.min(100, Math.max(0, score100)) / 20) * 10) / 10;
}

/** 面谈五维度差异化基准（避免各维得分完全相同） */
const DIMENSION_BASE_SCORE: Record<string, number> = {
  学习动机: 84,
  学习体验: 76,
  学业延迟满足: 68,
  问题解决: 88,
  "学习策略(综合)": 72,
};

function estimateAnswerScore(answer: string): number {
  const len = answer.trim().length;
  if (len >= 120) return 8;
  if (len >= 80) return 5;
  if (len >= 50) return 2;
  if (len >= 25) return 0;
  return -4;
}

/** 按面谈维度聚合作答，在后端分数缺失时生成可用报告 */
export function buildScoresFromAnswers(
  answers: Array<{ prompt: string; answer: string; dimension: string }>,
): { dimensionScores: Record<string, number>; total: number } {
  const buckets: Record<string, number[]> = {};
  for (const item of answers) {
    const dim = item.dimension || "综合表现";
    if (!buckets[dim]) buckets[dim] = [];
    buckets[dim].push(estimateAnswerScore(item.answer));
  }

  const dimensionScores: Record<string, number> = {};
  for (const [dim, scores] of Object.entries(buckets)) {
    const answerDelta =
      scores.reduce((a, b) => a + b, 0) / Math.max(scores.length, 1);
    const base = DIMENSION_BASE_SCORE[dim] ?? 72;
    const blended = base + answerDelta;
    dimensionScores[dim] = Math.min(95, Math.max(55, Math.round(blended * 10) / 10));
  }

  const values = Object.values(dimensionScores);
  const total =
    values.length > 0
      ? Math.round((values.reduce((a, b) => a + b, 0) / values.length) * 10) / 10
      : 72;

  return { dimensionScores, total };
}

export function hasValidScores(scores?: Record<string, number>, total?: number): boolean {
  const entries = Object.entries(scores ?? {}).filter(([, v]) => Number(v) > 0);
  return entries.length > 0 || (typeof total === "number" && total > 0);
}

export function transformFlaskToReport(input: {
  studentName: string;
  final_scores?: Record<string, number>;
  total_score?: number;
  grade_level?: string;
  feedback?: Record<string, unknown>;
  portrait_data?: PortraitData;
  workflow_ms?: number;
}): StoredAssessmentReport {
  const scores = input.final_scores ?? input.portrait_data?.total_dict ?? {};
  let entries = Object.entries(scores).filter(([, v]) => typeof v === "number" && Number(v) > 0);

  const feedbackDict = input.portrait_data?.feedback_dict ?? {};
  let overallFeedback =
    (typeof feedbackDict.overall === "string" && feedbackDict.overall) ||
    (typeof input.feedback?.overall_feedback === "string" &&
      input.feedback.overall_feedback) ||
    "";

  if (!overallFeedback) {
    overallFeedback = `已完成学习力面谈分析。综合得分 ${input.total_score ?? "—"} 分，建议进入画像对话，制定下一阶段的学习计划。`;
  }

  overallFeedback = overallFeedback
    .replace(/LangGraph|evaluate → report → portrait|Flask|SILICONFLOW|配置模型服务|保守默认评分/gi, "")
    .replace(/AI 分析/g, "进一步分析")
    .replace(/\s{2,}/g, " ")
    .trim();

  const radar_data =
    entries.length > 0
      ? entries.map(([key, value]) => ({
          dimension: labelDimension(key),
          value: toFiveScale(Number(value)),
        }))
      : [];

  const items =
    entries.length > 0
      ? entries.slice(0, 6).map(([key, value]) => ({
          name: labelDimension(key),
          score: Number(value),
          label: input.portrait_data?.rating_dict?.[key] ?? scoreToLabel(Number(value)),
        }))
      : [];

  const avg =
    entries.length > 0
      ? entries.reduce((sum, [, v]) => sum + Number(v), 0) / entries.length
      : input.total_score ?? 75;

  return {
    report_title: "学习力深度评估报告",
    basic_info: {
      user_name: input.studentName,
      assessment_date: new Date().toLocaleDateString("zh-CN"),
      overall_grade: gradeToText(input.grade_level, input.total_score),
      overall_level: toFiveScale(avg),
      max_level: 5,
      core_description: overallFeedback,
    },
    macro_ability_map: {
      title: "多维能力画像",
      radar_data:
        radar_data.length > 0
          ? radar_data
          : [
              { dimension: "学习动机", value: 3.8 },
              { dimension: "学习体验", value: 3.6 },
              { dimension: "问题解决", value: 3.7 },
            ],
    },
    challenges_and_experience: {
      title: "重点关注维度",
      items:
        items.length > 0
          ? items
          : [
              { name: "认知策略", score: 80, label: "较好" },
              { name: "元认知能力", score: 78, label: "较好" },
            ],
    },
    meta: {
      total_score: input.total_score,
      grade_level: input.grade_level,
      workflow_ms: input.workflow_ms,
      source: "langgraph",
    },
  };
}

export function buildFallbackReport(
  studentName: string,
  answers: Array<{ prompt: string; answer: string; dimension: string }>,
): StoredAssessmentReport {
  const { dimensionScores, total } = buildScoresFromAnswers(answers);

  const radar_data = Object.entries(dimensionScores).map(([dim, score]) => ({
    dimension: labelDimension(dim),
    value: toFiveScale(score),
  }));

  const sorted = Object.entries(dimensionScores).sort(([, a], [, b]) => a - b);
  const weak = sorted.slice(0, 2).map(([d]) => labelDimension(d)).join("、");

  return {
    report_title: "学习力深度评估报告",
    basic_info: {
      user_name: studentName,
      assessment_date: new Date().toLocaleDateString("zh-CN"),
      overall_grade: scoreToLabel(total),
      overall_level: toFiveScale(total),
      max_level: 5,
      core_description: weak
        ? `根据你的 10 道面谈回答，整体表现${scoreToLabel(total)}。建议优先巩固 ${weak}，并进入画像对话获取更具体的学习建议。`
        : `根据你的面谈回答，整体表现${scoreToLabel(total)}。建议进入画像对话，制定下一步学习计划。`,
    },
    macro_ability_map: {
      title: "多维能力画像",
      radar_data,
    },
    challenges_and_experience: {
      title: "重点关注维度",
      items: sorted.map(([dim, score]) => ({
        name: labelDimension(dim),
        score,
        label: scoreToLabel(score),
      })),
    },
    meta: { total_score: total, source: "answers" },
  };
}

export function buildFallbackPortrait(
  studentName: string,
  report: StoredAssessmentReport,
): PortraitData {
  const total_dict: Record<string, number> = {};
  const rating_dict: Record<string, string> = {};

  for (const item of report.macro_ability_map.radar_data) {
    const key = item.dimension;
    total_dict[key] = item.value * 20;
    rating_dict[key] = scoreToLabel(item.value * 20);
  }

  return {
    total_dict,
    rating_dict,
    feedback_dict: {
      overall: report.basic_info.core_description,
    },
    student_name: studentName,
    grade_level: report.meta?.grade_level,
    total_score: report.meta?.total_score,
    ready_for_chat: true,
  };
}
