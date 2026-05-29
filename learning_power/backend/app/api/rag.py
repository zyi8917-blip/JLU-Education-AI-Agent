"""RAG 检索 API"""
from flask import request

from app.api import rag_bp
from app.rag.course_rag import retrieve
from app.utils.response import success_response, error_response


@rag_bp.route("/course", methods=["GET"])
def retrieve_course():
    query = request.args.get("query", "").strip()
    top_k = request.args.get("top_k", 4, type=int)
    if not query:
        return error_response("query is required", 400)
    chunks = retrieve(query, top_k=top_k)
    return success_response(
        {
            "query": query,
            "chunks": chunks,
            "source": "chroma" if chunks else "none",
            "count": len(chunks),
        }
    )
