export type StreamChatOptions = {
  signal?: AbortSignal;
  onDelta: (text: string) => void;
  onError?: (message: string) => void;
};

import type { ApiChatMessage } from "@/lib/chat/types";

export async function streamCourseChat(
  body: {
    mode: "course" | "project";
    messages: ApiChatMessage[];
    slideContext?: string;
    userQuery?: string;
  },
  options: StreamChatOptions,
): Promise<void> {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal: options.signal,
  });

  if (!res.ok) {
    let msg = res.statusText;
    try {
      const j = (await res.json()) as { error?: string };
      if (j.error) msg = j.error;
    } catch {
      /* ignore */
    }
    options.onError?.(msg);
    return;
  }

  const reader = res.body?.getReader();
  if (!reader) {
    options.onError?.("No response body");
    return;
  }

  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";
      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed.startsWith("data:")) continue;
        const data = trimmed.slice(5).trim();
        if (data === "[DONE]") continue;
        try {
          const json = JSON.parse(data) as {
            choices?: Array<{ delta?: { content?: string } }>;
          };
          const delta = json.choices?.[0]?.delta?.content;
          if (delta) options.onDelta(delta);
        } catch {
          /* skip */
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}
