"""
应用配置
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
basedir = Path(__file__).parent.parent  # backend 目录
load_dotenv(basedir / '.env')
print(f"Loading .env from: {basedir / '.env'}")
print(f"SILICONFLOW_API_KEY loaded: {os.getenv('SILICONFLOW_API_KEY')[:10] if os.getenv('SILICONFLOW_API_KEY') else 'NOT FOUND'}...")

class Config:
    """基础配置"""
    # Flask配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        f'sqlite:///{basedir}/creativity_assessment.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # AI配置
    SILICONFLOW_API_KEY = os.getenv('SILICONFLOW_API_KEY')
    SILICONFLOW_BASE_URL = os.getenv('SILICONFLOW_BASE_URL', 'https://api.siliconflow.cn/v1')
    SILICONFLOW_MODEL_CHAT_A = os.getenv('SILICONFLOW_MODEL_CHAT_A', 'deepseek-ai/DeepSeek-V3')
    SILICONFLOW_MODEL_CHAT_B = os.getenv('SILICONFLOW_MODEL_CHAT_B', 'deepseek-ai/DeepSeek-V3')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', os.getenv('SILICONFLOW_API_KEY', ''))
    
    # 测评配置
    MAX_QUESTIONS = int(os.getenv('MAX_QUESTIONS', 10))
    TIME_LIMIT_MINUTES = int(os.getenv('TIME_LIMIT_MINUTES', 30))
    
    # 应用配置
    APP_NAME = "学生创造力测评系统"
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

