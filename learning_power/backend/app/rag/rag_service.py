"""RAG 统一入口：默认 LangChain，可回退原生 Chroma。"""
from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


def use_lc_rag() -> bool:
    return os.getenv("USE_LC_RAG", "true").lower() in ("1", "true", "yes")


def build_index() -> int:
    if use_lc_rag():
        try:
            from app.rag.lc_course_rag import build_index_lc

            n = build_index_lc()
            logger.info("Built RAG index with LangChain (%s chunks)", n)
            return n
        except Exception as exc:
            logger.warning("LangChain index build failed, fallback: %s", exc)
    from app.rag.course_rag import build_index as build_legacy

    return build_legacy()


def retrieve(query: str, top_k: int = 4) -> list[str]:
    if use_lc_rag():
        try:
            from app.rag.lc_course_rag import retrieve_lc

            return retrieve_lc(query, top_k=top_k)
        except Exception as exc:
            logger.warning("LangChain retrieve failed, fallback: %s", exc)
    from app.rag.course_rag import retrieve as retrieve_legacy

    return retrieve_legacy(query, top_k=top_k)
