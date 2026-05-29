"""
学生数据模型
"""
from datetime import datetime
from app import db


class Student(db.Model):
    """学生档案模型"""
    __tablename__ = 'students'

    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 学生信息
    name = db.Column(db.String(100), nullable=False, comment='姓名')
    student_id = db.Column(db.String(50), unique=True, nullable=False, index=True, comment='学号')
    gender = db.Column(db.String(10), nullable=False, comment='性别')
    age = db.Column(db.Integer, nullable=False, comment='年龄')
    grade = db.Column(db.String(50), nullable=False, comment='年级')
    college = db.Column(db.String(200), nullable=False, comment='学院')
    school = db.Column(db.String(200), default='吉林大学', nullable=False, comment='学校')

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间')

    def to_dict(self):
        """转换为字典"""
        return {
            'name': self.name,
            'student_id': self.student_id,
            'gender': self.gender,
            'age': self.age,
            'grade': self.grade,
            'college': self.college,
            'school': self.school,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Student {self.student_id}: {self.name}>'

