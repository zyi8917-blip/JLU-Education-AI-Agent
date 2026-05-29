export type ChatRole = "system" | "user" | "assistant";

export type ApiChatMessage = {
  role: ChatRole;
  content: string;
};

export type ChatRequestBody = {
  mode: "course" | "project";
  messages: ApiChatMessage[];
  slideContext?: string;
  /** 当前用户问题，用于 RAG 检索 */
  userQuery?: string;
};

export function isChatRequestBody(value: unknown): value is ChatRequestBody {
  if (!value || typeof value !== "object") return false;
  const v = value as Record<string, unknown>;
  if (v.mode !== "course" && v.mode !== "project") return false;
  if (!Array.isArray(v.messages)) return false;
  for (const m of v.messages) {
    if (!m || typeof m !== "object") return false;
    const msg = m as Record<string, unknown>;
    if (msg.role !== "system" && msg.role !== "user" && msg.role !== "assistant")
      return false;
    if (typeof msg.content !== "string") return false;
  }
  if (v.slideContext !== undefined && typeof v.slideContext !== "string")
    return false;
  if (v.userQuery !== undefined && typeof v.userQuery !== "string") return false;
  return true;
}
