"""RAG 检索评测：对 course_qa.json 问题做 Top-4 召回命中率统计"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.rag.rag_service import retrieve, use_lc_rag  # noqa: E402

REPO = BACKEND.parents[1]
QA_PATH = REPO / "future_learning_demo" / "demo-assets" / "course_qa.json"
OUT_PATH = REPO / "future_learning_demo" / "docs" / "rag-eval-results.json"


def _answer_hit(answer: str, chunks: list[str]) -> bool:
    needle = (answer or "").strip()
    if len(needle) < 8:
        needle = needle[: max(len(needle), 1)]
    else:
        needle = needle[:40]
    if not needle:
        return False
    blob = "\n".join(chunks)
    return needle in blob or any(needle in c for c in chunks)


def main() -> int:
    if not QA_PATH.exists():
        print(f"Missing {QA_PATH}")
        return 1

    data = json.loads(QA_PATH.read_text(encoding="utf-8"))
    entries = data.get("entries") or []

    details = []
    hits = 0
    for entry in entries:
        q = (entry.get("question") or "").strip()
        a = (entry.get("answer") or "").strip()
        if not q:
            continue
        chunks = retrieve(q, top_k=4)
        ok = _answer_hit(a, chunks)
        hits += int(ok)
        details.append(
            {
                "id": entry.get("id"),
                "question": q[:80],
                "hit": ok,
                "chunk_count": len(chunks),
            }
        )

    total = len(details)
    rate = round((hits / total) * 100, 1) if total else 0.0
    report = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "backend": "langchain" if use_lc_rag() else "chromadb",
        "totalQuestions": total,
        "hitCount": hits,
        "hitRatePercent": rate,
        "topK": 4,
        "details": details,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in report if k != "details"}, ensure_ascii=False, indent=2))
    print(f"Wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
