import type { ChatMessage } from "@/components/chat-panel";
import type { ApiChatMessage } from "@/lib/chat/types";
import {
  buildProjectDeliverablePrompt,
  buildProjectSystemPrompt,
  detectCompletedMilestones,
  resolveProjectPhase,
} from "@/lib/chat/project-prompts";
import { buildCourseOutline } from "@/data/course-context";

const courseAgentSystem = `You are a classroom Q&A tutor for an AI fundamentals course.
Use the slide context. Reply in Chinese unless the student uses another language.
Do not invent slide facts; say clearly when the slide does not cover a topic.
Keep answers concise with short structure when helpful.`;

const MAX_UI_ROUNDS = 12;
const MAX_TOTAL_CHARS = 14_000;

function uiToApiRole(role: ChatMessage["role"]): "user" | "assistant" | null {
  if (role === "user") return "user";
  if (role === "agent") return "assistant";
  return null;
}

function estimateChars(messages: ApiChatMessage[]): number {
  return messages.reduce((n, m) => n + m.content.length, 0);
}

function trimConversation(tail: ApiChatMessage[]): ApiChatMessage[] {
  let convo = tail;
  while (convo.length > MAX_UI_ROUNDS * 2) {
    convo = convo.slice(-MAX_UI_ROUNDS * 2);
  }
  return convo;
}

function trimByChars(out: ApiChatMessage[]): ApiChatMessage[] {
  let result = out;
  while (result.length > 1 && estimateChars(result) > MAX_TOTAL_CHARS) {
    if (result.length <= 3) break;
    result = [result[0], ...result.slice(3)];
  }
  return result;
}

export function buildCourseChatMessages(
  uiMessages: ChatMessage[],
  slideContext: string,
  ragChunks: string[] = [],
): ApiChatMessage[] {
  const ragBlock =
    ragChunks.length > 0
      ? `\n\n## Retrieved knowledge (RAG)\n${ragChunks
          .map((c, i) => `### Chunk ${i + 1}\n${c}`)
          .join("\n\n")}`
      : "";

  const systemContent = `${courseAgentSystem}\n\n## Slide context\n${
    slideContext || "(none)"
  }${ragBlock}`;

  const tail: ApiChatMessage[] = [];
  for (const m of uiMessages) {
    const role = uiToApiRole(m.role);
    if (!role || !m.content.trim()) continue;
    tail.push({ role, content: m.content.trim() });
  }

  const system: ApiChatMessage = { role: "system", content: systemContent };
  return trimByChars([system, ...trimConversation(tail)]);
}

export function buildProjectChatMessages(
  uiMessages: ChatMessage[],
  options?: { courseOutline?: string },
): ApiChatMessage[] {
  const userTurns = uiMessages.filter((m) => m.role === "user").length;
  const phase = resolveProjectPhase(userTurns);
  const completed = detectCompletedMilestones(uiMessages);
  const outline = options?.courseOutline ?? buildCourseOutline();

  const system: ApiChatMessage = {
    role: "system",
    content: buildProjectSystemPrompt(phase, completed, outline),
  };

  const tail: ApiChatMessage[] = [];
  for (const m of uiMessages) {
    const role = uiToApiRole(m.role);
    if (!role || !m.content.trim()) continue;
    tail.push({ role, content: m.content.trim() });
  }

  return trimByChars([system, ...trimConversation(tail)]);
}

export function buildProjectSummaryMessages(
  uiMessages: ChatMessage[],
): ApiChatMessage[] {
  return [
    {
      role: "system",
      content:
        "你是课程项目助教。根据对话整理方案摘要，中文 Markdown，不要编造对话中没有的内容。",
    },
    {
      role: "user",
      content: buildProjectDeliverablePrompt(uiMessages),
    },
  ];
}
