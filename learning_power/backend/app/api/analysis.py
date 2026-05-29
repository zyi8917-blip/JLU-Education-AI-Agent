"""
分析报告API
"""
from flask import request, jsonify
from datetime import datetime
import logging
from app.api import analysis_bp
from app.utils.response import success_response, error_response
from app.models.assessment import Assessment

# 配置日志
logger = logging.getLogger(__name__)

# 定义评分等级对应的分数范围
GRADE_SCORES = {
    'A': 90,
    'B': 80,
    'C': 70,
    'D': 60
}


@analysis_bp.route('/assessment/<assessment_id>', methods=['GET'])
def get_assessment_analysis(assessment_id):
    """获取单次测评分析 - 从数据库获取"""
    try:
        logger.info(f"Getting analysis for assessment: {assessment_id}")

        # 从数据库获取测评数据
        assessment = Assessment.query.filter_by(assessment_id=assessment_id).first()

        if not assessment:
            logger.error(f"Assessment not found: {assessment_id}")
            return error_response('Assessment not found', 404)

        logger.info(f"Found assessment: {assessment.assessment_id}")

        # 转换为字典
        assessment_dict = assessment.to_dict()

        # 构建分析数据
        final_scores = assessment_dict.get('final_scores', {})
        total_score = assessment_dict.get('total_score', 0)
        feedback = assessment_dict.get('feedback', {})
        dimension_analysis = feedback.get('dimension_feedback', {}) if feedback else {}
        overall_feedback = feedback.get('overall_feedback', '') if feedback else ''

        analysis = {
            'assessment_id': assessment_id,
            'student_id': assessment_dict.get('student_id'),
            'student_name': assessment_dict.get('student_name'),
            'evaluation_type': assessment_dict.get('evaluation_type'),
            'end_time': assessment_dict.get('end_time'),
            'start_time': assessment_dict.get('start_time'),
            'scores': final_scores,  # 直接返回分数对象
            'total_score': total_score,
            'level': assessment_dict.get('grade_level'),  # 直接返回等级
            'dimension_analysis': dimension_analysis,
            'overall_feedback': overall_feedback  # 添加总体反馈
        }

        return success_response(analysis)
    except Exception as e:
        logger.error(f"Error getting assessment analysis: {str(e)}", exc_info=True)
        return error_response(str(e), 500)


@analysis_bp.route('/trend/<student_id>', methods=['GET'])
def get_trend_analysis(student_id):
    """获取趋势分析 - 从数据库获取"""
    try:
        limit = request.args.get('limit', 10, type=int)

        # 从数据库获取该学生的所有测评，按时间排序
        assessments = Assessment.query.filter_by(student_id=student_id)\
            .order_by(Assessment.end_time.asc())\
            .limit(limit)\
            .all()

        # 构建趋势数据
        assessments_data = []
        for assessment in assessments:
            assessment_dict = assessment.to_dict()
            scores = assessment_dict.get('final_scores', {})
            assessments_data.append({
                'date': assessment_dict['end_time'][:10],  # 只取日期部分
                'fluency': scores.get('fluency', 0),
                'flexibility': scores.get('flexibility', 0),
                'originality': scores.get('originality', 0),
                'elaboration': scores.get('elaboration', 0),
                'total': assessment_dict.get('total_score', 0)
            })

        # 计算趋势（如果有多次测评）
        trend = {}
        if len(assessments_data) >= 2:
            first = assessments_data[0]
            last = assessments_data[-1]

            for key in ['fluency', 'flexibility', 'originality', 'elaboration', 'total']:
                if first[key] > 0:
                    change = ((last[key] - first[key]) / first[key]) * 100
                    trend[key] = f"{'+' if change >= 0 else ''}{change:.1f}%"
                else:
                    trend[key] = 'N/A'

        trend_data = {
            'student_id': student_id,
            'assessments': assessments_data,
            'trend': trend
        }

        return success_response(trend_data)
    except Exception as e:
        logger.error(f"Error getting trend analysis: {str(e)}", exc_info=True)
        return error_response(str(e), 500)


@analysis_bp.route('/radar/<assessment_id>', methods=['GET'])
def get_radar_data(assessment_id):
    """获取雷达图数据 - 从数据库获取"""
    try:
        # 从数据库获取测评数据
        assessment = Assessment.query.filter_by(assessment_id=assessment_id).first()

        if not assessment:
            return error_response('Assessment not found', 404)

        assessment_dict = assessment.to_dict()
        scores = assessment_dict.get('final_scores', {})

        radar_data = {
            'dimensions': ['流畅性', '灵活性', '独创性', '精细性'],
            'values': [
                int(scores.get('fluency', 0) * 10),
                int(scores.get('flexibility', 0) * 10),
                int(scores.get('originality', 0) * 10),
                int(scores.get('elaboration', 0) * 10)
            ],
            'max_value': 100
        }

        return success_response(radar_data)
    except Exception as e:
        logger.error(f"Error getting radar data: {str(e)}", exc_info=True)
        return error_response(str(e), 500)


