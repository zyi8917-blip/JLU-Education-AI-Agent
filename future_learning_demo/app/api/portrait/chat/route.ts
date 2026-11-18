import { NextRequest, NextResponse } from "next/server";
import { flaskFetch } from "@/lib/flask/client";
import { buildPortraitFallbackReply } from "@/lib/assessment/portrait-fallback";
import type { PortraitData } from "@/lib/assessment/transform-report";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type PortraitChatBody = {
  student_id?: string;
  student_name?: string;
  message: string;
  portrait_data: PortraitData;
  chat_history?: Array<{ role: "user" | "assistant"; content: string }>;
};

export async function POST(req: NextRequest) {
  let body: PortraitChatBody;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  if (!body.message?.trim()) {
    return NextResponse.json({ error: "message required" }, { status: 400 });
  }

  const studentName = body.student_name?.trim() || "同学";
  const portrait = body.portrait_data ?? {
    total_dict: {},
    rating_dict: {},
    feedback_dict: {},
  };

  const flask = await flaskFetch<{ reply: string; timestamp: string }>(
    "/api/v1/chat/portrait",
    {
      method: "POST",
      body: JSON.stringify({
        student_id: body.student_id || "demo-001",
        student_name: studentName,
        message: body.message.trim(),
        portrait_data: portrait,
        chat_history: body.chat_history ?? [],
      }),
    },
  );

  if (flask.ok && flask.data?.reply) {
    return NextResponse.json({
      reply: flask.data.reply,
      source: "ai",
      timestamp: flask.data.timestamp,
    });
  }

  return NextResponse.json({
    reply: buildPortraitFallbackReply(body.message.trim(), portrait, studentName),
    source: "local",
  });
}
