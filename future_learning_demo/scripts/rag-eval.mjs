/**
 * RAG 检索评测（调用 Python rag_eval.py）
 * npm run benchmark:rag
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
  "rag_eval.py",
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

process.exit(result.status ?? 1);
