"""
Flask扩展初始化模块
集中管理所有Flask扩展的初始化
"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# 初始化扩展（不绑定到应用）
db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()


def init_extensions(app):
    """
    初始化所有Flask扩展
    
    Args:
        app: Flask应用实例
    """
    # 初始化数据库
    db.init_app(app)
    
    # 初始化JWT
    jwt.init_app(app)
    
    # 初始化CORS
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', ["*"]),
            "methods": app.config.get('CORS_METHODS', ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]),
            "allow_headers": app.config.get('CORS_ALLOW_HEADERS', ["Content-Type", "Authorization"]),
            "supports_credentials": False,
            "max_age": app.config.get('CORS_MAX_AGE', 86400),
            "send_wildcard": True,
            "automatic_options": True
        },
        r"/auth/*": {
            "origins": app.config.get('CORS_ORIGINS', ["*"]),
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": app.config.get('CORS_ALLOW_HEADERS', ["Content-Type", "Authorization"]),
            "supports_credentials": False,
            "max_age": app.config.get('CORS_MAX_AGE', 86400)
        },
        r"/uploads/*": {
            "origins": app.config.get('CORS_ORIGINS', ["*"]),
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": app.config.get('CORS_ALLOW_HEADERS', ["Content-Type", "Authorization"]),
            "supports_credentials": False,
            "max_age": app.config.get('CORS_MAX_AGE', 86400)
        }
    })


def get_db_instance():
    """
    获取全局数据库实例
    
    Returns:
        SQLAlchemy: 数据库实例
    """
    return db
