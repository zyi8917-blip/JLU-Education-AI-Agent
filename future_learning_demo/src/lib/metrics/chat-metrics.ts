import { appendFileSync, existsSync, mkdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

export type ChatMetricEvent = {
  ts: string;
  mode: "course" | "project";
  firstTokenMs: number | null;
  totalMs: number;
  aborted: boolean;
  messageCount: number;
  ragSource?: "chroma" | "keyword" | "none";
  ragChunks?: number;
  error?: string;
};

const METRICS_DIR = join(process.cwd(), ".metrics");
const METRICS_FILE = join(METRICS_DIR, "chat-metrics.jsonl");

export function recordChatMetric(event: ChatMetricEvent): void {
  try {
    if (!existsSync(METRICS_DIR)) mkdirSync(METRICS_DIR, { recursive: true });
    appendFileSync(METRICS_FILE, `${JSON.stringify(event)}\n`, "utf8");
  } catch {
    /* non-fatal */
  }
}

export function loadChatMetrics(): ChatMetricEvent[] {
  if (!existsSync(METRICS_FILE)) return [];
  return readFileSync(METRICS_FILE, "utf8")
    .split("\n")
    .filter(Boolean)
    .map((line) => JSON.parse(line) as ChatMetricEvent);
}

export function summarizeMetrics(events: ChatMetricEvent[]) {
  const ok = events.filter((e) => !e.error);
  const withTtfb = ok.filter((e) => e.firstTokenMs != null);
  const aborted = ok.filter((e) => e.aborted);

  const avg = (nums: number[]) =>
    nums.length ? Math.round(nums.reduce((a, b) => a + b, 0) / nums.length) : null;

  return {
    totalRequests: events.length,
    successRequests: ok.length,
    avgFirstTokenMs: avg(withTtfb.map((e) => e.firstTokenMs as number)),
    p95FirstTokenMs: percentile(
      withTtfb.map((e) => e.firstTokenMs as number),
      0.95,
    ),
    abortRate:
      ok.length > 0
        ? Math.round((aborted.length / ok.length) * 1000) / 10
        : 0,
    ragChromaRate:
      ok.length > 0
        ? Math.round(
            (ok.filter((e) => e.ragSource === "chroma").length / ok.length) *
              1000,
          ) / 10
        : 0,
  };
}

function percentile(values: number[], p: number): number | null {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const idx = Math.min(
    sorted.length - 1,
    Math.max(0, Math.ceil(p * sorted.length) - 1),
  );
  return sorted[idx];
}
