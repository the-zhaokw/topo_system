"""
配置模块
导出配置类和扩展实例
"""
from config.config import Config, DevelopmentConfig, ProductionConfig, TestingConfig, config_by_name
from config.extensions import db, jwt, cors, init_extensions, get_db_instance

__all__ = [
    'Config',
    'DevelopmentConfig',
    'ProductionConfig',
    'TestingConfig',
    'config_by_name',
    'db',
    'jwt',
    'cors',
    'init_extensions',
    'get_db_instance'
]
