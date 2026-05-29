#!/usr/bin/env python3
"""
Flask应用启动脚本
"""
import os
from app import create_app, db

# 创建应用实例
env = os.getenv('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    # 创建数据库表
    with app.app_context():
        db.create_all()
        print("[ok] database tables ready")
    
    # 启动应用
    print("[start] Flask application")
    print(f"[url] http://{app.config['HOST']}:{app.config['PORT']}")
    print(f"[env] {env}")
    print(f"[db] {app.config['SQLALCHEMY_DATABASE_URI']}")
    print("=" * 50)
    
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )

