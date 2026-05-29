"""
测评管理API
"""
from flask import request, jsonify
from datetime import datetime
import logging
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.api import assessments_bp
from app.utils.response import success_response, error_response
from app.agents.assessment_workflow import run_assessment_workflow
from app.utils.llm_client import get_llm_client
from app import db
from app.models.assessment import Assessment
from app.models.student import Student

# 配置日志
logger = logging.getLogger(__name__)

# 临时存储（会话和答案仍使用内存，因为它们是临时的）
sessions_store = {}
questions_store = {}
answers_store = {}
# 已完成的测评现在存储在数据库中，不再使用内存存储
# completed_assessments_store = {}  # 已废弃，改用数据库

# 加载prompt.json文件
def load_prompt_data():
    """加载prompt.json文件"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_file_path = os.path.join(current_dir, '..', 'prompt.json')
        
        with open(prompt_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading prompt.json: {str(e)}")
        return {}

# 全局存储prompt数据
prompt_data = load_prompt_data()


@assessments_bp.route('/sessions', methods=['POST'])
def create_session():
    """创建测评会话"""
    try:
        data = request.get_json()
        
        if not data.get('student_id') or not data.get('student_name'):
            return error_response('student_id and student_name are required', 400)
        
        # 生成会话ID
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 创建会话
        session = {
            'session_id': session_id,
            'student_id': data['student_id'],
            'student_name': data['student_name'],
            'evaluation_type': data['evaluationType'],
            'status': 'in_progress',
            'start_time': datetime.now().isoformat(),
            'end_time': None
        }
        
        sessions_store[session_id] = session
        
        return success_response(session, message='Assessment session created')
    except Exception as e:
        return error_response(str(e), 500)


@assessments_bp.route('/sessions/<session_id>/questions', methods=['GET'])
def get_questions(session_id):
    """获取题目列表（支持个性化改写）"""
    try:
        session = sessions_store.get(session_id)

        if not session:
            return error_response('Session not found', 404)

        # 从prompt.json获取对应测评类型的题目
        evaluation_type = session.get('evaluation_type', 'creativity')
        student_id = session.get('student_id')

        # 如果prompt_data为空，使用默认题目
        if not prompt_data or evaluation_type not in prompt_data:
            # 使用默认的创造力题目
            default_questions = [
                {
                    'id': 'Q001',
                    'content': '请列举出砖块的所有可能用途。尽可能多地想出不同的用法。'
                },
                {
                    'id': 'Q002',
                    'content': '如果你有一个可以变成任何形状的魔法盒子，你会用它来做什么？请描述至少5种不同类型的用途。'
                },
                {
                    'id': 'Q003',
                    'content': '设计一个从未存在过的新型交通工具。请详细描述它的外观、功能和工作原理。'
                }
            ]
            questions_store[session_id] = default_questions
            return success_response({
                'questions': default_questions,
                'total': len(default_questions)
            })

        # 从prompt.json获取题目
        evaluation_data = prompt_data[evaluation_type]
        questions = evaluation_data.get('questions', [])

        # 格式化题目，添加id字段
        formatted_questions = []
        for question in questions:
            formatted_questions.append({
                'id': question['id'],
                'content': question['content']
            })

        # 尝试个性化改写问题
        try:
            if student_id:
                # 从数据库查询学生信息
                student = Student.query.filter_by(student_id=student_id).first()

                if student:
                    logger.info(f"Found student info for {student_id}, personalizing questions...")
                    student_info = student.to_dict()

                    # 调用LLM进行个性化改写
                    llm_client = get_llm_client()
                    personalized_questions = llm_client.personalize_questions(formatted_questions, student_info)

                    # 使用个性化后的问题
                    formatted_questions = personalized_questions
                    logger.info(f"Questions personalized successfully for student {student_id}")
                else:
                    logger.info(f"Student {student_id} not found in database, using original questions")
            else:
                logger.info("No student_id in session, using original questions")
        except Exception as e:
            logger.warning(f"Failed to personalize questions: {str(e)}, using original questions")
            # 如果个性化失败，继续使用原始问题

        # 缓存问题（无论是否个性化）
        questions_store[session_id] = formatted_questions

        return success_response({
            'questions': formatted_questions,
            'total': len(formatted_questions)
        })
    except Exception as e:
        logger.error(f"Error getting questions: {str(e)}")
        return error_response(str(e), 500)


@assessments_bp.route('/sessions/<session_id>/questions/<int:question_index>', methods=['GET'])
def get_question(session_id, question_index):
    """获取单个题目"""
    try:
        session = sessions_store.get(session_id)
        
        if not session:
            return error_response('Session not found', 404)
        
        questions = questions_store.get(session_id, [])
        
        if question_index < 0 or question_index >= len(questions):
            return error_response('Invalid question index', 400)
        
        question = questions[question_index]
        
        return success_response({
            'question': question,
            'progress': {
                'current': question_index + 1,
                'total': len(questions),
                'percentage': int((question_index + 1) / len(questions) * 100)
            }
        })
    except Exception as e:
        return error_response(str(e), 500)


@assessments_bp.route('/sessions/<session_id>/answers', methods=['POST'])
def submit_answer(session_id):
    """提交答案"""
    try:
        data = request.get_json()

        session = sessions_store.get(session_id)

        if not session:
            return error_response('Session not found', 404)

        if not data.get('question_id') or not data.get('content'):
            return error_response('question_id and content are required', 400)

        # 生成答案ID
        answer_id = f"ANS{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # 保存答案
        answer = {
            'answer_id': answer_id,
            'session_id': session_id,
            'question_id': data['question_id'],
            'content': data['content'],
            'time_spent': data.get('time_spent', 0),
            'submitted_at': datetime.now().isoformat()
        }

        if session_id not in answers_store:
            answers_store[session_id] = []
        answers_store[session_id].append(answer)

        return success_response({
            'answer_id': answer_id,
            'question_id': data['question_id'],
            'submitted_at': answer['submitted_at']
        }, message='Answer submitted successfully')
    except Exception as e:
        return error_response(str(e), 500)


@assessments_bp.route('/sessions/<session_id>/score', methods=['GET'])
def get_score(session_id):
    """获取评分结果"""
    try:
        session = sessions_store.get(session_id)
        
        if not session:
            return error_response('Session not found', 404)
        
        answers = answers_store.get(session_id, [])
        
        # 模拟评分（后续会使用双Agent评分）
        return success_response({
            'session_id': session_id,
            'answered_questions': len(answers),
            'total_questions': session['total_questions'],
            'current_scores': {
                'fluency': 7.5,
                'flexibility': 8.0,
                'originality': 6.5,
                'elaboration': 7.0
            },
            'total_score': 72.5
        })
    except Exception as e:
        return error_response(str(e), 500)


@assessments_bp.route('/sessions/<session_id>/complete', methods=['POST'])
def complete_session(session_id):
    """完成测评 - 使用AI批量评分"""
    try:
        session = sessions_store.get(session_id)

        if not session:
            return error_response('Session not found', 404)

        # 更新会话状态
        session['status'] = 'completed'
        session['end_time'] = datetime.now().isoformat()

        # 生成测评ID
        assessment_id = f"ASM{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # 获取该会话的所有答案
        answers = answers_store.get(session_id, [])
        questions = questions_store.get(session_id, [])
        evaluation_type = session.get('evaluation_type', 'creativity')

        logger.info(f"Evaluating {len(answers)} answers for session {session_id} with type {evaluation_type}")

        question_answer_pairs = []
        for answer in answers:
            question = next((q for q in questions if q['id'] == answer['question_id']), None)
            if question:
                question_answer_pairs.append({
                    'question_id': question['id'],
                    'question_content': question['content'],
                    'answer_content': answer['content']
                })
        question_answer_pairs.sort(key=lambda x: x['question_id'])

        workflow_state = run_assessment_workflow(
            session_id=session_id,
            student_id=session['student_id'],
            student_name=session['student_name'],
            evaluation_type=evaluation_type,
            question_answer_pairs=question_answer_pairs,
        )

        report_payload = workflow_state.get('report_payload') or {}
        portrait_data = workflow_state.get('portrait_data') or {}

        if workflow_state.get('error') and not report_payload:
            logger.error("LangGraph workflow error: %s", workflow_state.get('error'))
            final_scores = {'fluency': 70.0, 'flexibility': 70.0, 'originality': 70.0, 'elaboration': 70.0}
            total_score = 70.0
            answer_details = []
            feedback = {}
            grade_level = 'C'
            portrait_data = {
                'total_dict': final_scores,
                'rating_dict': {k: '中等' for k in final_scores},
                'feedback_dict': {},
                'ready_for_chat': False,
            }
            for pair in question_answer_pairs:
                answer_details.append({
                    'question_id': pair['question_id'],
                    'question_content': pair['question_content'],
                    'answer_content': pair['answer_content'],
                    'scores': total_score,
                    'comments': '评估过程出现问题，使用默认分数'
                })
        else:
            final_scores = report_payload.get('final_scores', {})
            total_score = report_payload.get('total_score', 0)
            answer_details = report_payload.get('answer_details', [])
            feedback = report_payload.get('feedback', {})
            grade_level = report_payload.get('grade_level', 'C')

        logger.info(f"Final scores: {final_scores}, Total: {total_score}")

        # 保存已完成的测评到数据库
        completed_assessment_data = {
            'assessment_id': assessment_id,
            'session_id': session_id,
            'student_id': session['student_id'],
            'student_name': session['student_name'],
            'evaluation_type': session['evaluation_type'],
            'start_time': session['start_time'],
            'end_time': session['end_time'],
            'final_scores': final_scores,  # 各小项评分
            'total_score': total_score,  # 总评分
            'answer_details': answer_details,  # 保存详细评分
            'grade_level': grade_level,  # 等级
            'feedback': feedback,  # 各小项评及总评
            'status': 'completed'
        }

        # 创建数据库记录
        assessment = Assessment.from_dict(completed_assessment_data)
        db.session.add(assessment)
        db.session.commit()

        logger.info(f"Assessment {assessment_id} saved to database")

        # 保存测评结果所需信息
        return success_response({
            'session_id': session_id,
            'assessment_id': assessment_id,
            'status': 'completed',
            'end_time': session['end_time'],
            'final_scores': final_scores,
            'total_score': total_score,
            'answer_details': answer_details,
            'report_url': f'/api/v1/analysis/assessment/{assessment_id}',
            'portrait_data': portrait_data,
            'workflow_ms': workflow_state.get('workflow_ms'),
            'agent_pipeline': ['evaluate_answers', 'generate_report', 'prepare_portrait'],
        }, message='Assessment completed')
    except Exception as e:
        logger.error(f"Error completing session: {str(e)}", exc_info=True)
        return error_response(str(e), 500)


@assessments_bp.route('/history/<student_id>', methods=['GET'])
def get_history(student_id):
    """获取测评历史 - 从数据库返回已完成的测评"""
    try:
        # 从数据库查询该学生的所有已完成测评
        assessments = Assessment.query.filter_by(student_id=student_id).order_by(Assessment.end_time.desc()).all()

        # 转换为字典列表
        student_assessments = [a.to_dict() for a in assessments]

        return success_response({
            'assessments': student_assessments,
            'total': len(student_assessments)
        })
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}", exc_info=True)
        return error_response(str(e), 500)


@assessments_bp.route('/<assessment_id>', methods=['DELETE'])
def delete_assessment(assessment_id):
    """删除测评记录"""
    try:
        # 从数据库查询测评记录
        assessment = Assessment.query.filter_by(assessment_id=assessment_id).first()

        if not assessment:
            return error_response('Assessment not found', 404)

        # 删除记录
        db.session.delete(assessment)
        db.session.commit()

        logger.info(f"Assessment {assessment_id} deleted from database")

        return success_response({
            'assessment_id': assessment_id,
            'message': 'Assessment deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting assessment: {str(e)}", exc_info=True)
        return error_response(str(e), 500)

