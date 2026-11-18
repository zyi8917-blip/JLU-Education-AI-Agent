"""LangChain 批量测评：ChatPromptTemplate + ChatOpenAI + JSON 解析（与 LangGraph evaluate 节点对接）"""
from __future__ import annotations

import json
import logging
import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from app.utils.llm_client import get_llm_client, prompt_data

logger = logging.getLogger(__name__)


def use_lc_eval() -> bool:
    return os.getenv("USE_LC_EVAL", "true").lower() in ("1", "true", "yes")


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
        max_tokens=2000,
        timeout=120,
    )


def _format_qa_block(question_answer_pairs: list[dict]) -> str:
    lines: list[str] = []
    for idx, pair in enumerate(question_answer_pairs, 1):
        q = pair.get("question_content") or pair.get("question") or ""
        a = pair.get("answer_content") or pair.get("answer") or ""
        lines.append(f"问题{idx}: {q}\n答案{idx}: {a}\n")
    return "\n".join(lines)


def batch_evaluate_lc(
    question_answer_pairs: list[dict],
    evaluation_type: str,
) -> dict:
    if not prompt_data or evaluation_type not in prompt_data:
        raise ValueError(f"Unknown evaluation_type: {evaluation_type}")

    evaluation_config = prompt_data[evaluation_type]
    prompt_template = evaluation_config.get("prompt", "")
    output_template = evaluation_config.get("output_template", {})

    lc_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "你是一位专业的教育心理学家，根据学生对开放性问卷答案评估其对应指标的学习能力。"
                "请严格按照用户要求的 JSON 结构输出，不要输出 markdown 代码块或多余说明。",
            ),
            (
                "human",
                "{rubric}\n\n# 测评问题及用户答案\n{qa_block}\n\n"
                "# 输出格式\n请返回可被 Python json.loads 解析的 JSON，结构如下：\n{output_schema}",
            ),
        ]
    )

    chain = lc_prompt | _get_chat_model() | StrOutputParser()
    result_text = chain.invoke(
        {
            "rubric": prompt_template,
            "qa_block": _format_qa_block(question_answer_pairs),
            "output_schema": json.dumps(output_template, ensure_ascii=False, indent=2),
        }
    )

    logger.info("LangChain batch evaluate finished (type=%s, chars=%s)", evaluation_type, len(result_text))
    llm = get_llm_client()
    return llm._parse_batch_evaluation_result(result_text.strip(), evaluation_type)
