import courseQa from "../../../demo-assets/course_qa.json";
import { readFileSync } from "node:fs";
import { join } from "node:path";

type QaEntry = {
  question: string;
  answer: string;
  keywords: string[];
};

function tokenize(text: string): string[] {
  return text
    .toLowerCase()
    .split(/[\s，。！？、；：""''（）\-\.]+/)
    .filter((t) => t.length > 1);
}

function scoreQuery(query: string, text: string, keywords: string[] = []): number {
  const q = new Set(tokenize(query));
  if (q.size === 0) return 0;
  let hit = 0;
  for (const t of tokenize(text)) {
    if (q.has(t)) hit += 1;
  }
  for (const kw of keywords) {
    if (query.toLowerCase().includes(kw.toLowerCase())) hit += 2;
  }
  return hit;
}

function loadMarkdownChunks(): Array<{ id: string; text: string }> {
  try {
    const mdPath = join(process.cwd(), "demo-assets", "class_agent_QA.md");
    const raw = readFileSync(mdPath, "utf8");
    const parts = raw.split(/^###\s+/m).filter(Boolean);
    return parts.map((part, i) => ({
      id: `md-${i}`,
      text: part.trim().slice(0, 1200),
    }));
  } catch {
    return [];
  }
}

export function retrieveByKeyword(query: string, topK = 4): string[] {
  const pool: Array<{ text: string; score: number }> = [];

  for (const entry of courseQa.entries as QaEntry[]) {
    const text = `Q: ${entry.question}\nA: ${entry.answer}`;
    pool.push({ text, score: scoreQuery(query, text, entry.keywords) });
  }

  for (const chunk of loadMarkdownChunks()) {
    pool.push({ text: chunk.text, score: scoreQuery(query, chunk.text) });
  }

  return pool
    .filter((p) => p.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, topK)
    .map((p) => p.text);
}
