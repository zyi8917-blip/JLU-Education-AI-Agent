"""
统一响应格式
"""
from flask import jsonify
from datetime import datetime


def success_response(data=None, message='success', code=200):
    """成功响应"""
    response = {
        'code': code,
        'message': message,
        'data': data,
        'timestamp': datetime.now().isoformat()
    }
    return jsonify(response), code


def error_response(message='error', code=400, error=None):
    """错误响应"""
    response = {
        'code': code,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    if error:
        response['error'] = error
    return jsonify(response), code

