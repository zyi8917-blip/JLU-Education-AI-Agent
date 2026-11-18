"""
Chroma 持久化向量库：课件 QA + Markdown + Slide 文本
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

import chromadb

COLLECTION_NAME = "course_agent_kb"
_REPO_ROOT = Path(__file__).resolve().parents[4]
_DEMO_ASSETS = _REPO_ROOT / "future_learning_demo" / "demo-assets"
_CHROMA_PATH = _REPO_ROOT / "future_learning_demo" / ".chroma"


def _extract_slide_text(slide: dict) -> str:
    elements = slide.get("page", {}).get("elements") or slide.get("elements") or []
    texts = []
    for el in elements:
        if el.get("type") == "text" and isinstance(el.get("content"), str):
            texts.append(re.sub(r"<[^>]+>", " ", el["content"]))
    return re.sub(r"\s+", " ", " ".join(texts)).strip()


def load_chunks() -> list[tuple[str, str]]:
    chunks: list[tuple[str, str]] = []

    qa_path = _DEMO_ASSETS / "course_qa.json"
    if qa_path.exists():
        qa = json.loads(qa_path.read_text(encoding="utf-8"))
        for entry in qa.get("entries", []):
            chunks.append(
                (
                    f"qa-{entry.get('id', len(chunks))}",
                    f"【问答】{entry.get('question', '')}\n{entry.get('answer', '')}",
                )
            )

    md_path = _DEMO_ASSETS / "class_agent_QA.md"
    if md_path.exists():
        raw = md_path.read_text(encoding="utf-8")
        for i, part in enumerate(raw.split("### ")):
            part = part.strip()
            if part:
                chunks.append((f"md-{i}", part[:1500]))

    slide_dir = _DEMO_ASSETS / "ppt-slides-with-assets"
    if slide_dir.exists():
        for file in sorted(slide_dir.glob("slide-*.json")):
            slide = json.loads(file.read_text(encoding="utf-8"))
            body = _extract_slide_text(slide)
            if body:
                chunks.append((f"slide-{file.name}", f"【课件 {file.name}】\n{body}"))

    slides_kb = _DEMO_ASSETS / "course_slides_kb.json"
    if slides_kb.exists():
        data = json.loads(slides_kb.read_text(encoding="utf-8"))
        for slide in data.get("slides", []):
            title = slide.get("title", "")
            body = slide.get("body", "")
            sid = slide.get("id", f"slide-kb-{len(chunks)}")
            if title or body:
                chunks.append((sid, f"【课件 {title}】\n{body}"))

    return chunks


def get_client() -> chromadb.PersistentClient:
    _CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(_CHROMA_PATH))


def build_index() -> int:
    chunks = load_chunks()
    if not chunks:
        raise RuntimeError("No documents to index")

    client = get_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(COLLECTION_NAME)
    collection.add(
        ids=[c[0] for c in chunks],
        documents=[c[1] for c in chunks],
    )
    return len(chunks)


def retrieve(query: str, top_k: int = 4) -> list[str]:
    query = (query or "").strip()
    if not query:
        return []

    client = get_client()
    try:
        collection = client.get_collection(COLLECTION_NAME)
    except Exception:
        return []

    if collection.count() == 0:
        return []

    result = collection.query(query_texts=[query], n_results=top_k)
    docs = result.get("documents") or [[]]
    return [d for d in docs[0] if isinstance(d, str) and d.strip()]
