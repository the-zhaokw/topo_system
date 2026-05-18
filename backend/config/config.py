"""
应用配置模块
集中管理所有应用配置项
"""
import os
from datetime import timedelta


class Config:
    """应用配置类"""
    
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
    
    # 数据库配置
    _db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'instance', 'topo_system.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{_db_path}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-this')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # JSON配置
    JSON_SORT_KEYS = False
    
    # CORS配置
    CORS_ORIGINS = ["*"]  # 开发环境允许所有来源
    CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    CORS_ALLOW_HEADERS = ["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"]
    CORS_MAX_AGE = 86400


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    # 生产环境应该限制CORS来源
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# 配置映射
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
