import type { PortraitData } from "@/lib/assessment/transform-report";
import { labelDimension } from "@/lib/assessment/dimension-labels";

function weakestDimensions(portrait: PortraitData, n = 2): string[] {
  const entries = Object.entries(portrait.total_dict ?? {})
    .filter(([, v]) => typeof v === "number" && v > 0)
    .sort(([, a], [, b]) => Number(a) - Number(b));
  return entries.slice(0, n).map(([k]) => labelDimension(k));
}

export function buildPortraitFallbackReply(
  message: string,
  portrait: PortraitData,
  studentName: string,
): string {
  const weak = weakestDimensions(portrait);
  const overall =
    portrait.feedback_dict?.overall ||
    "你在测评中展现了较好的学习自觉性与表达意愿，建议把优势迁移到日常复习节奏中。";
  const grade = portrait.grade_level ? `当前综合等级 ${portrait.grade_level} 档。` : "";

  if (/短板|弱|不足|问题/.test(message)) {
    const focus = weak.length
      ? `从数据上看，${weak.join("、")} 相对更值得优先关注。`
      : "建议从「计划性」和「复盘习惯」两个方向入手。";
    return `${studentName}，${grade}${focus} ${overall} 你可以先选一门最近感到吃力的课，每周固定两次 25 分钟的专项复盘。`;
  }

  if (/计划|本周|安排/.test(message)) {
    return `${studentName}，给你一份可执行的本周学习计划：\n\n1. 周一、周四：各 40 分钟「主动回忆」复习，不看笔记先写出要点。\n2. 周三：针对 ${weak[0] ?? "当前薄弱维度"} 做 1 次小测或讲给同学听。\n3. 周末：用 15 分钟写学习日志——今天最有效的一小时做了什么、下次如何复制。\n\n${overall}`;
  }

  if (/元认知/.test(message)) {
    return `${studentName}，提升元认知可以从三件事做起：学习前先写「本节课我要解决的一个问题」；学习中途暂停 2 分钟自检「我是否真懂」；学后用费曼技巧讲一遍。坚持两周，你会更清楚自己的卡点在哪里。`;
  }

  return `${studentName}，${grade}${overall} 关于「${message}」，建议你先明确一个最小目标（今天能完成的一件小事），再倒推所需时间与资源。需要更具体的方案，可以告诉我你最近正在学哪门课。`;
}
