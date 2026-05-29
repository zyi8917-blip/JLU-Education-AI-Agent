import type { ChatMetricEvent } from "@/lib/metrics/chat-metrics";

export function wrapStreamWithMetrics(
  upstream: ReadableStream<Uint8Array>,
  meta: Omit<ChatMetricEvent, "firstTokenMs" | "totalMs" | "aborted" | "ts">,
  onComplete: (event: ChatMetricEvent) => void,
): ReadableStream<Uint8Array> {
  const started = Date.now();
  let firstTokenMs: number | null = null;
  let aborted = false;

  const reader = upstream.getReader();

  return new ReadableStream<Uint8Array>({
    async pull(controller) {
      try {
        const { done, value } = await reader.read();
        if (done) {
          onComplete({
            ts: new Date().toISOString(),
            ...meta,
            firstTokenMs,
            totalMs: Date.now() - started,
            aborted,
          });
          controller.close();
          return;
        }
        if (value?.length && firstTokenMs === null) {
          firstTokenMs = Date.now() - started;
        }
        controller.enqueue(value);
      } catch (e) {
        aborted = true;
        onComplete({
          ts: new Date().toISOString(),
          ...meta,
          firstTokenMs,
          totalMs: Date.now() - started,
          aborted: true,
          error: e instanceof Error ? e.message : "stream error",
        });
        controller.error(e);
      }
    },
    cancel() {
      aborted = true;
      void reader.cancel();
      onComplete({
        ts: new Date().toISOString(),
        ...meta,
        firstTokenMs,
        totalMs: Date.now() - started,
        aborted: true,
      });
    },
  });
}
