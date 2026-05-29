"""
数据验证工具
"""

# 允许的年级选项
VALID_GRADES = [
    '大一', '大二', '大三', '大四',
    '研一', '研二', '研三',
    '博一', '博二', '博三及以上'
]

# 允许的性别选项
VALID_GENDERS = ['男', '女']


def validate_student_data(data):
    """验证学生数据"""
    if not data:
        return False, "数据不能为空"

    # 验证姓名
    if 'name' not in data or not data['name']:
        return False, "姓名不能为空"

    # 验证学号
    if 'student_id' not in data or not data['student_id']:
        return False, "学号不能为空"

    # 验证性别
    if 'gender' not in data or not data['gender']:
        return False, "性别不能为空"

    if data['gender'] not in VALID_GENDERS:
        return False, f"性别必须是 {' 或 '.join(VALID_GENDERS)}"

    # 验证年龄
    if 'age' not in data:
        return False, "年龄不能为空"

    if not isinstance(data['age'], int) or data['age'] < 16 or data['age'] > 100:
        return False, "年龄必须在 16 到 100 之间"

    # 验证年级
    if 'grade' not in data or not data['grade']:
        return False, "年级不能为空"

    if data['grade'] not in VALID_GRADES:
        return False, f"年级必须是以下选项之一：{', '.join(VALID_GRADES)}"

    # 验证学院
    if 'college' not in data or not data['college']:
        return False, "学院不能为空"

    return True, None


def validate_assessment_data(data):
    """验证测评数据"""
    if not data:
        return False, "Data is required"
    
    if 'student_id' not in data or not data['student_id']:
        return False, "Student ID is required"
    
    if 'student_name' not in data or not data['student_name']:
        return False, "Student name is required"
    
    return True, None


def validate_answer_data(data):
    """验证答案数据"""
    if not data:
        return False, "Data is required"
    
    if 'question_id' not in data or not data['question_id']:
        return False, "Question ID is required"
    
    if 'content' not in data or not data['content']:
        return False, "Answer content is required"
    
    return True, None

