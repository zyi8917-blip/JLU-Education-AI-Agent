import type { ChatMessage } from "@/components/chat-panel";
import type { ApiChatMessage } from "@/lib/chat/types";

const courseAgentSystem = `You are a classroom Q&A tutor for an AI fundamentals course.
Use the slide context. Reply in Chinese unless the student uses another language.
Do not invent slide facts; say clearly when the slide does not cover a topic.
Keep answers concise with short structure when helpful.`;

const projectCoachSystem = `You are a project coach (reserved for project mode).`;

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

  let convo = tail;
  while (convo.length > MAX_UI_ROUNDS * 2) {
    convo = convo.slice(-MAX_UI_ROUNDS * 2);
  }

  const system: ApiChatMessage = { role: "system", content: systemContent };
  let out: ApiChatMessage[] = [system, ...convo];

  while (out.length > 1 && estimateChars(out) > MAX_TOTAL_CHARS) {
    if (out.length <= 3) break;
    out = [out[0], ...out.slice(3)];
  }

  return out;
}

export function buildProjectChatMessages(uiMessages: ChatMessage[]): ApiChatMessage[] {
  const system: ApiChatMessage = {
    role: "system",
    content: projectCoachSystem,
  };
  const tail: ApiChatMessage[] = [];
  for (const m of uiMessages) {
    const role = uiToApiRole(m.role);
    if (!role || !m.content.trim()) continue;
    tail.push({ role, content: m.content.trim() });
  }
  let convo = tail;
  while (convo.length > MAX_UI_ROUNDS * 2) {
    convo = convo.slice(-MAX_UI_ROUNDS * 2);
  }
  return [system, ...convo];
}
