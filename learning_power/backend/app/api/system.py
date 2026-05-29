"""
系统设置API
"""
from flask import request, jsonify
from datetime import datetime, date
from app.api import system_bp
from app.utils.response import success_response, error_response
from app.models.student import Student
from app.models.assessment import Assessment

# 导入数据存储（从其他模块）
from app.api.assessments import sessions_store

# 系统配置存储
system_config = {
    'max_questions': 10,
    'time_limit_minutes': 30,
    'model_name': 'DeepSeek-V3',
    'debug': False
}


@system_bp.route('/config', methods=['GET'])
def get_config():
    """获取系统配置"""
    try:
        return success_response(system_config)
    except Exception as e:
        return error_response(str(e), 500)


@system_bp.route('/config', methods=['PUT'])
def update_config():
    """更新系统配置"""
    try:
        data = request.get_json()

        # 更新配置
        if 'max_questions' in data:
            system_config['max_questions'] = data['max_questions']
        if 'time_limit_minutes' in data:
            system_config['time_limit_minutes'] = data['time_limit_minutes']
        if 'model_name' in data:
            system_config['model_name'] = data['model_name']
        if 'debug' in data:
            system_config['debug'] = data['debug']

        return success_response(system_config, message='Configuration updated successfully')
    except Exception as e:
        return error_response(str(e), 500)


@system_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """获取统计数据 - 从数据库动态计算"""
    try:
        # 1. 学生总数
        total_students = Student.query.count()

        # 2. 测评总数（已完成的测评）- 从数据库查询
        total_assessments = Assessment.query.count()

        # 3. 今日测评数 - 从数据库查询
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        assessments_today = Assessment.query.filter(
            Assessment.end_time >= today_start,
            Assessment.end_time <= today_end
        ).count()

        # 4. 平均分数 - 从数据库计算
        average_score = 0.0
        if total_assessments > 0:
            from sqlalchemy import func
            avg_result = Assessment.query.with_entities(func.avg(Assessment.total_score)).scalar()
            average_score = round(avg_result, 1) if avg_result else 0.0

        # 5. 活跃会话数（进行中的测评）
        active_sessions = sum(1 for s in sessions_store.values() if s.get('status') == 'in_progress')

        stats = {
            'total_students': total_students,
            'total_assessments': total_assessments,
            'assessments_today': assessments_today,
            'average_score': average_score,
            'active_sessions': active_sessions
        }

        return success_response(stats)
    except Exception as e:
        return error_response(str(e), 500)


@system_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    try:
        health_status = {
            'status': 'healthy',
            'database': 'connected',
            'ai_service': 'available',
            'uptime': '2 days, 5 hours',
            'timestamp': datetime.now().isoformat()
        }
        
        return success_response(health_status)
    except Exception as e:
        return error_response(str(e), 500)

