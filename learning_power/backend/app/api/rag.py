"""RAG 检索 API（LangChain Retriever + 可选 LCEL 问答链）"""
import logging

from flask import request

from app.api import rag_bp
from app.rag.rag_service import retrieve, use_lc_rag
from app.utils.response import success_response, error_response

logger = logging.getLogger(__name__)


@rag_bp.route("/course", methods=["GET"])
def retrieve_course():
    query = request.args.get("query", "").strip()
    top_k = request.args.get("top_k", 4, type=int)
    if not query:
        return error_response("query is required", 400)
    chunks = retrieve(query, top_k=top_k)
    backend = "langchain" if use_lc_rag() else "chromadb"
    return success_response(
        {
            "query": query,
            "chunks": chunks,
            "source": "chroma" if chunks else "none",
            "count": len(chunks),
            "rag_backend": backend,
        }
    )


@rag_bp.route("/qa", methods=["POST"])
def rag_qa():
    """
    LangChain LCEL：Retriever | Prompt | ChatModel
    Body: { "question": "...", "top_k": 4 }
    """
    data = request.get_json() or {}
    question = (data.get("question") or "").strip()
    top_k = int(data.get("top_k") or 4)
    if not question:
        return error_response("question is required", 400)

    try:
        from app.rag.lc_course_rag import answer_with_rag_chain

        payload = answer_with_rag_chain(question, top_k=top_k)
        return success_response(payload)
    except Exception as exc:
        logger.error("RAG QA chain failed: %s", exc, exc_info=True)
        return error_response(f"RAG QA failed: {exc}", 500)
