import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from flask import request, g

# 导入所有日志组件
from logging_config import EnhancedLogger, log_manager
from log_rotation import LogRotationManager
from log_rotation_config import LogRotationConfig, get_log_rotation_config
from performance_monitoring import PerformanceMonitor, init_performance_monitoring

def initialize_logging_system(
    app_name: str = "topo_system",
    log_directory: str = "logs",
    config_file: str = "log_rotation_config.json",
    enable_performance_monitoring: bool = True,
    enable_log_rotation: bool = True,
    enable_database_logging: bool = True
) -> Dict[str, Any]:
    """
    初始化完整的日志系统
    
    Args:
        app_name: 应用名称
        log_directory: 日志目录
        config_file: 配置文件路径
        enable_performance_monitoring: 是否启用性能监控
        enable_log_rotation: 是否启用日志轮转
        enable_database_logging: 是否启用数据库日志记录
    
    Returns:
        包含所有日志组件的字典
    """
    
    print(f"[{datetime.now()}] 开始初始化日志系统...")
    
    # 确保日志目录存在
    os.makedirs(log_directory, exist_ok=True)
    
    # 1. 初始化日志轮转配置
    print(f"[{datetime.now()}] 初始化日志轮转配置...")
    rotation_config = LogRotationConfig(config_file)
    
    # 验证配置
    validation_results = rotation_config.validate_config()
    if not all(validation_results.values()):
        print(f"[{datetime.now()}] 警告: 日志配置验证失败 - {validation_results}")
    
    # 2. 初始化日志轮转管理器
    log_rotation_manager = None
    if enable_log_rotation:
        print(f"[{datetime.now()}] 初始化日志轮转管理器...")
        log_rotation_manager = LogRotationManager(
            log_base_dir=log_directory,
            config=rotation_config
        )
        
        # 启动日志轮转服务
        try:
            log_rotation_manager.start_rotation_service()
            print(f"[{datetime.now()}] 日志轮转服务已启动")
        except Exception as e:
            print(f"[{datetime.now()}] 警告: 日志轮转服务启动失败 - {e}")
    
    # 3. 初始化性能监控
    performance_monitor = None
    if enable_performance_monitoring:
        print(f"[{datetime.now()}] 初始化性能监控...")
        performance_monitor = init_performance_monitoring(
            log_manager=log_manager,
            app=None  # 将在Flask应用初始化后设置
        )
        print(f"[{datetime.now()}] 性能监控已初始化")
    
    # 4. 初始化数据库日志记录
    if enable_database_logging:
        print(f"[{datetime.now()}] 初始化数据库日志记录...")
        # 数据库日志记录已在EnhancedLogger中集成
        print(f"[{datetime.now()}] 数据库日志记录已初始化")
    
    # 5. 记录系统启动日志
    try:
        log_manager.log_business(
            operation="system_startup",
            details={
                "app_name": app_name,
                "log_directory": log_directory,
                "config_file": config_file,
                "performance_monitoring": enable_performance_monitoring,
                "log_rotation": enable_log_rotation,
                "database_logging": enable_database_logging,
                "initialization_time": datetime.now().isoformat()
            }
        )
        print(f"[{datetime.now()}] 系统启动日志已记录")
    except Exception as e:
        print(f"[{datetime.now()}] 警告: 系统启动日志记录失败 - {e}")
    
    # 6. 返回所有组件
    logging_components = {
        "log_manager": log_manager,
        "rotation_config": rotation_config,
        "log_rotation_manager": log_rotation_manager,
        "performance_monitor": performance_monitor,
        "app_name": app_name,
        "log_directory": log_directory,
        "initialization_time": datetime.now()
    }
    
    print(f"[{datetime.now()}] 日志系统初始化完成")
    
    return logging_components

