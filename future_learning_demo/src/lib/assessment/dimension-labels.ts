/** 测评维度与画像字段的中文展示名 */
export const DIMENSION_LABELS: Record<string, string> = {
  metacognition: "元认知能力",
  cognitive_strategy: "认知策略",
  critical_thinking: "批判性思维",
  learning_motivation: "学习动机",
  social_emotional: "社会情感能力",
  responsible_decision: "负责任决策",
  social_awareness: "社会知觉",
  self_management: "自我管理",
  relationship_skills: "同伴关系",
  fluency: "流畅性",
  flexibility: "灵活性",
  originality: "独创性",
  elaboration: "精细性",
  autonomy: "自主性",
  competence: "胜任感",
  relatedness: "关系需求",
  monitoring: "自我监测",
  integration: "自我整合",
  differentiation: "他人分化",
  decentration: "他人去中心化",
  open_mindedness: "思维开放性",
  analytical_logical_skills: "分析性与逻辑性",
  systematic_planning: "系统性与规划性",
  intellectual_curiosity: "求知欲与探索精神",
  cognitive_maturity: "认知成熟度",
  overall: "综合表现",
  "学习动机": "学习动机",
  "学习体验": "学习体验",
  "学业延迟满足": "学业延迟满足",
  "问题解决": "问题解决",
  "学习策略(综合)": "学习策略",
};

export function labelDimension(key: string): string {
  return DIMENSION_LABELS[key] ?? key;
}

export function formatRatingSummary(
  ratingDict: Record<string, string> | undefined,
  limit = 4,
): string {
  const entries = Object.entries(ratingDict ?? {}).slice(0, limit);
  if (!entries.length) return "";
  return entries.map(([k, v]) => `${labelDimension(k)} · ${v}`).join("  ");
}
