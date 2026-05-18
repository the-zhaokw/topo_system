"""
Flask应用入口模块
重构后的主应用文件，替代原有的enhanced_app.py
"""
import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime

# 导入配置
from config import init_extensions, db, jwt, cors, config_by_name

# 导入模型（确保所有模型都被注册）
from models import *

# 导入工具函数
from utils import sync_time_to_china

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_app(config_name=None):
    """
    应用工厂函数
    
    Args:
        config_name: 配置名称（development/production/testing）
        
    Returns:
        Flask: Flask应用实例
    """
    # 使用环境变量或默认配置
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # 创建Flask应用
    app = Flask(__name__)
    
    # 允许不带尾部斜杠的路由
    app.url_map.strict_slashes = False
    
    # 加载配置
    config_class = config_by_name.get(config_name, config_by_name['default'])
    app.config.from_object(config_class)
    
    # 配置JSON编码
    app.json.ensure_ascii = False
    
    # 自定义JSONProvider
    class CustomJSONProvider(app.json_provider_class):
        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.strftime('%Y-%m-%d %H:%M:%S')
            return super().default(obj)
    
    app.json_provider_class = CustomJSONProvider
    app.json = CustomJSONProvider(app)
    
    # 初始化扩展
    init_extensions(app)
    
    # 注册蓝图（如果有的话）
    register_blueprints(app)
    
    # 注册错误处理
    register_error_handlers(app)
    
    # 注册请求钩子
    register_request_handlers(app)
    
    # 同步时区
    sync_time_to_china()
    
    return app


def register_blueprints(app):
    """
    注册Flask蓝图
    
    Args:
        app: Flask应用实例
    """
    # 这里可以注册各个API蓝图
    # from api.auth import auth_bp
    # from api.projects import projects_bp
    # app.register_blueprint(auth_bp, url_prefix='/api/auth')
    # app.register_blueprint(projects_bp, url_prefix='/api/projects')
    pass


def register_error_handlers(app):
    """
    注册错误处理器
    
    Args:
        app: Flask应用实例
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad Request', 'message': str(error)}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized', 'message': '请先登录'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden', 'message': '权限不足'}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not Found', 'message': '资源不存在'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal Server Error', 'message': '服务器内部错误'}), 500


def register_request_handlers(app):
    """
    注册请求处理器
    
    Args:
        app: Flask应用实例
    """
    @app.after_request
    def after_request(response):
        """请求后处理，添加CORS头"""
        origin = request.headers.get('Origin')
        allowed_origins = app.config.get('CORS_ORIGINS', ["*"])
        
        if origin in allowed_origins or allowed_origins == ["*"]:
            response.headers['Access-Control-Allow-Origin'] = origin if origin else '*'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin'
            response.headers['Access-Control-Max-Age'] = '86400'
        
        return response


# 创建应用实例
app = create_app()


# 静态文件服务
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    """提供上传文件服务"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# 健康检查接口
@app.route('/health')
def health_check():
    """健康检查接口"""
    return jsonify({'status': 'ok', 'message': 'Service is running'})


# 初始化数据库
@app.cli.command('init-db')
def init_db_command():
    """初始化数据库命令"""
    with app.app_context():
        db.create_all()
        print('数据库初始化完成！')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
