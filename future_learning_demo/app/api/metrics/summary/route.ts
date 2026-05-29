import { loadChatMetrics, summarizeMetrics } from "@/lib/metrics/chat-metrics";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  const events = loadChatMetrics();
  return Response.json({
    summary: summarizeMetrics(events),
    recent: events.slice(-20),
  });
}
