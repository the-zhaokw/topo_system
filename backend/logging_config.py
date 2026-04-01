import logging
import logging.handlers
import os
from datetime import datetime
from flask import request, g
import json

class EnhancedLogger:
    """增强型日志记录器，提供完整的系统日志功能"""
    
    def __init__(self, app=None):
        self.app = app
        self.loggers = {}
        self.setup_complete = False
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """初始化日志系统"""
        if self.setup_complete:
            return
            
        self.app = app
        self.setup_log_directory()
        self.configure_loggers()
        self.setup_complete = True
        
        # 将日志记录器注册到应用上下文
        app.logger_manager = self
    
    def setup_log_directory(self):
        """设置日志目录结构"""
        base_log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        
        # 创建主要日志目录
        self.log_dirs = {
            'main': base_log_dir,
            'requests': os.path.join(base_log_dir, 'requests'),
            'errors': os.path.join(base_log_dir, 'errors'),
            'audit': os.path.join(base_log_dir, 'audit'),
            'performance': os.path.join(base_log_dir, 'performance'),
            'business': os.path.join(base_log_dir, 'business')
        }
        
        for log_dir in self.log_dirs.values():
            os.makedirs(log_dir, exist_ok=True)
    
    def configure_loggers(self):
        """配置所有日志记录器"""
        # 主应用日志记录器
        self.loggers['app'] = self.create_logger('app', 'enhanced_app.log', level=logging.INFO)
        
        # 请求日志记录器
        self.loggers['requests'] = self.create_logger('requests', 'requests.log', level=logging.INFO)
        
        # 错误日志记录器
        self.loggers['errors'] = self.create_logger('errors', 'errors.log', level=logging.ERROR)
        
        # log记录器
        self.loggers['audit'] = self.create_logger('audit', 'audit.log', level=logging.INFO)
        
        # 性能日志记录器
        self.loggers['performance'] = self.create_logger('performance', 'performance.log', level=logging.INFO)
        
        # 业务逻辑日志记录器
        self.loggers['business'] = self.create_logger('business', 'business.log', level=logging.INFO)
        
        # 数据库操作日志记录器
        self.loggers['database'] = self.create_logger('database', 'database.log', level=logging.INFO)
    
    def create_logger(self, name, filename, level=logging.INFO, max_bytes=10*1024*1024, backup_count=5):
        """创建并配置一个日志记录器"""
        logger = logging.getLogger(f'enhanced_{name}')
        logger.setLevel(level)
        
        # 清除现有处理器
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # 文件处理器（带轮转）
        log_path = os.path.join(self.log_dirs.get(name, self.log_dirs['main']), filename)
        file_handler = logging.handlers.RotatingFileHandler(
            log_path, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        
        # 格式化器
        if name == 'requests':
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(username)s - %(ip)s - "%(method)s %(path)s" - %(status_code)s - %(duration)sms'
            )
        elif name == 'audit':
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - USER:%(user_id)s - ACTION:%(action)s - RESOURCE:%(resource_type)s - ID:%(resource_id)s - DETAILS:%(details)s - IP:%(ip)s'
            )
        elif name == 'performance':
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(operation)s - DURATION:%(duration)sms - MEMORY:%(memory_usage)sMB - DB_QUERIES:%(db_queries)s'
            )
        elif name == 'errors':
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s\nEXCEPTION:\n%(exception_info)s\nREQUEST:\n%(request_info)s\nUSER:\n%(user_info)s'
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def log_request(self, user_id=None, action=None, details=None, username=None, ip=None, method=None, path=None, status_code=None, duration=None, user_agent=None):
        """记录HTTP请求日志
        
        支持两种调用方式：
        1. 标准HTTP请求日志：username, ip, method, path, status_code, duration, user_agent
        2. 业务请求日志：user_id, action, details
        """
        # 如果是标准HTTP请求日志格式
        if username is not None or ip is not None or method is not None:
            extra = {
                'username': username or 'anonymous',
                'ip': ip or 'unknown',
                'method': method or 'UNKNOWN',
                'path': path or 'unknown',
                'status_code': status_code or 0,
                'duration': duration or 0
            }
            self.loggers['requests'].info('', extra=extra)
        
        # 如果是业务请求日志格式（转换为log）
        elif user_id is not None and action is not None:
            self.log_audit(
                user_id=user_id,
                action=action,
                resource_type='request',
                details=details,
                ip=ip
            )
        
        # 如果只有user_id，记录为匿名请求
        elif user_id is not None:
            extra = {
                'username': f'user_{user_id}',
                'ip': ip or 'unknown',
                'method': method or 'UNKNOWN',
                'path': path or 'unknown',
                'status_code': status_code or 0,
                'duration': duration or 0
            }
            self.loggers['requests'].info('', extra=extra)
    
    def log_error(self, message, exception=None, request_info=None, user_info=None):
        """记录错误日志"""
        extra = {
            'exception_info': str(exception) if exception else 'None',
            'request_info': json.dumps(request_info, ensure_ascii=False) if request_info else 'None',
            'user_info': json.dumps(user_info, ensure_ascii=False) if user_info else 'None'
        }
        
        # 检查errors日志记录器是否存在
        if 'errors' in self.loggers and self.loggers['errors']:
            self.loggers['errors'].error(message, extra=extra)
        else:
            # 如果errors日志记录器不存在，使用默认的日志记录器
            import logging
            logger = logging.getLogger('enhanced_errors')
            # 确保日志记录器有处理器
            if not logger.handlers:
                logger.setLevel(logging.ERROR)
                console_handler = logging.StreamHandler()
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                console_handler.setFormatter(formatter)
                logger.addHandler(console_handler)
            
            # 使用简单的消息格式，避免格式化字段错误
            logger.error(f"Error: {message} - Exception: {extra['exception_info']}")
    
    def log_audit(self, user_id, action, resource_type, resource_id=None, details=None, ip=None):
        """记录log"""
        extra = {
            'user_id': user_id or 'unknown',
            'action': action,
            'resource_type': resource_type,
            'resource_id': resource_id or 'none',
            'details': details or '',
            'ip': ip or 'unknown'
        }
        
        self.loggers['audit'].info('', extra=extra)
    
    def log_performance(self, operation, duration, memory_usage=0, db_queries=0, **kwargs):
        """记录性能日志"""
        extra = {
            'operation': operation,
            'duration': duration,
            'memory_usage': memory_usage,
            'db_queries': db_queries
        }
        extra.update(kwargs)
        
        # 检查performance日志记录器是否存在
        if 'performance' in self.loggers and self.loggers['performance']:
            self.loggers['performance'].info('', extra=extra)
        else:
            # 如果performance日志记录器不存在，使用默认的日志记录器
            import logging
            logger = logging.getLogger('enhanced_performance')
            # 确保日志记录器有处理器
            if not logger.handlers:
                logger.setLevel(logging.INFO)
                console_handler = logging.StreamHandler()
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                console_handler.setFormatter(formatter)
                logger.addHandler(console_handler)
            
            # 使用简单的消息格式，避免格式化字段错误
            logger.info(f"Performance: {operation} - {duration}ms - Memory: {memory_usage}MB - DB Queries: {db_queries}")
    
    def log_business(self, operation, user_id=None, project_id=None, details=None, level='info', current_user_id=None):
        """记录业务逻辑日志"""
        # 兼容 current_user_id 参数
        if current_user_id is not None and user_id is None:
            user_id = current_user_id
        
        message = f"{operation}"
        if user_id:
            message += f" - USER:{user_id}"
        if project_id:
            message += f" - PROJECT:{project_id}"
        if details:
            message += f" - {details}"
        
        # 检查loggers字典是否已初始化，以及是否包含'business'键
        if hasattr(self, 'loggers') and 'business' in self.loggers:
            getattr(self.loggers['business'], level)(message)
        else:
            # 如果loggers字典未初始化，使用默认的日志记录器
            import logging
            logger = logging.getLogger('enhanced_business')
            getattr(logger, level)(message)
    
    def log_database(self, operation, table=None, record_id=None, user_id=None, details=None):
        """记录数据库操作日志"""
        message = f"DATABASE {operation}"
        if table:
            message += f" - TABLE:{table}"
        if record_id:
            message += f" - ID:{record_id}"
        if user_id:
            message += f" - USER:{user_id}"
        if details:
            message += f" - {details}"
        
        self.loggers['database'].info(message)
    
    def get_logger(self, name='app'):
        """获取指定的日志记录器"""
        if name in self.loggers:
            return self.loggers[name]
        elif 'app' in self.loggers:
            return self.loggers['app']
        else:
            # 如果'app'日志记录器也不存在，创建一个临时的控制台日志记录器
            temp_logger = logging.getLogger('temp_app_logger')
            if not temp_logger.handlers:
                temp_logger.setLevel(logging.INFO)
                console_handler = logging.StreamHandler()
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                console_handler.setFormatter(formatter)
                temp_logger.addHandler(console_handler)
            return temp_logger

