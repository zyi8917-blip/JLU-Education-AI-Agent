"""
测评记录模型
"""
from datetime import datetime
from app import db
import json


class Assessment(db.Model):
    """测评记录模型"""
    __tablename__ = 'assessments'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    assessment_id = db.Column(db.String(100), unique=True, nullable=False, index=True, comment='测评ID')
    session_id = db.Column(db.String(100), nullable=False, comment='会话ID')
    student_id = db.Column(db.String(50), nullable=False, index=True, comment='学号')
    student_name = db.Column(db.String(100), nullable=False, comment='学生姓名')
    evaluation_type = db.Column(db.String(50), nullable=False, comment='测评类型')
    
    # 时间信息
    start_time = db.Column(db.DateTime, nullable=False, comment='开始时间')
    end_time = db.Column(db.DateTime, nullable=False, comment='结束时间')
    
    # 评分信息（存储为JSON字符串）
    final_scores = db.Column(db.Text, nullable=False, comment='各维度评分（JSON）')
    total_score = db.Column(db.Float, nullable=False, comment='总分')
    grade_level = db.Column(db.String(10), nullable=False, comment='等级评定')
    
    # 详细信息（存储为JSON字符串）
    answer_details = db.Column(db.Text, nullable=True, comment='答案详情（JSON）')
    feedback = db.Column(db.Text, nullable=True, comment='反馈信息（JSON）')
    
    # 状态
    status = db.Column(db.String(20), default='completed', nullable=False, comment='状态')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'assessment_id': self.assessment_id,
            'session_id': self.session_id,
            'student_id': self.student_id,
            'student_name': self.student_name,
            'evaluation_type': self.evaluation_type,
            'start_time': self.start_time.isoformat() if isinstance(self.start_time, datetime) else self.start_time,
            'end_time': self.end_time.isoformat() if isinstance(self.end_time, datetime) else self.end_time,
            'final_scores': json.loads(self.final_scores) if isinstance(self.final_scores, str) else self.final_scores,
            'total_score': self.total_score,
            'grade_level': self.grade_level,
            'answer_details': json.loads(self.answer_details) if self.answer_details and isinstance(self.answer_details, str) else self.answer_details,
            'feedback': json.loads(self.feedback) if self.feedback and isinstance(self.feedback, str) else self.feedback,
            'status': self.status,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
    
    @staticmethod
    def from_dict(data):
        """从字典创建对象"""
        # 处理时间字段
        start_time = data.get('start_time')
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        
        end_time = data.get('end_time')
        if isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        # 处理JSON字段
        final_scores = data.get('final_scores')
        if isinstance(final_scores, dict):
            final_scores = json.dumps(final_scores, ensure_ascii=False)
        
        answer_details = data.get('answer_details')
        if isinstance(answer_details, (dict, list)):
            answer_details = json.dumps(answer_details, ensure_ascii=False)
        
        feedback = data.get('feedback')
        if isinstance(feedback, dict):
            feedback = json.dumps(feedback, ensure_ascii=False)
        
        return Assessment(
            assessment_id=data.get('assessment_id'),
            session_id=data.get('session_id'),
            student_id=data.get('student_id'),
            student_name=data.get('student_name'),
            evaluation_type=data.get('evaluation_type'),
            start_time=start_time,
            end_time=end_time,
            final_scores=final_scores,
            total_score=data.get('total_score', 0),
            grade_level=data.get('grade_level', 'C'),
            answer_details=answer_details,
            feedback=feedback,
            status=data.get('status', 'completed')
        )
    
    def __repr__(self):
        return f'<Assessment {self.assessment_id} - {self.student_name}>'

