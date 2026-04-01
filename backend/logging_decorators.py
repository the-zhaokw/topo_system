import logging
import functools
from datetime import datetime
from flask import request, g, jsonify
import json
import traceback
from logging_config import get_log_manager

def log_function_call(logger_name='app', level='info', include_args=True, include_result=False):
    """函数调用日志装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log_manager = get_log_manager()
            logger = log_manager.get_logger(logger_name)
            
            # 构建函数调用信息
            func_info = f"{func.__module__}.{func.__name__}"
            
            # 记录函数调用
            if include_args:
                log_message = f"Calling {func_info} - args: {args}, kwargs: {kwargs}"
            else:
                log_message = f"Calling {func_info}"
            
            getattr(logger, level)(log_message)
            
            # 记录开始时间
            start_time = datetime.now()
            
            try:
                # 执行函数
                result = func(*args, **kwargs)
                
                # 计算执行时间
                duration = (datetime.now() - start_time).total_seconds() * 1000
                
                # 记录函数返回
                if include_result:
                    log_message = f"Completed {func_info} - Result: {result} - Duration: {duration:.2f}ms"
                else:
                    log_message = f"Completed {func_info} - Duration: {duration:.2f}ms"
                
                getattr(logger, level)(log_message)
                
                # 记录性能日志
                log_manager.log_performance(
                    operation=func_info,
                    duration=duration,
                    memory_usage=0,  # 可以添加内存监控
                    db_queries=0   # 可以添加数据库查询计数
                )
                
                return result
                
            except Exception as e:
                # 记录异常
                duration = (datetime.now() - start_time).total_seconds() * 1000
                log_message = f"Failed {func_info} - Error: {str(e)} - Duration: {duration:.2f}ms"
                logger.error(log_message)
                
                # 记录错误日志
                log_manager.log_error(
                    message=f"Function {func_info} failed",
                    exception=traceback.format_exc()
                )
                
                raise
        
        return wrapper
    return decorator

def log_api_call(func=None, logger_name='app', level='info'):
    """API调用日志装饰器"""
    if func is None:
        return lambda f: log_api_call(f, logger_name, level)
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            log_manager = get_log_manager()
            logger = log_manager.get_logger(logger_name)
            
            func_info = f"{func.__module__}.{func.__name__}"
            
            log_message = f"API Call Start: {func_info} - Method: {request.method} - Path: {request.path}"
            getattr(logger, level)(log_message)
            
            if request.data:
                try:
                    request_data = json.loads(request.data.decode('utf-8'))
                    logger.debug(f"Request Data: {json.dumps(request_data, ensure_ascii=False)}")
                except:
                    logger.debug(f"Request Data: {request.data.decode('utf-8')}")
        except Exception as e:
            pass
        
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            
            try:
                duration = (datetime.now() - start_time).total_seconds() * 1000
                log_message = f"API Call Complete: {func_info} - Status: Success - Duration: {duration:.2f}ms"
                log_manager = get_log_manager()
                logger = log_manager.get_logger(logger_name)
                getattr(logger, level)(log_message)
            except Exception as e:
                pass
            
            return result
            
        except Exception as e:
            try:
                duration = (datetime.now() - start_time).total_seconds() * 1000
                log_message = f"API Call Failed: {func_info} - Error: {str(e)} - Duration: {duration:.2f}ms"
                log_manager = get_log_manager()
                logger = log_manager.get_logger(logger_name)
                logger.error(log_message)
                
                log_manager.log_error(
                    message=f"API {func_info} failed",
                    exception=traceback.format_exc()
                )
            except Exception as log_err:
                pass
            
            raise
    
    return wrapper

def log_database_operation(operation, table=None, record_id=None, user_id=None, details=None):
    """记录数据库操作日志"""
    log_manager = get_log_manager()
    log_manager.log_database(operation, table, record_id, user_id, details)

def log_audit_action(user_id, action, resource_type, resource_id=None, details=None, ip=None):
    """记录审计操作日志"""
    log_manager = get_log_manager()
    log_manager.log_audit(user_id, action, resource_type, resource_id, details, ip)

def log_business_operation(func=None, logger_name='app', level='info'):
    """业务操作日志装饰器"""
    if func is None:
        return lambda f: log_business_operation(f, logger_name, level)
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_info = f"{func.__module__}.{func.__name__}"
        
        try:
            log_manager = get_log_manager()
            logger = log_manager.get_logger(logger_name)
            log_message = f"Business Operation Start: {func_info}"
            getattr(logger, level)(log_message)
        except Exception as e:
            pass
        
        result = func(*args, **kwargs)
        
        try:
            log_manager = get_log_manager()
            logger = log_manager.get_logger(logger_name)
            log_message = f"Business Operation Complete: {func_info}"
            getattr(logger, level)(log_message)
        except Exception as e:
            pass
        
        return result
    
    return wrapper

def log_performance_metric(operation, duration, memory_usage=0, db_queries=0, **kwargs):
    """记录性能指标日志"""
    log_manager = get_log_manager()
    log_manager.log_performance(operation, duration, memory_usage, db_queries, **kwargs)

class ErrorHandler:
    """错误处理类，统一处理异常和错误日志"""
    
    @staticmethod
    def handle_api_error(error, error_code=500, error_type="Internal Error"):
        """处理API错误"""
        log_manager = get_log_manager()
        
        # 收集错误信息
        error_info = {
            'error_type': error_type,
            'error_message': str(error),
            'error_code': error_code,
            'timestamp': datetime.now().isoformat(),
            'path': request.path,
            'method': request.method,
            'remote_addr': request.remote_addr
        }
        
        # 获取用户信息
        username = getattr(g, 'username', 'anonymous')
        user_id = getattr(g, 'user_id', None)
        
        # 记录错误日志
        log_manager.log_error(
            message=f"API Error: {error_type} - {str(error)}",
            exception=traceback.format_exc(),
            request_info={
                'method': request.method,
                'path': request.path,
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', ''),
                'data': request.get_data(as_text=True) if request.data else None
            },
            user_info={
                'username': username,
                'user_id': user_id
            }
        )
        
        # 记录log（如果是权限相关错误）
        if error_code in [403, 401]:
            log_manager.log_audit(
                user_id=user_id,
                action='access_denied',
                resource_type='api',
                resource_id=request.path,
                details=f"Access denied: {str(error)}",
                ip=request.remote_addr
            )
        
        # 返回错误响应
        return jsonify({
            'error': error_type,
            'message': str(error),
            'error_code': error_code,
            'timestamp': datetime.now().isoformat()
        }), error_code
    
    @staticmethod
    def handle_validation_error(errors):
        """处理验证错误"""
        log_manager = get_log_manager()
        
        # 记录验证错误
        log_manager.log_error(
            message=f"Validation Error: {json.dumps(errors, ensure_ascii=False)}",
            request_info={
                'method': request.method,
                'path': request.path,
                'data': request.get_data(as_text=True) if request.data else None
            }
        )
        
        return jsonify({
            'error': 'Validation Error',
            'message': '输入数据验证失败',
            'errors': errors,
            'timestamp': datetime.now().isoformat()
        }), 400
    
    @staticmethod
    def handle_database_error(error, operation=None):
        """处理数据库错误"""
        log_manager = get_log_manager()
        
        # 记录数据库错误
        log_manager.log_database(
            operation=f"ERROR_{operation or 'unknown'}" if operation else "ERROR",
            details=str(error),
            user_id=getattr(g, 'user_id', None)
        )
        
        log_manager.log_error(
            message=f"Database Error: {str(error)}",
            exception=traceback.format_exc()
        )
        
        return jsonify({
            'error': 'Database Error',
            'message': '数据库操作失败',
            'timestamp': datetime.now().isoformat()
        }), 500

# 便捷的错误处理函数
def handle_error(error, error_code=500, error_type="Internal Error"):
    """便捷的错误处理函数"""
    return ErrorHandler.handle_api_error(error, error_code, error_type)

def handle_validation_errors(errors):
    """便捷的验证错误处理函数"""
    return ErrorHandler.handle_validation_error(errors)

def handle_db_error(error, operation=None):
    """便捷的数据库错误处理函数"""
    return ErrorHandler.handle_database_error(error, operation)