# 全局日志管理器实例
log_manager = EnhancedLogger()

def get_log_manager():
    """获取日志管理器实例"""
    # 如果日志管理器尚未配置，尝试使用默认配置
    if not log_manager.setup_complete:
        # 尝试从Flask应用获取配置
        from flask import current_app
        try:
            if current_app:
                log_manager.init_app(current_app)
                return log_manager
        except Exception as e:
            print(f"无法从Flask应用获取配置: {e}")
            # 继续执行默认配置
        
        # 如果无法获取Flask应用，使用默认配置
        import logging
        import os
        
        # 设置日志目录结构
        base_log_dir = os.path.join(os.getcwd(), 'logs')
        
        # 创建主要日志目录
        log_manager.log_dirs = {
            'main': base_log_dir,
            'requests': os.path.join(base_log_dir, 'requests'),
            'errors': os.path.join(base_log_dir, 'errors'),
            'audit': os.path.join(base_log_dir, 'audit'),
            'performance': os.path.join(base_log_dir, 'performance'),
            'business': os.path.join(base_log_dir, 'business')
        }
        
        # 创建所有日志目录
        for log_dir in log_manager.log_dirs.values():
            os.makedirs(log_dir, exist_ok=True)
        
        # 配置默认日志记录器
        log_manager.configure_loggers()
        log_manager.setup_complete = True
    
    return log_manager

