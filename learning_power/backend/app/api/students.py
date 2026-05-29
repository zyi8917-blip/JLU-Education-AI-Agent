"""
学生管理API
"""
from flask import request, jsonify
from datetime import datetime
from app.api import students_bp
from app.utils.response import success_response, error_response
from app.utils.validators import validate_student_data, VALID_GRADES, VALID_GENDERS
from app import db
from app.models.student import Student


@students_bp.route('', methods=['GET'])
def get_students():
    """获取学生列表"""
    try:
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 10, type=int)
        grade = request.args.get('grade', None)
        keyword = request.args.get('keyword', None)

        # 构建查询
        query = Student.query

        # 筛选
        if grade:
            query = query.filter(Student.grade == grade)
        if keyword:
            query = query.filter(Student.name.contains(keyword))

        # 分页
        pagination = query.order_by(Student.created_at.desc()).paginate(
            page=page,
            per_page=size,
            error_out=False
        )

        students = [student.to_dict() for student in pagination.items]

        return success_response({
            'students': students,
            'total': pagination.total,
            'page': page,
            'size': size,
            'total_pages': pagination.pages
        })
    except Exception as e:
        return error_response(str(e), 500)


@students_bp.route('', methods=['POST'])
def create_student():
    """创建学生档案"""
    try:
        data = request.get_json()

        # 验证数据
        is_valid, error_msg = validate_student_data(data)
        if not is_valid:
            return error_response(error_msg, 400)

        # 使用用户输入的学号
        student_id = data.get('student_id', '').strip()
        if not student_id:
            return error_response('学号不能为空', 400)

        # 检查学号是否已存在
        existing_student = Student.query.filter_by(student_id=student_id).first()
        if existing_student:
            return error_response('学号已存在，请使用其他学号', 400)

        # 创建学生对象
        student = Student(
            name=data['name'],
            student_id=student_id,
            gender=data['gender'],
            age=data['age'],
            grade=data['grade'],
            college=data['college'],
            school=data.get('school', '吉林大学')
        )

        # 保存到数据库
        db.session.add(student)
        db.session.commit()

        return success_response(student.to_dict(), message='Student created successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@students_bp.route('/<student_id>', methods=['GET'])
def get_student(student_id):
    """获取学生详情"""
    try:
        student = Student.query.filter_by(student_id=student_id).first()

        if not student:
            return error_response('Student not found', 404)

        return success_response(student.to_dict())
    except Exception as e:
        return error_response(str(e), 500)


@students_bp.route('/<student_id>', methods=['PUT'])
def update_student(student_id):
    """更新学生信息"""
    try:
        student = Student.query.filter_by(student_id=student_id).first()

        if not student:
            return error_response('Student not found', 404)

        data = request.get_json()

        # 更新字段
        if 'name' in data:
            student.name = data['name']
        if 'gender' in data:
            student.gender = data['gender']
        if 'age' in data:
            student.age = data['age']
        if 'grade' in data:
            student.grade = data['grade']
        if 'college' in data:
            student.college = data['college']
        if 'school' in data:
            student.school = data['school']

        student.updated_at = datetime.now()

        db.session.commit()

        return success_response(student.to_dict(), message='Student updated successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@students_bp.route('/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    """删除学生"""
    try:
        student = Student.query.filter_by(student_id=student_id).first()

        if not student:
            return error_response('Student not found', 404)

        db.session.delete(student)
        db.session.commit()

        return success_response(None, message='Student deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@students_bp.route('/verify', methods=['POST'])
def verify_student():
    """验证学生是否存在（通过姓名和学号）"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        student_id = data.get('student_id', '').strip()

        if not name or not student_id:
            return error_response('姓名和学号不能为空', 400)

        # 查找学生
        student = Student.query.filter_by(student_id=student_id).first()

        if not student:
            return error_response('未找到该学生档案，请先在学生管理中添加', 404)

        # 验证姓名是否匹配
        if student.name != name:
            return error_response(f'学号 {student_id} 对应的学生姓名是 {student.name}，不是 {name}', 400)

        return success_response(student.to_dict(), message='学生验证成功')
    except Exception as e:
        return error_response(str(e), 500)

@students_bp.route('/options', methods=['GET'])
def get_student_options():
    """获取学生信息的选项列表（年级、性别等）"""
    try:
        return success_response({
            'grades': VALID_GRADES,
            'genders': VALID_GENDERS,
            'default_school': '吉林大学'
        })
    except Exception as e:
        return error_response(str(e), 500)


