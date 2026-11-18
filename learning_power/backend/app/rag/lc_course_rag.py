"""
LangChain RAG：Document 加载 → Chroma VectorStore → Retriever → LCEL 问答链
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI

from app.rag.course_rag import COLLECTION_NAME, _CHROMA_PATH, load_chunks

EMBEDDING_MODEL = os.getenv(
    "RAG_EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)


def chunks_to_documents(chunks: list[tuple[str, str]]) -> list[Document]:
    documents: list[Document] = []
    for doc_id, text in chunks:
        doc_type = "qa"
        if doc_id.startswith("md-"):
            doc_type = "markdown"
        elif doc_id.startswith("slide-"):
            doc_type = "slide"
        elif doc_id.startswith("qa-"):
            doc_type = "qa"
        documents.append(
            Document(
                page_content=text,
                metadata={"id": doc_id, "source": doc_id, "type": doc_type},
            )
        )
    return documents


@lru_cache(maxsize=1)
def get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def get_vectorstore() -> Chroma:
    _CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    return Chroma(
        persist_directory=str(_CHROMA_PATH),
        embedding_function=get_embeddings(),
        collection_name=COLLECTION_NAME,
    )


def get_retriever(top_k: int = 4):
    return get_vectorstore().as_retriever(search_kwargs={"k": top_k})


def build_index_lc() -> int:
    chunks = load_chunks()
    if not chunks:
        raise RuntimeError("No documents to index")

    documents = chunks_to_documents(chunks)
    _CHROMA_PATH.mkdir(parents=True, exist_ok=True)

    # 重建 collection（与旧脚本行为一致）
    try:
        existing = Chroma(
            persist_directory=str(_CHROMA_PATH),
            embedding_function=get_embeddings(),
            collection_name=COLLECTION_NAME,
        )
        existing.delete_collection()
    except Exception:
        pass

    Chroma.from_documents(
        documents=documents,
        embedding=get_embeddings(),
        persist_directory=str(_CHROMA_PATH),
        collection_name=COLLECTION_NAME,
    )
    return len(documents)


def retrieve_lc(query: str, top_k: int = 4) -> list[str]:
    query = (query or "").strip()
    if not query:
        return []
    docs = get_retriever(top_k=top_k).invoke(query)
    return [d.page_content for d in docs if d.page_content.strip()]


def _format_docs(docs: list[Document]) -> str:
    return "\n\n---\n\n".join(d.page_content for d in docs)


@lru_cache(maxsize=1)
def get_lc_chat_model() -> ChatOpenAI:
    api_key = os.getenv("SILICONFLOW_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("SILICONFLOW_BASE_URL", "https://api.deepseek.com/v1")
    model = os.getenv("SILICONFLOW_MODEL_CHAT_A", "deepseek-chat")
    if not api_key:
        raise RuntimeError("SILICONFLOW_API_KEY or OPENAI_API_KEY required for RAG QA chain")
    return ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=0.3,
    )


def create_rag_qa_chain(top_k: int = 4):
    """LCEL：Retriever → Prompt → ChatModel → String"""
    retriever = get_retriever(top_k=top_k)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "你是《人工智能基础》课堂助教。仅根据下列检索到的课件/QA 内容回答，"
                "不知道则说明未在资料中找到，不要编造。\n\n## 检索内容\n{context}",
            ),
            ("human", "{question}"),
        ]
    )
    llm = get_lc_chat_model()

    def load_context(question: str) -> str:
        docs = retriever.invoke(question)
        return _format_docs(docs)

    chain = (
        RunnablePassthrough.assign(context=lambda x: load_context(x["question"]))
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain, retriever


def answer_with_rag_chain(question: str, top_k: int = 4) -> dict:
    chain, retriever = create_rag_qa_chain(top_k=top_k)
    docs = retriever.invoke(question)
    answer = chain.invoke({"question": question})
    return {
        "answer": answer,
        "chunks": [d.page_content for d in docs],
        "chunk_count": len(docs),
        "source": "langchain-rag-lcel",
        "embedding_model": EMBEDDING_MODEL,
    }
