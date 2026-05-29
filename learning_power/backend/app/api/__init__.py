"""
API蓝图初始化
"""
from flask import Blueprint

# 创建蓝图
students_bp = Blueprint('students', __name__)
assessments_bp = Blueprint('assessments', __name__)
analysis_bp = Blueprint('analysis', __name__)
system_bp = Blueprint('system', __name__)
chat_bp = Blueprint('chat', __name__)
rag_bp = Blueprint('rag', __name__)

# 导入路由（避免循环导入）
from app.api import students, assessments, analysis, system, chat, rag

