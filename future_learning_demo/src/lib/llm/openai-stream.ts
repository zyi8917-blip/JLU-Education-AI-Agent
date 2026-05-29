import type { ApiChatMessage } from "@/lib/chat/types";

export type StreamOpenAIOptions = {
  baseUrl: string;
  apiKey: string;
  model: string;
  messages: ApiChatMessage[];
  signal: AbortSignal;
};

/**
 * OpenAI-compatible streaming chat.completions; returns upstream bytes (SSE).
 */
export async function streamOpenAIChatCompletion(
  opts: StreamOpenAIOptions,
): Promise<ReadableStream<Uint8Array>> {
  const url = `${opts.baseUrl}/chat/completions`;
  const upstream = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${opts.apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: opts.model,
      messages: opts.messages,
      stream: true,
    }),
    signal: opts.signal,
  });

  if (!upstream.ok) {
    const text = await upstream.text().catch(() => "");
    throw new Error(
      `OpenAI error ${upstream.status}: ${text.slice(0, 800)}`,
    );
  }

  if (!upstream.body) {
    throw new Error("OpenAI response has no body");
  }

  return upstream.body;
}
