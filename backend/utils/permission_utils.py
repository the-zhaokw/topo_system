"""
权限处理工具模块
提供权限检查相关的装饰器和函数
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity


def require_permission(permission_name):
    """
    权限检查装饰器
    检查当前用户是否具有指定权限
    
    Args:
        permission_name: 权限名称
        
    Returns:
        decorator: 装饰器函数
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            if not current_user_id:
                return jsonify({'error': '未登录'}), 401
            
            from models import User
            user = User.query.get(current_user_id)
            if not user or not user.has_permission(permission_name):
                return jsonify({'error': '权限不足'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_login(f):
    """
    登录检查装饰器
    检查用户是否已登录
    
    Args:
        f: 被装饰的函数
        
    Returns:
        function: 装饰后的函数
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({'error': '未登录'}), 401
        return f(*args, **kwargs)
    return decorated_function


def require_admin(f):
    """
    管理员权限检查装饰器
    检查用户是否为管理员
    
    Args:
        f: 被装饰的函数
        
    Returns:
        function: 装饰后的函数
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({'error': '未登录'}), 401
        
        from models import User
        user = User.query.get(current_user_id)
        if not user or not user.is_system_admin():
            return jsonify({'error': '需要管理员权限'}), 403
        
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """
    获取当前登录用户
    
    Returns:
        User: 当前用户对象，如果未登录则返回None
    """
    current_user_id = get_jwt_identity()
    if not current_user_id:
        return None
    
    from models import User
    return User.query.get(current_user_id)


def check_user_permission(user, permission):
    """
    检查用户是否有指定权限
    
    Args:
        user: 用户对象
        permission: 权限名称
        
    Returns:
        bool: 是否有权限
    """
    if not user:
        return False
    return user.has_permission(permission)
