"""python scripts/build_course_rag.py"""
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.rag.course_rag import build_index  # noqa: E402

if __name__ == "__main__":
    n = build_index()
    print(f"Indexed {n} chunks into future_learning_demo/.chroma")
