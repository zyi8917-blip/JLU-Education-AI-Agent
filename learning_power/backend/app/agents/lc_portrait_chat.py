"""LangChain 画像对话：ChatPromptTemplate + 历史消息 + ChatOpenAI"""
from __future__ import annotations

import logging
import os
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

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
        temperature=0.7,
        max_tokens=800,
        timeout=30,
    )


def portrait_reply_lc(
    *,
    system_prompt: str,
    message: str,
    chat_history: list[dict[str, str]] | None = None,
) -> str:
    """基于 LangChain 消息链生成画像助手回复。"""
    history = chat_history or []
    recent = history[-10:]

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "{system_prompt}"),
            MessagesPlaceholder("history"),
            ("human", "{message}"),
        ]
    )

    lc_history: list[Any] = []
    for item in recent:
        role = item.get("role")
        content = item.get("content") or ""
        if role == "assistant":
            lc_history.append(AIMessage(content=content))
        elif role == "user":
            lc_history.append(HumanMessage(content=content))

    chain = prompt | _get_chat_model()
    msg = chain.invoke(
        {
            "system_prompt": system_prompt,
            "history": lc_history,
            "message": message,
        }
    )
    text = getattr(msg, "content", str(msg))
    logger.info("LangChain portrait reply length=%s", len(text))
    return text.strip()
