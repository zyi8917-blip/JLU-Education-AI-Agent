import { buildCourseSlide, type CourseSlideSpec } from "@/data/slide-builder";

const courseSlideSpecs: CourseSlideSpec[] = [
  {
    id: "course-slide-1",
    title: "从一只「龙虾」说起",
    subtitle: "OpenClaw 现象：软件形态正在从工具走向智能体",
    bullets: [
      "黄仁勋称 OpenClaw 是「这个时代最重要的软件发布」——重点不在星标数，而在范式变化",
      "2026 年 3 月 GitHub 星标超越 React，说明开发者对「可执行任务系统」的关注超过传统框架",
      "腾讯门口「养虾」装机潮：从 2 岁到 60 岁，说明 Agent 正在进入大众使用场景",
    ],
    cards: [
      {
        title: "模型层",
        body: "理解、推理、生成——LLM 提供认知能力",
        color: "#2563eb",
      },
      {
        title: "Agent 层",
        body: "目标拆解、工具调用、任务执行——把能力变成行动",
        color: "#0f766e",
      },
    ],
    footer: "课程主线：AI 不只会「回答问题」，还要能「参与工作流」",
    accent: "#2563eb",
  },
  {
    id: "course-slide-2",
    title: "拥抱人工智能时代",
    subtitle: "从「工业革命」到「认知革命」",
    bullets: [
      "五种智能协同：大模型 · 智能体 · 具身智能 · 物理智能 · 生物智能",
      "迭代速度前所未有，能力上限仍在抬升，系统具备递归式自我改进潜力",
      "学习者要建立整体视角：不是单点技术，而是多种能力共同推动的新阶段",
    ],
    cards: [
      { title: "大模型", body: "语言理解与推理", color: "#2563eb" },
      { title: "智能体", body: "规划 + 工具 + 执行", color: "#0f766e" },
      { title: "具身/物理", body: "进入真实环境", color: "#f59e0b" },
      { title: "生物智能", body: "自然人机协同", color: "#7c3aed" },
    ],
    accent: "#0f766e",
  },
  {
    id: "course-slide-3",
    title: "什么是大语言模型（LLM）",
    subtitle: "Transformer · 预训练 · 指令微调 · 对齐",
    bullets: [
      "底层架构：Decoder-only Transformer，通过 Self-Attention 建模长距离依赖",
      "训练阶段：海量文本预训练 → SFT 指令微调 → RLHF/DPO 人类偏好对齐",
      "推理方式：自回归逐 token 生成；KV Cache 加速 decode 阶段",
    ],
    table: {
      headers: ["阶段", "目标", "典型产出"],
      rows: [
        ["预训练", "学语言规律与世界知识", "Base 模型"],
        ["SFT", "学会听指令、对话格式", "Chat/Instruct 模型"],
        ["对齐", "更有帮助、更安全", "产品级模型"],
      ],
    },
    accent: "#2563eb",
  },
  {
    id: "course-slide-4",
    title: "什么是 AI Agent",
    subtitle: "感知 · 规划 · 记忆 · 行动",
    bullets: [
      "ReAct：思考—行动—观察循环，适合多步工具调用",
      "Plan-and-Execute：先拆子任务再逐步执行，适合流程明确的业务",
      "Tool Calling：模型输出结构化工具调用，框架执行后回灌 Observation",
    ],
    cards: [
      {
        title: "编排型",
        body: "LangGraph 固定节点：测评 → 报告 → 画像",
        color: "#2563eb",
      },
      {
        title: "知识增强型",
        body: "RAG + 对话：课堂伴学、课件问答",
        color: "#0f766e",
      },
    ],
    footer: "本课程平台：Next.js 网关 + Chroma RAG + LangGraph 工作流",
    accent: "#7c3aed",
  },
  {
    id: "course-slide-5",
    title: "RAG：检索增强生成",
    subtitle: "让模型「有依据地回答」，而不是纯靠参数记忆",
    bullets: [
      "离线：文档切片 → Embedding 向量化 → 写入 Chroma 等向量库",
      "在线：用户提问 → Top-K 召回 → 拼入 Prompt → LLM 生成",
      "工程要点：混合检索（BM25+向量）、Rerank、metadata 过滤、评测集",
    ],
    table: {
      headers: ["环节", "本项目实现", "效果"],
      rows: [
        ["索引", "课件 JSON + QA + Markdown", "8 条 chunk"],
        ["检索", "Flask /api/v1/rag/course", "Top-4 召回"],
        ["生成", "Next.js /api/chat SSE", "流式输出"],
      ],
    },
    accent: "#0f766e",
  },
  {
    id: "course-slide-6",
    title: "Prompt / Context / Harness 工程",
    subtitle: "三层工程决定 Agent 能否稳定落地",
    bullets: [
      "Prompt Engineering：角色、格式、禁止项——模型「怎么说」",
      "Context Engineering：RAG + 历史 + slide 摘要——模型「看到什么」",
      "Harness Engineering：编排、流式、降级、metrics——系统「怎么跑」",
    ],
    cards: [
      {
        title: "上下文裁剪",
        body: "最近 12 轮 + 约 14K 字符，防 token 爆炸",
        color: "#2563eb",
      },
      {
        title: "可观测",
        body: "benchmark:chat · 首 token 延迟 · RAG 命中率",
        color: "#f59e0b",
      },
    ],
    accent: "#2563eb",
  },
  {
    id: "course-slide-7",
    title: "学习力测评与画像 Agent",
    subtitle: "LangGraph 三节点：评分 → 报告 → 画像上下文",
    bullets: [
      "evaluate_answers：批量 LLM 评分，产出维度分数与评语",
      "generate_report：整理可读报告字段，供结果页展示",
      "prepare_portrait：生成 portrait_data，画像对话 Agent 直接消费",
    ],
    footer: "闭环：测评 → 报告 → 画像答疑 → 课件伴学 → PBL 项目实践",
    accent: "#7c3aed",
  },
  {
    id: "course-slide-8",
    title: "PBL：设计你的课堂助教 Agent",
    subtitle: "做中学——从理解到方案设计",
    bullets: [
      "明确服务对象：全体学生 / 教师 / 学习困难群体",
      "设计 3 个核心功能：课前导学、课中答疑、课后反馈",
      "梳理使用流程 + 风险提醒（幻觉、隐私、过度依赖）",
    ],
    cards: [
      { title: "课程教练", body: "澄清目标与场景", color: "#2563eb" },
      { title: "方案设计", body: "功能模块与流程", color: "#0f766e" },
      { title: "评估反馈", body: "效果与学习力提升", color: "#f59e0b" },
    ],
    accent: "#0f766e",
  },
];

export const slideDeck = courseSlideSpecs.map((spec) => ({
  id: spec.id,
  title: spec.title,
  data: buildCourseSlide(spec),
  spec,
}));

export type SlideDeckItem = (typeof slideDeck)[number];
