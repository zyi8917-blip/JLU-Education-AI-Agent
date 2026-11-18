"""LangChain Tools：课件检索等（供 Tool Calling Agent 使用）"""
from __future__ import annotations

from langchain_core.tools import tool

from app.rag.rag_service import retrieve


@tool
def search_course_materials(query: str) -> str:
    """检索《人工智能基础》课件、Slide 文本与 QA 问答库。输入为自然语言问题或关键词，返回 Top-4 相关片段。"""
    q = (query or "").strip()
    if not q:
        return "请提供检索关键词或问题。"
    chunks = retrieve(q, top_k=4)
    if not chunks:
        return "未在资料库中找到相关内容。"
    return "\n\n---\n\n".join(chunks)


COURSE_AGENT_TOOLS = [search_course_materials]