def setup_flask_logging(app, logging_components: Dict[str, Any]) -> None:
    """
    设置Flask应用的日志记录
    
    Args:
        app: Flask应用实例
        logging_components: 日志组件字典
    """
    
    print(f"[{datetime.now()}] 开始设置Flask日志记录...")
    
    # 获取组件
    log_manager = logging_components.get("log_manager")
    performance_monitor = logging_components.get("performance_monitor")
    
    if not log_manager:
        print(f"[{datetime.now()}] 错误: 日志管理器未初始化")
        return
    
    # 1. 设置请求日志记录
    @app.before_request
    def log_request():
        """记录请求信息"""
        # 跳过 OPTIONS 请求（CORS preflight）
        if request.method == 'OPTIONS':
            return
        try:
            # 获取用户信息
            user_id = None
            if hasattr(app, 'extensions') and 'jwt' in app.extensions:
                from flask_jwt_extended import get_jwt_identity
                try:
                    user_id = get_jwt_identity()
                except:
                    pass
            
            # 记录请求
            log_manager.log_request(
                user_id=user_id,
                action='http_request',
                details={
                    'method': request.method,
                    'url': request.url,
                    'ip': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent', ''),
                    'request_id': request.headers.get('X-Request-ID', '')
                }
            )
            
            # 设置请求开始时间（用于性能监控）
            if performance_monitor:
                from flask import g
                g.request_start_time = datetime.now()
                
        except Exception as e:
            print(f"[{datetime.now()}] 请求日志记录错误: {e}")
    
    # 2. 设置响应日志记录
    @app.after_request
    def log_response(response):
        """记录响应信息"""
        try:
            # 计算响应时间
            response_time = None
            if performance_monitor and hasattr(g, 'request_start_time'):
                response_time = (datetime.now() - g.request_start_time).total_seconds()
                
                # 记录性能指标
                performance_monitor.track_response_time(
                    endpoint=request.endpoint or 'unknown',
                    response_time=response_time,
                    status_code=response.status_code
                )
                
                # 慢请求告警
                slow_threshold = logging_components.get("rotation_config").get_performance_config().get("slow_request_threshold_seconds", 5.0)
                if response_time > slow_threshold:
                    log_manager.log_error(
                        error_type="slow_request",
                        error_message=f"Slow request detected: {response_time:.2f}s",
                        context={
                            "method": request.method,
                            "url": request.url,
                            "response_time": response_time,
                            "status_code": response.status_code
                        }
                    )
                    
                    # 发送告警
                    if performance_monitor:
                        performance_monitor.send_alert(
                            alert_type="slow_request",
                            message=f"Slow request: {request.method} {request.url} took {response_time:.2f}s",
                            severity="warning",
                            context={
                                "response_time": response_time,
                                "threshold": slow_threshold,
                                "url": request.url
                            }
                        )
            
            # 记录响应
            log_manager.log_business(
                operation="response_sent",
                details={
                    "method": request.method,
                    "url": request.url,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "content_length": response.content_length
                }
            )
            
        except Exception as e:
            print(f"[{datetime.now()}] 响应日志记录错误: {e}")
            
        return response
    
    # 3. 设置错误日志记录
    @app.errorhandler(Exception)
    def log_error(error):
        """记录错误信息"""
        try:
            # 记录错误
            log_manager.log_error(
                message=f"Unhandled exception: {type(error).__name__} - {str(error)}",
                exception=str(error),
                request_info={
                    "method": request.method,
                    "url": request.url,
                    "ip": request.remote_addr,
                    "user_agent": request.headers.get('User-Agent', '')
                }
            )
            
            # 性能监控错误计数
            if performance_monitor:
                performance_monitor.log_error(
                    error_type=type(error).__name__,
                    error_message=str(error),
                    context=request.endpoint or 'unknown'
                )
            
        except Exception as e:
            print(f"[{datetime.now()}] 错误日志记录错误: {e}")
    
    print(f"[{datetime.now()}] Flask日志记录设置完成")

def get_system_status(logging_components: Dict[str, Any]) -> Dict[str, Any]:
    """
    获取日志系统状态
    
    Args:
        logging_components: 日志组件字典
    
    Returns:
        系统状态信息
    """
    
    try:
        log_manager = logging_components.get("log_manager")
        rotation_manager = logging_components.get("log_rotation_manager")
        performance_monitor = logging_components.get("performance_monitor")
        rotation_config = logging_components.get("rotation_config")
        
        status = {
            "system_info": {
                "app_name": logging_components.get("app_name"),
                "initialization_time": logging_components.get("initialization_time").isoformat() if logging_components.get("initialization_time") else None,
                "current_time": datetime.now().isoformat(),
                "uptime_seconds": (datetime.now() - logging_components.get("initialization_time")).total_seconds() if logging_components.get("initialization_time") else 0
            },
            "logging_system": {
                "log_manager": log_manager is not None,
                "log_directory": logging_components.get("log_directory"),
                "log_files": rotation_config.get_all_log_files() if rotation_config else []
            },
            "rotation_system": {
                "enabled": rotation_manager is not None,
                "service_running": rotation_manager.running if rotation_manager else False,
                "config_valid": all(rotation_config.validate_config().values()) if rotation_config else False
            },
            "performance_monitoring": {
                "enabled": performance_monitor is not None,
                "metrics_collected": performance_monitor.current_metrics if performance_monitor else {},
                "alerts_sent": len(list(performance_monitor.metrics_history['errors'])) if performance_monitor else 0
            },
            "disk_usage": {
                "log_directory": logging_components.get("log_directory"),
                "total_size_mb": 0,  # 将在后续版本中实现
                "file_count": 0      # 将在后续版本中实现
            }
        }
        
        return status
        
    except Exception as e:
        return {
            "error": f"获取系统状态失败: {str(e)}",
            "current_time": datetime.now().isoformat()
        }

# 全局日志组件实例
logging_system = None

def get_logging_system() -> Optional[Dict[str, Any]]:
    """获取日志系统实例"""
    return logging_system

def init_logging_system(**kwargs) -> Dict[str, Any]:
    """初始化日志系统（全局函数）"""
    global logging_system
    logging_system = initialize_logging_system(**kwargs)
    return logging_system