def setup_request_logging(app):
    """设置请求日志记录"""
    
    @app.before_request
    def before_request():
        """记录请求开始时间"""
        # 跳过 OPTIONS 请求（CORS preflight）
        if request.method == 'OPTIONS':
            return None
            
        g.start_time = datetime.now()
        g.request_id = str(uuid.uuid4())
        
        # 获取用户信息
        username = 'anonymous'
        try:
            from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
            if verify_jwt_in_request(False):
                user_id = get_jwt_identity()  # Fix: Call the function instead of passing it
                if user_id:
                    from enhanced_app import User
                    user = User.query.get(user_id)
                    username = user.username if user else f'user_{user_id}'
        except:
            pass
        
        g.username = username
    
    @app.after_request
    def after_request(response):
        """记录请求完成信息"""
        if hasattr(g, 'start_time'):
            duration = (datetime.now() - g.start_time).total_seconds() * 1000
            username = getattr(g, 'username', 'anonymous')
            
            log_manager.log_request(
                username=username,
                ip=request.remote_addr,
                method=request.method,
                path=request.path,
                status_code=response.status_code,
                duration=int(duration),
                user_agent=request.headers.get('User-Agent', '')
            )
        
        return response

def setup_error_logging(app):
    """设置错误日志记录"""
    
    @app.errorhandler(Exception)
    def handle_error(error):
        """记录未处理的异常"""
        import traceback
        
        # 收集请求信息
        request_info = {
            'method': request.method,
            'path': request.path,
            'remote_addr': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'data': request.get_data(as_text=True) if request.data else None
        }
        
        # 收集用户信息
        user_info = {
            'username': getattr(g, 'username', 'anonymous'),
            'user_id': getattr(g, 'user_id', None)
        }
        
        # 记录错误
        log_manager.log_error(
            message=f"Unhandled exception: {str(error)}",
            exception=traceback.format_exc(),
            request_info=request_info,
            user_info=user_info
        )
        
        # 返回错误响应
        return jsonify({'error': 'Internal server error'}), 500