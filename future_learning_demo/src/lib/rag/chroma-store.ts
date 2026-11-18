import { existsSync } from "node:fs";
import { join } from "node:path";
import { retrieveByKeyword } from "@/lib/rag/keyword-fallback";

const CHROMA_DIR = join(process.cwd(), ".chroma");
const RAG_API =
  process.env.RAG_API_URL?.replace(/\/$/, "") ||
  "http://127.0.0.1:5000/api/v1/rag/course";

// Windows 本机 node fetch 偶发 connect EADDRINUSE（TIME_WAIT 端口冲突），失败后短暂重试即可恢复
const RETRY_DELAYS_MS = [300, 600];
// Flask 首次检索需加载 embedding 模型（约 30-40s），之后命中进程内缓存为毫秒级
const COLD_TIMEOUT_MS = 45_000;
const WARM_TIMEOUT_MS = 8_000;

let ragWarm = false;

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export async function isChromaIndexReady(): Promise<boolean> {
  return existsSync(CHROMA_DIR);
}

async function fetchRagOnce(url: string, timeoutMs: number) {
  const res = await fetch(url, { signal: AbortSignal.timeout(timeoutMs) });
  if (!res.ok) return null;
  const json = (await res.json()) as {
    data?: { chunks?: string[]; count?: number };
  };
  const chunks = json.data?.chunks ?? [];
  return chunks.length > 0 ? chunks : null;
}

async function retrieveFromFlaskApi(
  query: string,
  topK: number,
): Promise<string[] | null> {
  const url = `${RAG_API}?query=${encodeURIComponent(query)}&top_k=${topK}`;
  const timeoutMs = ragWarm ? WARM_TIMEOUT_MS : COLD_TIMEOUT_MS;
  const delays = [...RETRY_DELAYS_MS];
  for (;;) {
    try {
      const chunks = await fetchRagOnce(url, timeoutMs);
      if (chunks) ragWarm = true;
      return chunks;
    } catch {
      const delay = delays.shift();
      if (delay === undefined) return null;
      await sleep(delay);
    }
  }
}

export async function retrieveCourseContext(
  query: string,
  topK = 4,
): Promise<{ chunks: string[]; source: "chroma" | "keyword" }> {
  const trimmed = query.trim();
  if (!trimmed) return { chunks: [], source: "keyword" };

  if (await isChromaIndexReady()) {
    const remote = await retrieveFromFlaskApi(trimmed, topK);
    if (remote?.length) return { chunks: remote, source: "chroma" };
  }

  return { chunks: retrieveByKeyword(trimmed, topK), source: "keyword" };
}
