/**
 * Agent 链路压测：npm run benchmark:chat
 * 需先 npm run dev 且配置 .env.local 中的 OPENAI_API_KEY（可选，无 Key 时仅测 RAG/裁剪）
 */
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const baseUrl = process.env.BENCHMARK_BASE_URL || "http://127.0.0.1:3000";
const outDir = join(root, "docs");
const outFile = join(outDir, "benchmark-results.json");

function percentile(values, p) {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const idx = Math.min(sorted.length - 1, Math.max(0, Math.ceil(p * values.length) - 1));
  return sorted[idx];
}

async function probeHealth() {
  try {
    const res = await fetch(`${baseUrl}/api/metrics/summary`, { signal: AbortSignal.timeout(3000) });
    return res.ok;
  } catch {
    return false;
  }
}

async function streamOnce(messages, userQuery, signal) {
  const started = Date.now();
  let firstTokenMs = null;
  let bytes = 0;
  let aborted = false;

  const res = await fetch(`${baseUrl}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mode: "course", messages, userQuery }),
    signal,
  });

  if (!res.ok) {
    const err = await res.text();
    return { ok: false, status: res.status, error: err.slice(0, 300), firstTokenMs, totalMs: Date.now() - started, aborted };
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      bytes += value?.length ?? 0;
      if (firstTokenMs === null && bytes > 0) firstTokenMs = Date.now() - started;
    }
  } catch (e) {
    if (e.name === "AbortError") aborted = true;
    else throw e;
  }

  return {
    ok: true,
    firstTokenMs,
    totalMs: Date.now() - started,
    aborted,
    ragSource: res.headers.get("x-rag-source"),
    bytes,
  };
}

function buildMessages(round) {
  const history = [];
  for (let i = 0; i < round; i++) {
    history.push({ role: "user", content: `第${i + 1}轮：OpenClaw 是什么？` });
    history.push({ role: "assistant", content: `第${i + 1}轮简要回答。` });
  }
  history.push({ role: "user", content: "请结合课件说明五种智能融合的意义。" });
  return [
    { role: "system", content: "你是课堂助教。\n\n## Slide context\nPage 1" },
    ...history,
  ];
}

async function main() {
  const result = {
    generatedAt: new Date().toISOString(),
    baseUrl,
    serverOnline: await probeHealth(),
    rounds20: { attempted: false },
    abort: { attempted: false },
    ragKeyword: { attempted: false },
    samples: [],
  };

  const qa = JSON.parse(
    readFileSync(join(root, "demo-assets/course_qa.json"), "utf8"),
  );
  const keywordHits = (qa.entries ?? []).filter((e) =>
    `${e.question}${e.answer}`.toLowerCase().includes("openclaw"),
  ).length;
  result.ragKeyword = {
    attempted: true,
    hitCount: keywordHits,
    source: "keyword",
  };

  if (!result.serverOnline) {
    result.note =
      "Dev server not running. Start with: npm run dev. LLM/stream metrics require OPENAI_API_KEY.";
    mkdirSync(outDir, { recursive: true });
    writeFileSync(outFile, JSON.stringify(result, null, 2));
    console.log(JSON.stringify(result, null, 2));
    console.log(`\nWrote ${outFile}`);
    process.exit(0);
  }

  const ttfbList = [];
  let roundsOk = 0;
  for (let r = 1; r <= 20; r++) {
    const messages = buildMessages(r);
    const probe = await streamOnce(messages, "五种智能融合后会带来什么？", undefined);
    result.samples.push({ round: r, ...probe });
    if (probe.ok) {
      roundsOk += 1;
      if (probe.firstTokenMs != null) ttfbList.push(probe.firstTokenMs);
    }
    if (probe.status === 503) break;
  }
  result.rounds20 = {
    attempted: true,
    successRounds: roundsOk,
    successRate: Math.round((roundsOk / 20) * 1000) / 10,
    avgFirstTokenMs: ttfbList.length
      ? Math.round(ttfbList.reduce((a, b) => a + b, 0) / ttfbList.length)
      : null,
    p95FirstTokenMs: percentile(ttfbList, 0.95),
  };

  const ac = new AbortController();
  setTimeout(() => ac.abort(), 400);
  const abortProbe = await streamOnce(
    buildMessages(2),
    "OpenClaw 为什么会引发关注？",
    ac.signal,
  );
  result.abort = {
    attempted: true,
    aborted: abortProbe.aborted,
    abortSuccess: abortProbe.aborted === true,
  };

  try {
    const summaryRes = await fetch(`${baseUrl}/api/metrics/summary`);
    result.metricsSummary = await summaryRes.json();
  } catch {
    /* ignore */
  }

  mkdirSync(outDir, { recursive: true });
  writeFileSync(outFile, JSON.stringify(result, null, 2));
  console.log(JSON.stringify(result, null, 2));
  console.log(`\nWrote ${outFile}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
