"""
LangGraph StateGraph: 测评完成 → 生成报告 → 画像上下文就绪

三节点线性编排，供 complete_session 与画像对话复用。
"""
from __future__ import annotations

import logging
import time
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from app.utils.llm_client import get_llm_client

logger = logging.getLogger(__name__)


class AssessmentWorkflowState(TypedDict, total=False):
    session_id: str
    student_id: str
    student_name: str
    evaluation_type: str
    question_answer_pairs: list[dict[str, str]]
    evaluation_result: dict[str, Any]
    report_payload: dict[str, Any]
    portrait_data: dict[str, Any]
    workflow_ms: float
    error: str | None


def _score_to_rating(score: float) -> str:
    if score >= 85:
        return "优秀"
    if score >= 75:
        return "良好"
    if score >= 65:
        return "中等"
    if score >= 55:
        return "待提升"
    return "需加强"


def node_evaluate_answers(state: AssessmentWorkflowState) -> AssessmentWorkflowState:
    """节点1：批量 LLM 评测答案（默认 LangChain ChatPromptTemplate + ChatOpenAI）。"""
    pairs = state.get("question_answer_pairs") or []
    evaluation_type = state.get("evaluation_type") or "creativity"
    llm = get_llm_client()

    try:
        from app.agents.lc_batch_evaluate import batch_evaluate_lc, use_lc_eval

        if use_lc_eval():
            try:
                result = batch_evaluate_lc(pairs, evaluation_type)
                return {**state, "evaluation_result": result, "error": None}
            except Exception as lc_exc:
                logger.warning("LangChain batch evaluate failed, fallback: %s", lc_exc)

        result = llm.batch_evaluate_answers(
            question_answer_pairs=pairs,
            evaluation_type=evaluation_type,
        )
        return {**state, "evaluation_result": result, "error": None}
    except Exception as exc:
        logger.error("evaluate_answers node failed: %s", exc, exc_info=True)
        return {**state, "evaluation_result": {}, "error": str(exc)}


def node_generate_report(state: AssessmentWorkflowState) -> AssessmentWorkflowState:
    """节点2：将评测结果加工为前端报告结构。"""
    evaluation = state.get("evaluation_result") or {}
    detailed_scores = evaluation.get("detailed_scores", {})
    rating_summary = dict(evaluation.get("rating_summary", {}))
    feedback = evaluation.get("feedback", {})
    grade_level = evaluation.get("grade_level", "C")

    total_score = rating_summary.pop("total", 0) if isinstance(rating_summary, dict) else 0
    final_scores = rating_summary if isinstance(rating_summary, dict) else {}

    answer_details = []
    pairs = state.get("question_answer_pairs") or []
    for idx, (key, detail) in enumerate(detailed_scores.items()):
        pair = pairs[idx] if idx < len(pairs) else {}
        answer_details.append(
            {
                "question_id": key,
                "question_content": pair.get("question_content", ""),
                "answer_content": pair.get("answer_content", ""),
                "scores": detail.get("rating", 0) if isinstance(detail, dict) else 0,
                "comments": detail.get("reason", "") if isinstance(detail, dict) else "",
            }
        )

    report_payload = {
        "final_scores": final_scores,
        "total_score": total_score,
        "answer_details": answer_details,
        "feedback": feedback,
        "grade_level": grade_level,
    }
    return {**state, "report_payload": report_payload, "error": state.get("error")}


def node_prepare_portrait(state: AssessmentWorkflowState) -> AssessmentWorkflowState:
    """节点3：生成画像对话所需的 portrait_data。"""
    report = state.get("report_payload") or {}
    final_scores = report.get("final_scores") or {}
    feedback = report.get("feedback") or {}

    total_dict = {k: float(v) for k, v in final_scores.items() if isinstance(v, (int, float))}
    rating_dict = {k: _score_to_rating(float(v)) for k, v in total_dict.items()}

    feedback_dict: dict[str, str] = {}
    if isinstance(feedback, dict):
        dim_fb = feedback.get("dimension_feedback", {})
        if isinstance(dim_fb, dict):
            feedback_dict.update({k: str(v) for k, v in dim_fb.items()})
        overall = feedback.get("overall_feedback")
        if overall:
            feedback_dict["overall"] = str(overall)

    portrait_data = {
        "total_dict": total_dict,
        "rating_dict": rating_dict,
        "feedback_dict": feedback_dict,
        "student_id": state.get("student_id"),
        "student_name": state.get("student_name"),
        "evaluation_type": state.get("evaluation_type"),
        "grade_level": report.get("grade_level"),
        "total_score": report.get("total_score"),
        "ready_for_chat": True,
    }
    return {**state, "portrait_data": portrait_data}


def _build_graph():
    graph = StateGraph(AssessmentWorkflowState)
    graph.add_node("evaluate_answers", node_evaluate_answers)
    graph.add_node("generate_report", node_generate_report)
    graph.add_node("prepare_portrait", node_prepare_portrait)
    graph.add_edge(START, "evaluate_answers")
    graph.add_edge("evaluate_answers", "generate_report")
    graph.add_edge("generate_report", "prepare_portrait")
    graph.add_edge("prepare_portrait", END)
    return graph.compile()


_WORKFLOW = _build_graph()


def run_assessment_workflow(
    *,
    session_id: str,
    student_id: str,
    student_name: str,
    evaluation_type: str,
    question_answer_pairs: list[dict[str, str]],
) -> AssessmentWorkflowState:
    """执行完整测评编排并返回终态。"""
    started = time.perf_counter()
    initial: AssessmentWorkflowState = {
        "session_id": session_id,
        "student_id": student_id,
        "student_name": student_name,
        "evaluation_type": evaluation_type,
        "question_answer_pairs": question_answer_pairs,
    }
    final = _WORKFLOW.invoke(initial)
    final["workflow_ms"] = round((time.perf_counter() - started) * 1000, 2)
    logger.info(
        "Assessment workflow finished session=%s ms=%s portrait_ready=%s",
        session_id,
        final.get("workflow_ms"),
        (final.get("portrait_data") or {}).get("ready_for_chat"),
    )
    return final
