"""
统一权限检查工具
=================

提供：
    - require_perm(perm_code): 装饰器，校验细分权限码
    - require_module(module_code): 装饰器，校验大功能模块可见性
    - require_any(*perm_codes): 装饰器，任一权限满足即可
    - require_all(*perm_codes): 装饰器，全部权限满足
    - require_roles(*role_codes): 装饰器，按 UserRole 校验
    - require_admin(): 装饰器，仅系统/职位管理员
    - check_perm(user, perm_code): 函数式检查细分权限
    - check_module(user, module_code): 函数式检查大功能模块
    - filter_query_by_perm(query, model, user, perm_code, owner_field='created_by'):
        根据权限与数据归属，自动收窄 SQLAlchemy 查询

权限模型与现有 User.check_permission() / accessible_modules 保持完全兼容，
不影响已存在接口的行为。
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity


def _load_user():
    """延迟加载 User 模型，避免循环导入。"""
    from enhanced_app import User
    return User


def _get_current_user():
    """获取当前用户对象。"""
    User = _load_user()
    current_user_id = get_jwt_identity()
    if not current_user_id:
        return None
    try:
        return User.query.get(int(current_user_id))
    except Exception:
        return User.query.get(current_user_id)


def is_system_admin(user):
    """是否为系统/职位级管理员（用于超级放行）。"""
    if not user:
        return False
    if getattr(user, 'is_super_admin', False):
        return True
    if getattr(user, 'is_admin', False):
        return True
    try:
        pos = user.get_position_info()
        if pos and (pos.is_admin or pos.is_manager):
            return True
    except Exception:
        pass
    return False


def check_perm(user, perm_code):
    """检查用户是否拥有指定细分权限码（已集成 is_admin 放行）。"""
    if not user or not perm_code:
        return False
    if is_system_admin(user):
        return True
    try:
        return bool(user.check_permission(perm_code))
    except Exception:
        return False


def check_module(user, module_code):
    """检查用户是否可访问指定大功能模块。"""
    if not user or not module_code:
        return False
    if is_system_admin(user):
        return True
    try:
        return bool(user.can_access_module(module_code))
    except Exception:
        return False


def check_any(user, perm_codes):
    return any(check_perm(user, code) for code in perm_codes if code)


def check_all(user, perm_codes):
    return all(check_perm(user, code) for code in perm_codes if code)


def _deny(perm_code, status=403):
    return jsonify({
        'error': '权限不足',
        'code': 'PERMISSION_DENIED',
        'required_permission': perm_code
    }), status


# ---------------------------------------------------------------------------
# 装饰器
# ---------------------------------------------------------------------------
def require_perm(perm_code):
    """细分权限装饰器。"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user = _get_current_user()
            if not user:
                return jsonify({'error': '用户不存在'}), 404
            if not check_perm(user, perm_code):
                return _deny(perm_code)
            return f(*args, **kwargs)
        return wrapper
    return decorator


def require_module(module_code):
    """大功能模块可见性装饰器。"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user = _get_current_user()
            if not user:
                return jsonify({'error': '用户不存在'}), 404
            if not check_module(user, module_code):
                return jsonify({
                    'error': '无该模块的访问权限',
                    'code': 'MODULE_ACCESS_DENIED',
                    'required_module': module_code
                }), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator


def require_any(*perm_codes):
    """任一权限满足即可。"""
    codes = [c for c in perm_codes if c]
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user = _get_current_user()
            if not user:
                return jsonify({'error': '用户不存在'}), 404
            if not check_any(user, codes):
                return _deny('|'.join(codes))
            return f(*args, **kwargs)
        return wrapper
    return decorator


def require_all(*perm_codes):
    """全部权限满足。"""
    codes = [c for c in perm_codes if c]
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user = _get_current_user()
            if not user:
                return jsonify({'error': '用户不存在'}), 404
            if not check_all(user, codes):
                return _deny('&'.join(codes))
            return f(*args, **kwargs)
        return wrapper
    return decorator


def require_roles(*role_codes):
    """按 UserRole 枚举校验（系统保留）。"""
    roles = [r.value if hasattr(r, 'value') else r for r in role_codes]
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user = _get_current_user()
            if not user:
                return jsonify({'error': '用户不存在'}), 404
            if is_system_admin(user):
                return f(*args, **kwargs)
            if not user.role or user.role not in roles:
                return _deny('role:' + '|'.join(roles))
            return f(*args, **kwargs)
        return wrapper
    return decorator


def require_admin():
    """仅系统/职位管理员。"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user = _get_current_user()
            if not user:
                return jsonify({'error': '用户不存在'}), 404
            if not is_system_admin(user):
                return jsonify({'error': '需要管理员权限', 'code': 'ADMIN_REQUIRED'}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator


def require_self_or_admin(id_arg='user_id', id_kwarg=None):
    """仅允许访问自己或管理员（多用于按 user_id 操作的接口）。"""
    arg_name = id_kwarg or id_arg
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user = _get_current_user()
            if not user:
                return jsonify({'error': '用户不存在'}), 404
            if is_system_admin(user):
                return f(*args, **kwargs)
            target_id = kwargs.get(arg_name)
            try:
                target_id = int(target_id) if target_id is not None else None
            except (TypeError, ValueError):
                target_id = None
            if target_id is None or target_id != user.id:
                return _deny('self_or_admin')
            return f(*args, **kwargs)
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# 数据级过滤辅助
# ---------------------------------------------------------------------------
def filter_query_by_perm(query, model, user, perm_code,
                          owner_fields=('created_by', 'reporter_id', 'owner_id',
                                        'user_id', 'submitted_by', 'assigned_to')):
    """根据数据级权限与归属字段，自动收窄查询。

    规则：
        - 系统管理员 / 拥有 perm_code -> 返回原 query
        - 否则将 query 限制在 owner_fields 命中当前用户 ID 的记录
        - 如果模型没有任何 owner 字段，添加一个始终为 False 的条件（结果为空）

    Args:
        query: SQLAlchemy Query 对象
        model: 对应 ORM 模型
        user: 当前用户
        perm_code: 查看全部需要的权限码
        owner_fields: 可选的所有权字段集合

    Returns:
        SQLAlchemy Query（已被收窄）
    """
    from sqlalchemy import or_

    if not user:
        # 未登录返回空结果
        return query.filter(__import__('sqlalchemy').false())

    if check_perm(user, perm_code) or is_system_admin(user):
        return query

    field_names = {c.key for c in model.__table__.columns}
    owner_cols = []
    for name in owner_fields:
        if name in field_names:
            owner_cols.append(getattr(model, name))
    if not owner_cols:
        # 没有任何归属字段：拒绝查看他人数据
        from sqlalchemy import false as _false
        return query.filter(_false())

    return query.filter(or_(*[col == user.id for col in owner_cols]))


__all__ = [
    'is_system_admin',
    'check_perm',
    'check_module',
    'check_any',
    'check_all',
    'require_perm',
    'require_module',
    'require_any',
    'require_all',
    'require_roles',
    'require_admin',
    'require_self_or_admin',
    'filter_query_by_perm',
]
