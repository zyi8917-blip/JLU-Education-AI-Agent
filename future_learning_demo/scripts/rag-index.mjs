/**
 * 构建 Chroma 索引（Python 嵌入式 PersistentClient）
 * npm run rag:index
 */
import { spawnSync } from "node:child_process";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const script = join(
  root,
  "..",
  "learning_power",
  "backend",
  "scripts",
  "build_course_rag.py",
);

const py = process.env.PYTHON || "python";
const result = spawnSync(py, [script], {
  cwd: join(root, "..", "learning_power", "backend"),
  stdio: "inherit",
  encoding: "utf8",
  env: {
    ...process.env,
    HF_ENDPOINT: process.env.HF_ENDPOINT || "https://hf-mirror.com",
  },
});

if (result.status !== 0) {
  console.error("RAG index build failed. Install: pip install chromadb");
  process.exit(result.status ?? 1);
}

console.log("Chroma index ready at future_learning_demo/.chroma");
