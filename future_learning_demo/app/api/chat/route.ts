import { NextRequest } from "next/server";
import { isChatRequestBody } from "@/lib/chat/types";
import { getLlmEnv } from "@/lib/llm/env";
import { streamOpenAIChatCompletion } from "@/lib/llm/openai-stream";
import { wrapStreamWithMetrics } from "@/lib/llm/stream-with-metrics";
import { recordChatMetric } from "@/lib/metrics/chat-metrics";
import { retrieveCourseContext } from "@/lib/rag/chroma-store";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return Response.json({ error: "Invalid JSON" }, { status: 400 });
  }

  if (!isChatRequestBody(body)) {
    return Response.json({ error: "Invalid request body" }, { status: 400 });
  }

  const env = getLlmEnv();
  if (!env) {
    return Response.json(
      {
        error:
          "LLM not configured. Copy .env.example to .env.local and set OPENAI_API_KEY.",
      },
      { status: 503 },
    );
  }

  let ragSource: "chroma" | "keyword" | "none" = "none";
  let ragChunks = 0;
  if (body.mode === "course" && body.userQuery?.trim()) {
    const rag = await retrieveCourseContext(body.userQuery.trim(), 4);
    ragSource = rag.chunks.length ? rag.source : "none";
    ragChunks = rag.chunks.length;
    if (rag.chunks.length > 0) {
      const ragText = rag.chunks.join("\n\n");
      const systemIdx = body.messages.findIndex((m) => m.role === "system");
      if (systemIdx >= 0) {
        body.messages[systemIdx] = {
          ...body.messages[systemIdx],
          content: `${body.messages[systemIdx].content}\n\n## Retrieved knowledge (RAG)\n${ragText}`,
        };
      }
    }
  }

  try {
    const upstream = await streamOpenAIChatCompletion({
      baseUrl: env.baseUrl,
      apiKey: env.apiKey,
      model: env.model,
      messages: body.messages,
      signal: req.signal,
    });

    const stream = wrapStreamWithMetrics(
      upstream,
      {
        mode: body.mode,
        messageCount: body.messages.length,
        ragSource,
        ragChunks,
      },
      (event) => recordChatMetric(event),
    );

    return new Response(stream, {
      headers: {
        "Content-Type": "text/event-stream; charset=utf-8",
        "Cache-Control": "no-cache, no-transform",
        Connection: "keep-alive",
        "X-RAG-Source": ragSource,
      },
    });
  } catch (e) {
    const message = e instanceof Error ? e.message : "Upstream error";
    recordChatMetric({
      ts: new Date().toISOString(),
      mode: body.mode,
      firstTokenMs: null,
      totalMs: 0,
      aborted: false,
      messageCount: body.messages.length,
      ragSource,
      ragChunks,
      error: message,
    });
    return Response.json({ error: message }, { status: 502 });
  }
}
