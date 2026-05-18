"""
RESTful API for Bug Management System
遵循RESTful设计原则，提供清晰的API接口
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token
import logging

# 延迟导入工具函数以避免模块导入时的数据库查询
def get_workflow_manager():
    from enhanced_app import workflow_manager
    return workflow_manager

def get_send_notifications():
    from enhanced_app import send_notifications
    return send_notifications

# 获取认证蓝图
def get_auth_bp():
    from api.auth import auth_bp
    return auth_bp

def get_create_access_token():
    from enhanced_app import create_access_token
    return create_access_token

# 延迟导入数据库模型以避免循环导入
def get_db_and_models():
    from enhanced_app import db
    from enhanced_app import User
    from enhanced_app import Bug
    from enhanced_app import Project
    from enhanced_app import Comment
    from enhanced_app import Activity
    from enhanced_app import ProjectMember
    from enhanced_app import BugStatus
    from enhanced_app import Priority
    from enhanced_app import Severity
    from enhanced_app import create_audit_log
    from enhanced_app import UserRole
    return db, User, Bug, Project, Comment, Activity, ProjectMember, BugStatus, Priority, Severity, create_audit_log, UserRole

# 创建API蓝图 - 注意：不在模块级别注册子蓝图，而是在 enhanced_app.py 中注册
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 延迟导入API蓝图以避免模块导入时的数据库查询
def get_avatar_bp():
    from api.avatar import avatar_bp
    return avatar_bp

def get_materials_bp():
    from api.materials import materials_bp
    return materials_bp

def get_contracts_bp():
    from api.contracts import contracts_bp
    return contracts_bp

def get_statistics_bp():
    from api.statistics import statistics_bp
    return statistics_bp

def get_bugs_bp():
    from api.bugs import bugs_bp
    return bugs_bp

def get_projects_bp():
    from api.projects import projects_bp
    return projects_bp

def get_users_bp():
    from api.users import users_bp
    return users_bp

def get_notifications_bp():
    from api.notifications import notifications_bp
    return notifications_bp

def get_attendance_bp():
    from api.attendance import attendance_bp
    return attendance_bp

def get_system_bp():
    from api.system import system_bp
    return system_bp

def get_activities_bp():
    from api.activities import activities_bp
    return activities_bp

def get_work_logs_bp():
    from api.work_logs import work_logs_bp
    return work_logs_bp

def get_bug_statistics_bp():
    from api.bug_statistics import bug_statistics_bp
    return bug_statistics_bp

def get_delivery_tracking_bp():
    from api.delivery_tracking import delivery_tracking_bp
    return delivery_tracking_bp

def get_contracts_enhanced_bp():
    from api.contracts_enhanced import contracts_enhanced_bp
    return contracts_enhanced_bp

def get_contracts_statistics_bp():
    from api.contracts_statistics_enhanced import contracts_statistics_bp
    return contracts_statistics_bp

def get_requirements_bp():
    from api.requirements import requirements_bp
    return requirements_bp

def get_test_management_bp():
    from api.test_management import test_management_bp
    return test_management_bp

def get_audit_bp():
    from api.audit import audit_bp
    return audit_bp

def get_search_bp():
    from api.search import search_bp
    return search_bp

def get_performance_bp():
    from api.performance import perf_bp
    return perf_bp

def get_health_bp():
    from api.health import health_bp
    return health_bp

def get_docs_bp():
    from api.docs import api_docs_bp
    return api_docs_bp

def get_export_bp():
    from api.export import export_bp
    return export_bp

def get_todos_bp():
    from api.todos import todos_bp
    return todos_bp

def get_project_logs_bp():
    from api.project_logs import project_logs_bp
    return project_logs_bp

def get_knowledge_bp():
    from api.knowledge import knowledge_bp
    return knowledge_bp

def get_data_import_export_bp():
    from api.data_import_export import data_bp
    return data_bp

def get_monitoring_bp():
    from api.monitoring import monitoring_bp
    return monitoring_bp

def get_risks_bp():
    from api.risks import risks_bp
    return risks_bp

def get_personal_plan_bp():
    from api.personal_plan import personal_plan_bp
    return personal_plan_bp

def require_permission(permission):
    """权限装饰器"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            db, User, Bug, Project, Comment, Activity, ProjectMember, BugStatus, Priority, Severity, create_audit_log, UserRole = get_db_and_models()
            
            current_user_id = get_jwt_identity()
            current_user = User.query.get(int(current_user_id))
            
            if not current_user or not current_user.can(permission):
                return jsonify({'error': '权限不足'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ==================== 用户管理API ====================

@api_bp.route('/roles', methods=['GET'])
@jwt_required()
def get_roles():
    """获取角色列表"""
    db, User, Bug, Project, Comment, Activity, ProjectMember, BugStatus, Priority, Severity, create_audit_log, UserRole = get_db_and_models()
    
    roles = [
        {'value': UserRole.ADMIN.value, 'name': '管理员'},
        {'value': UserRole.USER.value, 'name': '普通用户'},
        {'value': UserRole.HR.value, 'name': '人力资源'},
        {'value': UserRole.DEPARTMENT_MANAGER.value, 'name': '部门经理'},
        {'value': UserRole.DIVISION_LEADER.value, 'name': '部门领导'}
    ]
    
    return jsonify({
        'roles': roles
    })

# 注册头像静态文件路由
import os
from flask import send_from_directory

def get_app():
    from enhanced_app import app
    return app

@api_bp.route('/uploads/<path:filepath>')
def serve_uploads(filepath):
    """提供上传文件的静态访问"""
    app = get_app()
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    return send_from_directory(upload_dir, filepath)
