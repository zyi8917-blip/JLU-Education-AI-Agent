"""
Flask应用初始化
"""
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='default'):
    """创建Flask应用实例"""
    app = Flask(__name__)

    # 加载配置
    from app.config import config
    app.config.from_object(config[config_name])

    # 初始化扩展
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    migrate.init_app(app, db)

    # 导入模型（确保模型被注册）
    with app.app_context():
        from app.models import Student
    
    # 注册蓝图
    from app.api import students_bp, assessments_bp, analysis_bp, system_bp, chat_bp, rag_bp, agent_bp
    from app.api.tts import tts_bp
    app.register_blueprint(students_bp, url_prefix='/api/v1/students')
    app.register_blueprint(assessments_bp, url_prefix='/api/v1/assessments')
    app.register_blueprint(analysis_bp, url_prefix='/api/v1/analysis')
    app.register_blueprint(system_bp, url_prefix='/api/v1/system')
    app.register_blueprint(chat_bp, url_prefix='/api/v1/chat')
    app.register_blueprint(rag_bp, url_prefix='/api/v1/rag')
    app.register_blueprint(agent_bp, url_prefix='/api/v1/agent')
    app.register_blueprint(tts_bp, url_prefix='/api/v1/tts')
    
    # 健康检查端点
    @app.route('/api/health')
    def health():
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat()
            }
        })
    
    # 根路径
    @app.route('/')
    def index():
        return jsonify({
            'code': 200,
            'message': 'Welcome to Creativity Assessment System API',
            'data': {
                'version': '1.0.0',
                'docs': '/api/docs'
            }
        })
    
    # 全局错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'code': 404,
            'message': 'Resource not found',
            'timestamp': datetime.now().isoformat()
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'code': 500,
            'message': 'Internal server error',
            'timestamp': datetime.now().isoformat()
        }), 500
    
    return app

