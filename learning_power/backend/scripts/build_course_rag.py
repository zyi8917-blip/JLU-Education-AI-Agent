"""python scripts/build_course_rag.py — 默认 LangChain 构建索引"""
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.rag.rag_service import build_index, use_lc_rag  # noqa: E402

if __name__ == "__main__":
    n = build_index()
    mode = "LangChain" if use_lc_rag() else "ChromaDB"
    print(f"Indexed {n} chunks ({mode}) into future_learning_demo/.chroma")
