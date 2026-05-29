import { existsSync } from "node:fs";
import { join } from "node:path";
import { retrieveByKeyword } from "@/lib/rag/keyword-fallback";

const CHROMA_DIR = join(process.cwd(), ".chroma");
const RAG_API =
  process.env.RAG_API_URL?.replace(/\/$/, "") ||
  "http://127.0.0.1:5000/api/v1/rag/course";

export async function isChromaIndexReady(): Promise<boolean> {
  return existsSync(CHROMA_DIR);
}

async function retrieveFromFlaskApi(
  query: string,
  topK: number,
): Promise<string[] | null> {
  try {
    const url = `${RAG_API}?query=${encodeURIComponent(query)}&top_k=${topK}`;
    const res = await fetch(url, { signal: AbortSignal.timeout(4000) });
    if (!res.ok) return null;
    const json = (await res.json()) as {
      data?: { chunks?: string[]; count?: number };
    };
    const chunks = json.data?.chunks ?? [];
    return chunks.length > 0 ? chunks : null;
  } catch {
    return null;
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
