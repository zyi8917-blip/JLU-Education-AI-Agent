import type { ChatMessage } from "@/components/chat-panel";

export type ProjectAgentPhase = "coach" | "design" | "review";

export type ProjectMilestone = {
  id: string;
  label: string;
  keywords: string[];
};

export const projectMilestones: ProjectMilestone[] = [
  {
    id: "audience",
    label: "明确课堂助教 Agent 面向的对象和使用场景",
    keywords: ["学生", "教师", "场景", "对象", "用户", "服务", "面向", "课堂"],
  },
  {
    id: "features",
    label: "提出 3 个核心功能",
    keywords: ["功能", "模块", "导学", "答疑", "反馈", "课前", "课中", "课后"],
  },
  {
    id: "workflow",
    label: "说明课堂中的使用流程",
    keywords: ["流程", "步骤", "使用", "互动", "一节课", "上课", "环节"],
  },
  {
    id: "risk",
    label: "补充 1 条风险提醒和优化建议",
    keywords: ["风险", "隐私", "幻觉", "依赖", "边界", "优化", "提醒", "安全"],
  },
];

const agentNames: Record<ProjectAgentPhase, string> = {
  coach: "课程教练 Agent",
  design: "方案设计 Agent",
  review: "评估反馈 Agent",
};

export function getProjectAgentName(phase: ProjectAgentPhase): string {
  return agentNames[phase];
}

export function resolveProjectPhase(userTurnCount: number): ProjectAgentPhase {
  if (userTurnCount <= 1) return "coach";
  if (userTurnCount <= 3) return "design";
  return "review";
}

export function detectCompletedMilestones(messages: ChatMessage[]): string[] {
  const text = messages
    .filter((m) => m.role === "user")
    .map((m) => m.content)
    .join("\n")
    .toLowerCase();

  return projectMilestones
    .filter((m) => m.keywords.some((kw) => text.includes(kw.toLowerCase())))
    .map((m) => m.id);
}

export function buildProjectSystemPrompt(
  phase: ProjectAgentPhase,
  completedIds: string[],
  courseOutline: string,
): string {
  const pending = projectMilestones
    .filter((m) => !completedIds.includes(m.id))
    .map((m) => `- ${m.label}`)
    .join("\n");

  const phaseGuide: Record<ProjectAgentPhase, string> = {
    coach:
      "当前阶段：澄清教学目标与服务对象。追问要具体，例如服务全体学生、教师还是学习困难群体；在什么课堂场景使用。",
    design:
      "当前阶段：引导补全功能模块与使用流程。建议覆盖课前导学、课中答疑、课后反馈至少三个功能，并说明学生和教师如何互动。",
    review:
      "当前阶段：评估方案完整性并补充风险。检查是否缺少幻觉、隐私、过度依赖 AI 等提醒；给出 1～2 条可落地的优化建议。",
  };

  return `你是《人工智能基础》课程 PBL 项目中的「${agentNames[phase]}」。
你的任务是通过对话帮助学生完成「课堂助教 Agent 应用方案」，而不是代替学生写完整答案。

## 课程背景（学生已学内容）
${courseOutline}

## 项目目标
在 3～5 轮对话内完成可讲解的方案：目标人群、核心功能、使用流程、风险提醒。

## 当前阶段
${phaseGuide[phase]}

## 尚未覆盖的里程碑（优先引导）
${pending || "- 四项里程碑已基本覆盖，请帮学生整理成简洁方案摘要"}

## 回复要求
- 使用中文，语气像项目教练，简洁分点
- 每次只推进 1～2 个关键点，留问题让学生补充
- 不要编造学生没提到的细节；可给结构建议
- 若信息不足，用 1 个追问结束`;
}

export function buildProjectDeliverablePrompt(messages: ChatMessage[]): string {
  const transcript = messages
    .filter((m) => m.role !== "system")
    .map((m) => `${m.speaker}: ${m.content}`)
    .join("\n\n");

  return `根据以下 PBL 对话，整理一份「课堂助教 Agent 方案摘要」，用 Markdown 结构输出：

# 方案摘要
## 1. 服务对象与场景
## 2. 三个核心功能
## 3. 课堂使用流程
## 4. 风险提醒与优化建议
## 5. 学习力提升点（1～3 条）

只基于对话中已有信息归纳，缺失项写「待补充」。对话如下：

${transcript}`;
}
