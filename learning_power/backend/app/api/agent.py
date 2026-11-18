"""Agent API：Tool Calling、PBL 分阶段提示"""
import logging
import os

from flask import request

from app.api import agent_bp
from app.utils.response import error_response, success_response

logger = logging.getLogger(__name__)

PBL_PHASE_GUIDE = {
    "coach": "澄清教学目标与服务对象，追问具体课堂场景。",
    "design": "引导补全至少 3 个核心功能与使用流程（课前/课中/课后）。",
    "review": "评估方案完整性，补充幻觉、隐私、过度依赖 AI 等风险与优化建议。",
}

PBL_AGENT_NAMES = {
    "coach": "课程教练 Agent",
    "design": "方案设计 Agent",
    "review": "评估反馈 Agent",
}


@agent_bp.route("/course", methods=["POST"])
def course_tool_agent():
    """
    LangChain Tool Calling Agent
    Body: { "question": "...", "chat_history": [] }
    """
    data = request.get_json() or {}
    question = (data.get("question") or "").strip()
    history = data.get("chat_history") or []
    if not question:
        return error_response("question is required", 400)

    try:
        from app.agents.lc_tool_agent import run_course_tool_agent

        payload = run_course_tool_agent(question, chat_history=history)
        return success_response(payload)
    except Exception as exc:
        logger.error("course tool agent failed: %s", exc, exc_info=True)
        return error_response(f"Agent failed: {exc}", 500)


@agent_bp.route("/pbl", methods=["POST"])
def pbl_agent_meta():
    """
    PBL 多 Agent 元数据与系统提示（供前端或联调复用）
    Body: { "phase": "coach|design|review", "message": "..." }
    """
    data = request.get_json() or {}
    phase = (data.get("phase") or "coach").strip()
    if phase not in PBL_PHASE_GUIDE:
        return error_response("invalid phase", 400)

    use_lc = os.getenv("USE_LC_EVAL", "true").lower() in ("1", "true", "yes")
    return success_response(
        {
            "phase": phase,
            "agent_name": PBL_AGENT_NAMES[phase],
            "phase_guide": PBL_PHASE_GUIDE[phase],
            "pipeline": ["coach", "design", "review"],
            "langchain_eval_enabled": use_lc,
            "note": "完整对话流在 Next.js PBL 页，按轮次自动切换三 Agent。",
        }
    )
