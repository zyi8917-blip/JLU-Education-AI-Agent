"""LangChain Tool Calling Agent：按需调用课件检索 Tool 后作答"""
from __future__ import annotations

import logging
import os

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from app.agents.course_tools import COURSE_AGENT_TOOLS, search_course_materials

logger = logging.getLogger(__name__)


def _get_chat_model() -> ChatOpenAI:
    api_key = os.getenv("SILICONFLOW_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("SILICONFLOW_BASE_URL", "https://api.deepseek.com/v1")
    model = os.getenv("SILICONFLOW_MODEL_CHAT_A", "deepseek-chat")
    if not api_key:
        raise RuntimeError("SILICONFLOW_API_KEY or OPENAI_API_KEY required")
    return ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=0.3,
    )


def run_course_tool_agent(question: str, chat_history: list | None = None) -> dict:
    """
    单轮 Tool Agent：模型可调用 search_course_materials，再生成最终回答。
    """
    question = (question or "").strip()
    if not question:
        raise ValueError("question is required")

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "你是《人工智能基础》课堂助教。需要事实依据时必须先调用 search_course_materials，"
                "不要编造课件内容。用中文简洁回答。",
            ),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    llm = _get_chat_model()
    agent = create_tool_calling_agent(llm, COURSE_AGENT_TOOLS, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=COURSE_AGENT_TOOLS,
        verbose=False,
        max_iterations=3,
        handle_parsing_errors=True,
    )

    history = chat_history or []
    result = executor.invoke({"input": question, "chat_history": history})
    output = (result.get("output") or "").strip()

    # 额外做一次检索便于 API 返回引用片段（与 Tool 结果一致）
    chunks = retrieve_via_tool(question)

    return {
        "answer": output,
        "chunks": chunks,
        "chunk_count": len(chunks),
        "source": "langchain-tool-agent",
        "tools_used": ["search_course_materials"],
    }


def retrieve_via_tool(query: str) -> list[str]:
    raw = search_course_materials.invoke({"query": query})
    if not raw or raw.startswith("未在") or raw.startswith("请提供"):
        return []
    return [p.strip() for p in raw.split("\n\n---\n\n") if p.strip()]