@analysis_bp.route('/compare', methods=['GET'])
def compare_assessments():
    """对比分析 - 从数据库获取"""
    try:
        student_id = request.args.get('student_id')
        assessment_ids = request.args.get('assessment_ids', '').split(',')

        if not student_id or not assessment_ids:
            return error_response('student_id and assessment_ids are required', 400)

        # 获取指定的测评数据
        comparisons = []
        for assessment_id in assessment_ids:
            assessment = Assessment.query.filter_by(
                assessment_id=assessment_id.strip(),
                student_id=student_id
            ).first()

            if assessment:
                assessment_dict = assessment.to_dict()
                scores = assessment_dict.get('final_scores', {})
                comparisons.append({
                    'assessment_id': assessment_id.strip(),
                    'date': assessment_dict['end_time'][:10],
                    'scores': {
                        'fluency': scores.get('fluency', 0),
                        'flexibility': scores.get('flexibility', 0),
                        'originality': scores.get('originality', 0),
                        'elaboration': scores.get('elaboration', 0)
                    },
                    'total_score': assessment_dict.get('total_score', 0)
                })

        return success_response({'comparisons': comparisons})
    except Exception as e:
        logger.error(f"Error comparing assessments: {str(e)}", exc_info=True)
        return error_response(str(e), 500)


@analysis_bp.route('/overall/<student_id>', methods=['GET'])
def get_overall_analysis(student_id):
    """
    获取全体测评分析
    统计该用户所有测评的评级信息和汇总评语内容
    """
    try:
        logger.info(f"Getting overall analysis for student: {student_id}")

        # 从数据库获取该学生的所有测评记录
        assessments = Assessment.query.filter_by(student_id=student_id).all()

        if not assessments:
            return error_response('No assessments found for this student', 404)

        # 转换为字典列表
        student_assessments = [a.to_dict() for a in assessments]

        # 获取评级（{对应指标：评级}）
        level_dict = {}
        for assessment in student_assessments:
            level_dict[assessment['evaluation_type']] = assessment.get('grade_level', 'N/A')

        # 获取总分 （{对应指标：总分}）
        total_dict = {}
        for assessment in student_assessments:
            total_dict[assessment['evaluation_type']] = assessment.get('total_score', 0)

        # 获取评语 （{对应指标：评语}）
        feedback_dict = {}
        for assessment in student_assessments:
            feedback = assessment.get('feedback', {})
            if feedback:
                feedback_dict[assessment['evaluation_type']] = feedback.get('overall_feedback', 'N/A')
            else:
                feedback_dict[assessment['evaluation_type']] = 'N/A'

        # 获取各维度详细分数（{对应指标：{子维度：分数}}）
        dimension_scores_dict = {}
        for assessment in student_assessments:
            eval_type = assessment['evaluation_type']
            final_scores = assessment.get('final_scores', {})

            # 对批判性思维的历史数据进行100分制转换
            # 如果子维度分数都小于等于20，说明是旧的20分制数据，需要转换为100分制
            if eval_type == 'critical_thinking' and final_scores:
                # 检测是否为旧的20分制数据（所有分数都<=20）
                all_scores = [v for v in final_scores.values() if isinstance(v, (int, float))]
                if all_scores and max(all_scores) <= 20:
                    # 转换为100分制：分数 * 5
                    final_scores = {k: round(v * 5, 2) if isinstance(v, (int, float)) else v
                                   for k, v in final_scores.items()}

            dimension_scores_dict[eval_type] = final_scores

        # 获取各维度详细反馈（{对应指标：{子维度：反馈}}）
        dimension_feedback_dict = {}
        for assessment in student_assessments:
            feedback = assessment.get('feedback', {})
            if feedback and 'dimension_feedback' in feedback:
                dimension_feedback_dict[assessment['evaluation_type']] = feedback.get('dimension_feedback', {})
            else:
                dimension_feedback_dict[assessment['evaluation_type']] = {}

        # 构建响应数据
        overall_analysis = {
            'student_id': student_id,
            'student_name': student_assessments[0].get('student_name', ''),
            'total_assessments': len(student_assessments),
            'level_dict': level_dict,
            'total_dict': total_dict,
            'feedback_dict': feedback_dict,
            'dimension_scores_dict': dimension_scores_dict,  # 新增：各维度详细分数
            'dimension_feedback_dict': dimension_feedback_dict  # 新增：各维度详细反馈
        }

        return success_response(overall_analysis)

    except Exception as e:
        logger.error(f"Error getting overall analysis: {str(e)}", exc_info=True)
        return error_response(str(e), 500)


@analysis_bp.route('/list', methods=['GET'])
def get_analysis_list():
    """获取测评列表 - 从数据库获取"""
    try:
        # 获取查询参数
        student_id = request.args.get('student_id')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))

        logger.info(f"Getting analysis list, student_id: {student_id}, page: {page}, page_size: {page_size}")

        # 构建查询
        query = Assessment.query

        # 按学生ID筛选
        if student_id:
            query = query.filter_by(student_id=student_id)

        # 按完成时间倒序排序
        query = query.order_by(Assessment.end_time.desc())

        # 分页
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()

        # 格式化返回数据
        formatted_items = []
        for assessment in items:
            assessment_dict = assessment.to_dict()
            formatted_items.append({
                'assessment_id': assessment_dict['assessment_id'],
                'student_id': assessment_dict['student_id'],
                'student_name': assessment_dict['student_name'],
                'evaluation_type': assessment_dict['evaluation_type'],
                'start_time': assessment_dict['start_time'],
                'end_time': assessment_dict['end_time'],
                'total_score': assessment_dict['total_score'],
                'final_scores': assessment_dict['final_scores'],
                'status': assessment_dict['status']
            })

        logger.info(f"Found {total} assessments, returning {len(formatted_items)} items")

        return success_response({
            'total': total,
            'page': page,
            'page_size': page_size,
            'items': formatted_items
        })
    except Exception as e:
        logger.error(f"Error getting analysis list: {str(e)}", exc_info=True)
        return error_response(str(e), 500)

