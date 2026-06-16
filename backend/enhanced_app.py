from flask import Flask, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from flask_cors import CORS
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import logging
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from functools import wraps

# 从 config.extensions 导入 db 和 jwt，确保使用统一的实例
from config.extensions import db, jwt, init_extensions

CHINA_TZ = ZoneInfo('Asia/Shanghai')

def now_china():
    """获取中国时区(UTC+8)的当前时间"""
    return datetime.now(CHINA_TZ)

def utcnow():
    """获取中国时区当前时间（兼容原有 utcnow 用法）"""
    return datetime.now(CHINA_TZ)

def sync_time_to_china():
    """同步时间到中国时区 (UTC+8)"""
    try:
        current_time = now_china()
        logging.info(f"时间已同步到中国时区 (UTC+8)，当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        logging.warning(f"时间同步设置失败: {e}")

sync_time_to_china()

# 导入枚举和工具
# 移除循环导入，改为本地定义UserRole
# from utils import init_logging_system, setup_flask_logging

# 创建Flask应用
app = Flask(__name__)

# 允许不带尾部斜杠的路由（解决CORS预检请求重定向问题）
app.url_map.strict_slashes = False

# 配置应用
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
# 使用绝对路径避免工作目录问题
_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'topo_system.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite:///{_db_path}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-this')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['JSON_SORT_KEYS'] = False
app.json.ensure_ascii = False

class CustomJSONProvider(app.json_provider_class):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(obj)

app.json_provider_class = CustomJSONProvider
app.json = CustomJSONProvider(app)

# 配置静态文件服务用于头像等上传文件
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    from flask import send_from_directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 注意：db 和 jwt 已从 config.extensions 导入，init_extensions 函数也从该模块导入

# 配置CORS - 更全面的CORS配置
cors = CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],  # 开发环境允许所有来源
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
        "supports_credentials": False,  # 允许所有来源时关闭 credentials
        "max_age": 86400,
        "send_wildcard": True,
        "automatic_options": True
    },
    r"/auth/*": {
        "origins": ["*"],  # 开发环境允许所有来源
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
        "supports_credentials": False,  # 允许所有来源时关闭 credentials
        "max_age": 86400
    },
    r"/uploads/*": {
        "origins": ["*"],  # 开发环境允许所有来源
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
        "supports_credentials": False,  # 允许所有来源时关闭 credentials
        "max_age": 86400
    }
})

# 手动添加CORS headers to ensure they're always present
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    allowed_origins = ["*"]  # 开发环境允许所有来源

    if origin in allowed_origins or allowed_origins == ["*"]:
        response.headers['Access-Control-Allow-Origin'] = origin if origin else '*'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin'
        response.headers['Access-Control-Max-Age'] = '86400'

    return response

# 全局数据库实例获取函数
def get_db_instance():
    """获取全局数据库实例"""
    return db

# 定义UserRole枚举（临时定义，将在后续代码中重新定义）
# class UserRole:
#     """用户角色枚举"""
#     ADMIN = "admin"
#     PROJECT_MANAGER = "project_manager"
#     DEVELOPER = "developer"
#     TESTER = "tester"
#     HR = "hr"
#     DIVISION_LEADER = "division_leader"

# 直接在enhanced_app.py中定义所有模型类，避免循环导入和表定义冲突
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum, Float, Date, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

# 定义枚举类（在模块级别定义，以便其他模块可以导入）
class UserRole(enum.Enum):
    """用户角色枚举 - 简化角色层级"""
    ADMIN = "admin"
    MANAGER = "manager"
    PROJECT_MANAGER = "project_manager"
    TEST_ENGINEER = "test_engineer"
    SOFTWARE_ENGINEER = "software_engineer"
    USER = "user"
    HR = "hr"
    DEPARTMENT_MANAGER = "department_manager"

    @classmethod
    def _missing_(cls, value):
        """Handle case-insensitive enum matching"""
        if isinstance(value, str):
            # Try case-insensitive matching
            for member in cls:
                if member.value == value.lower():
                    return member
        # If no match found, let the default behavior take over
        return super()._missing_(value)

class ProjectStatus(enum.Enum):
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    
    @classmethod
    def _missing_(cls, value):
        """Handle case-insensitive enum matching"""
        if isinstance(value, str):
            for member in cls:
                if member.value == value.lower():
                    return member
        return super()._missing_(value)

class AttendanceStatus(enum.Enum):
    """考勤状态枚举"""
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EARLY_LEAVE = "early_leave"
    LEAVE = "leave"
    BUSINESS_TRIP = "business_trip"
    OVERTIME = "overtime"
    MISSING = "missing"
    
    @classmethod
    def _missing_(cls, value):
        """Handle case-insensitive enum matching"""
        if isinstance(value, str):
            for member in cls:
                if member.value == value.lower():
                    return member
        return super()._missing_(value)

class ApprovalStatus(enum.Enum):
    """审批状态枚举"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    
    @classmethod
    def _missing_(cls, value):
        """Handle case-insensitive enum matching"""
        if isinstance(value, str):
            for member in cls:
                if member.value == value.lower():
                    return member
        return super()._missing_(value)

class BugStatus(enum.Enum):
    """Bug 状态枚举"""
    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    FIXED = "fixed"
    RESOLVED = "resolved"
    VERIFIED = "verified"
    CLOSED = "closed"
    REOPENED = "reopened"
    REJECTED = "rejected"
    OPEN = "open"
    
    @classmethod
    def _missing_(cls, value):
        """Handle case-insensitive enum matching"""
        if isinstance(value, str):
            for member in cls:
                if member.value == value.lower():
                    return member
        return super()._missing_(value)

class Priority(enum.Enum):
    """优先级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    
    @classmethod
    def _missing_(cls, value):
        """Handle case-insensitive enum matching"""
        if isinstance(value, str):
            for member in cls:
                if member.value == value.lower():
                    return member
        return super()._missing_(value)

class Severity(enum.Enum):
    """严重程度枚举"""
    TRIVIAL = "trivial"
    MINOR = "minor"
    MAJOR = "major"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    BLOCKER = "blocker"
    
    @classmethod
    def _missing_(cls, value):
        """Handle case-insensitive enum matching"""
        if isinstance(value, str):
            for member in cls:
                if member.value == value.lower():
                    return member
        return super()._missing_(value)

# 定义User模型（在模块级别定义）
class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    salt = Column(String(32), nullable=False)  # 添加salt字段，设置为非空
    role = Column(String(50), default=UserRole.USER.value, nullable=True)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)  # 用户是否激活
    first_name = Column(String(50))  # 名
    last_name = Column(String(50))  # 姓
    department = Column(String(100))
    position = Column(String(100))
    phone = Column(String(20))  # 保留原字段，用于向后兼容
    employee_id = Column(String(50))  # 工号
    company_phone = Column(String(20))  # 公司电话
    mobile_phone = Column(String(20))  # 手机号码
    birthday = Column(DateTime)  # 生日
    gender = Column(String(20))  # 性别
    work_language = Column(String(50))  # 工作语言
    avatar = Column(String(255))  # 头像
    status = Column(String(20), default='online')  # 用户设置的状态: online, busy, away, offline
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)  # 记录上次登录时间
    last_activity = Column(DateTime)  # 记录最后活动时间，用于判断用户是否在线
    email_notification_enabled = Column(Boolean, default=True)  # 是否启用邮箱通知
    email_on_bug_assigned = Column(Boolean, default=True)  # Bug分配时邮件通知
    email_on_bug_closed = Column(Boolean, default=True)  # Bug关闭时邮件通知
    custom_permissions = Column(Text, default='{}')  # 用户自定义权限（JSON格式）
    is_super_admin = Column(Boolean, default=False)  # 是否为系统管理员（拥有所有系统权限，不可被修改）
    accessible_modules = Column(Text, default=None)  # 用户可见的大功能模块编码列表（JSON 数组），空表示使用系统默认

    # 关系
    projects = relationship("ProjectMember", back_populates="user", cascade="all, delete-orphan")
    
    def set_password(self, password):
        """设置密码哈希"""
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
    
    def get_position_info(self):
        """获取用户的职位信息"""
        if not self.position:
            return None
        return Position.query.filter_by(name=self.position).first()

    def is_system_admin(self):
        """是否为系统管理员（可查看所有部门）

        系统管理员包括：
        1. 系统管理员（is_super_admin=True）- 拥有所有系统权限
        2. 管理员用户（is_admin=True）
        3. 拥有管理员职位的用户（Position.is_admin=True）
        4. 拥有经理职位的用户（Position.is_manager=True）
        """
        if self.is_super_admin:
            return True
        if self.is_admin:
            return True
        position_info = self.get_position_info()
        if position_info:
            return position_info.is_admin or position_info.is_manager
        return False

    def is_department_manager(self):
        """是否为部门经理（可查看自己部门的成员）"""
        position_info = self.get_position_info()
        return position_info is not None and position_info.is_manager

    def is_admin_position(self):
        """是否为管理员职位（拥有管理权限但不是系统管理员）"""
        position_info = self.get_position_info()
        return position_info is not None and position_info.is_admin

    def has_management_permission(self):
        """是否拥有管理权限（系统管理员或管理员职位或部门经理）"""
        if self.is_super_admin:
            return True
        position_info = self.get_position_info()
        if position_info:
            return position_info.is_admin or position_info.is_manager
        return False

    def has_permission(self, required_role):
        """检查用户权限 - 基于职位"""
        if self.is_super_admin:
            return True

        position_info = self.get_position_info()
        if position_info:
            if position_info.is_admin:
                return True
            if position_info.is_manager:
                return True
            return False

        return False

    def can(self, permission):
        """检查用户是否具有特定权限 - 综合考虑职位权限和自定义额外/限制权限"""
        return self.check_permission(permission)

    def get_custom_permissions(self):
        """获取用户的自定义权限"""
        import json
        if not self.custom_permissions:
            return {}
        try:
            return json.loads(self.custom_permissions)
        except:
            return {}

    def set_custom_permissions(self, permissions_dict):
        """设置用户的自定义权限"""
        import json
        self.custom_permissions = json.dumps(permissions_dict)

    def check_permission(self, permission_code):
        """综合检查用户是否有特定权限（结合职位权限和自定义权限）- 完全基于职位"""
        if self.is_super_admin:
            return True

        position_info = self.get_position_info()
        if position_info:
            if position_info.is_admin or position_info.is_manager:
                return True

            import json
            try:
                perms = json.loads(position_info.permissions) if position_info.permissions else []
                if permission_code in perms:
                    return True
            except:
                pass

        custom_perms = self.get_custom_permissions()
        if permission_code in custom_perms.get('allowed', []):
            return True

        if permission_code in custom_perms.get('denied', []):
            return False

        return False

    def get_online_status(self):
        """获取用户的实际在线状态
        
        逻辑：
        - 如果用户设置的状态是 offline，则返回 offline
        - 如果用户最近5分钟有活动，则根据用户设置的状态返回 (online/busy/away)
        - 如果用户超过5分钟没有活动，则返回 offline
        """
        from datetime import datetime, timedelta
        
        # 如果用户设置的状态是 offline，直接返回
        if self.status == 'offline':
            return 'offline'
        
        # 检查最后活动时间
        if self.last_activity:
            five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
            if self.last_activity >= five_minutes_ago:
                # 用户在5分钟内有活动，返回用户设置的状态
                return self.status or 'online'
        
        # 用户超过5分钟没有活动，视为离线
        return 'offline'

    def update_activity(self):
        """更新用户最后活动时间"""
        self.last_activity = datetime.utcnow()

    # ==================== 大功能模块（侧边栏一级菜单）可见性 ====================
    def get_accessible_modules(self):
        """获取用户可见的大功能模块编码列表

        返回值：模块编码（module:xxx）列表
        规则：
        - 如果用户已经显式配置过 accessible_modules（即使为非空列表），以配置为准
        - 如果 accessible_modules 为 None：
            - 系统管理员 / 职位是管理员或经理：拥有所有模块
            - 其他用户：返回系统默认模块
        """
        # 延迟导入，避免循环
        from models.permissions import get_default_accessible_modules, MODULE_CATALOG

        # 显式配置过（含空列表）则完全按配置返回，不被职位权限覆盖
        if self.accessible_modules is not None:
            try:
                import json
                modules = json.loads(self.accessible_modules)
                if isinstance(modules, list):
                    return modules
            except Exception:
                pass

        # 未配置时：系统管理员/管理员/经理 -> 全部；普通用户 -> 默认
        if self.is_system_admin():
            return [m['code'] for m in MODULE_CATALOG]

        return get_default_accessible_modules()

    def set_accessible_modules(self, modules):
        """设置用户可见的大功能模块编码列表

        传入 [] 表示显式清空，传入 None 视为重置为系统默认
        """
        import json
        if modules is None:
            self.accessible_modules = None
            return
        if not isinstance(modules, list):
            modules = []
        # 去重
        modules = list(dict.fromkeys(modules))
        self.accessible_modules = json.dumps(modules, ensure_ascii=False)

    def can_access_module(self, module_code):
        """检查用户是否可访问指定大功能模块"""
        return module_code in self.get_accessible_modules()

    def reset_accessible_modules(self):
        """重置用户可见模块为系统默认值（清除显式配置）"""
        self.accessible_modules = None

class Department(db.Model):
    __tablename__ = 'departments'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Position(db.Model):
    __tablename__ = 'positions'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    permissions = Column(Text, default='[]')
    is_admin = Column(Boolean, default=False)
    is_manager = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': self.permissions,
            'is_admin': self.is_admin,
            'is_manager': self.is_manager,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class PersonalTask(db.Model):
    __tablename__ = 'personal_tasks'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    parent_id = Column(Integer, ForeignKey('personal_tasks.id'), nullable=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    status = Column(String(20), default='todo', nullable=False)
    priority = Column(String(20), default='medium')
    progress = Column(Integer, default=0)
    quadrant = Column(Integer)
    scheduled_date = Column(String(20))
    scheduled_time = Column(String(10))
    due_date = Column(String(20))
    estimated_minutes = Column(Integer)
    actual_minutes = Column(Integer)
    tags = Column(String(500))
    is_habit = Column(Boolean, default=False)
    habit_frequency = Column(String(20))
    source = Column(String(20), default='manual')
    dependencies = Column(Text)  # JSON格式存储依赖任务ID列表
    is_pinned = Column(Boolean, default=False)
    order_index = Column(Integer, default=0)
    reminder_config = Column(Text)  # JSON格式: {"before_hours": 1, "channels": ["browser", "email"]}
    completed = Column(Boolean, default=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系定义
    subtasks = db.relationship('PersonalTask', backref=db.backref('parent', remote_side=[id]),
                               lazy='dynamic', foreign_keys=[parent_id])

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'parent_id': self.parent_id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'progress': self.progress,
            'quadrant': self.quadrant,
            'scheduled_date': self.scheduled_date,
            'scheduled_time': self.scheduled_time,
            'due_date': self.due_date,
            'estimated_minutes': self.estimated_minutes,
            'actual_minutes': self.actual_minutes,
            'tags': self.tags,
            'is_habit': self.is_habit,
            'habit_frequency': self.habit_frequency,
            'source': self.source,
            'dependencies': json.loads(self.dependencies) if self.dependencies else [],
            'is_pinned': self.is_pinned,
            'order_index': self.order_index,
            'reminder_config': json.loads(self.reminder_config) if self.reminder_config else None,
            'completed': self.completed,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'subtask_count': self.subtasks.count() if self.subtasks else 0,
            'completed_subtasks': self.subtasks.filter_by(completed=True).count() if self.subtasks else 0
        }

class FocusSession(db.Model):
    __tablename__ = 'focus_sessions'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    task_id = Column(Integer, ForeignKey('personal_tasks.id'))
    focus_type = Column(String(20), default='pomodoro')
    planned_duration = Column(Integer, default=25)
    actual_duration = Column(Integer)
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'task_id': self.task_id,
            'focus_type': self.focus_type,
            'planned_duration': self.planned_duration,
            'actual_duration': self.actual_duration,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class HabitRecord(db.Model):
    __tablename__ = 'habit_records'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    task_id = Column(Integer, ForeignKey('personal_tasks.id'))
    completed_date = Column(Date, nullable=False)
    duration_minutes = Column(Integer)
    note = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'task_id': self.task_id,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'duration_minutes': self.duration_minutes,
            'note': self.note,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PlanTemplate(db.Model):
    """计划模板 - 用于快速创建重复性任务计划"""
    __tablename__ = 'plan_templates'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    template_type = Column(String(20), default='daily')  # daily/weekly/project
    tasks_template = Column(Text, nullable=False)  # JSON格式: 任务模板列表
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'template_type': self.template_type,
            'tasks_template': json.loads(self.tasks_template) if self.tasks_template else [],
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ReviewRecord(db.Model):
    """复盘记录 - 存储用户的复盘数据"""
    __tablename__ = 'review_records'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(200))
    date_range_start = Column(String(20), nullable=False)
    date_range_end = Column(String(20), nullable=False)
    review_type = Column(String(20), default='weekly')  # weekly/monthly/custom

    # 核心指标
    total_planned = Column(Integer, default=0)
    total_completed = Column(Integer, default=0)
    total_planned_hours = Column(Float, default=0.0)
    total_actual_hours = Column(Float, default=0.0)
    overdue_count = Column(Integer, default=0)
    avg_overdue_days = Column(Float, default=0.0)

    # 复盘内容
    summary_text = Column(Text)  # 自动生成的周报文案
    key_achievements = Column(Text)  # 重点工作成果
    challenges = Column(Text)  # 遇到的挑战和问题
    lessons_learned = Column(Text)  # 经验教训
    next_week_plan = Column(Text)  # 下周计划

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'date_range_start': self.date_range_start,
            'date_range_end': self.date_range_end,
            'review_type': self.review_type,
            'total_planned': self.total_planned,
            'total_completed': self.total_completed,
            'completion_rate': round((self.total_completed / self.total_planned * 100) if self.total_planned > 0 else 0, 1),
            'total_planned_hours': self.total_planned_hours,
            'total_actual_hours': self.total_actual_hours,
            'hours_variance': round((self.total_actual_hours - self.total_planned_hours), 1),
            'overdue_count': self.overdue_count,
            'avg_overdue_days': round(self.avg_overdue_days, 1),
            'summary_text': self.summary_text,
            'key_achievements': self.key_achievements,
            'challenges': self.challenges,
            'lessons_learned': self.lessons_learned,
            'next_week_plan': self.next_week_plan,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class PersonalSettings(db.Model):
    __tablename__ = 'personal_settings'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    default_view = Column(String(20), default='list')
    pomodoro_duration = Column(Integer, default=25)
    break_duration = Column(Integer, default=5)
    long_break_duration = Column(Integer, default=15)
    work_streak_alert = Column(Integer, default=60)
    custom_tags = Column(String(500))
    tag_colors = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        import json
        tag_colors_dict = {}
        if self.tag_colors:
            try:
                tag_colors_dict = json.loads(self.tag_colors)
            except:
                pass
        return {
            'id': self.id,
            'user_id': self.user_id,
            'default_view': self.default_view,
            'pomodoro_duration': self.pomodoro_duration,
            'break_duration': self.break_duration,
            'long_break_duration': self.long_break_duration,
            'work_streak_alert': self.work_streak_alert,
            'custom_tags': self.custom_tags.split(',') if self.custom_tags else [],
            'tag_colors': tag_colors_dict,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# 定义Project模型（在模块级别定义）
class Project(db.Model):
    __tablename__ = 'projects'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    code = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    status = Column(String(50), default='active', nullable=False)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey('users.id'))
    manager_id = Column(Integer, ForeignKey('users.id'))
    progress = Column(Integer, default=0)
    current_stage = Column(String(100))
    quality = Column(String(50))
    risk = Column(String(50))
    resources = Column(Text)
    cost = Column(Float, default=0.0)  # 费用: 0=normal, >0=over, <0=under
    priority = Column(String(50))
    technology_stack = Column(Text)
    budget = Column(Float, default=0.0)
    actual_cost = Column(Float, default=0.0)
    project_type = Column(String(50))  # 项目类型
    client_name = Column(String(200))  # 客户名称
    client_contact = Column(String(200))  # 客户联系方式
    contract_value = Column(Float, default=0.0)  # 合同金额
    estimated_hours = Column(Integer, default=0)  # 预估工时
    actual_hours = Column(Integer, default=0)  # 实际工时
    team_size = Column(Integer, default=0)  # 团队规模
    tags = Column(Text)  # 标签
    milestones = Column(Text)  # 里程碑
    versions = Column(Text)  # 项目版本列表，JSON格式存储
    modules = Column(Text)  # 项目模块列表，JSON格式存储
    
    # 关系
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    manager = relationship("User", foreign_keys=[manager_id])
    owner = relationship("User", foreign_keys=[owner_id])
    creator = relationship("User", foreign_keys=[created_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'owner_id': self.owner_id,
            'manager_id': self.manager_id,
            'progress': self.progress,
            'current_stage': self.current_stage,
            'quality': self.quality,
            'risk': self.risk,
            'resources': self.resources,
            'cost': self.cost,
            'priority': self.priority,
            'technology_stack': self.technology_stack,
            'budget': self.budget,
            'actual_cost': self.actual_cost,
            'project_type': self.project_type,
            'client_name': self.client_name,
            'client_contact': self.client_contact,
            'contract_value': self.contract_value,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'team_size': self.team_size,
            'tags': self.tags,
            'milestones': self.milestones,
            'versions': self.versions,
            'modules': self.modules
        }

# 定义项目成员模型
class ProjectMember(db.Model):
    """项目成员模型"""
    __tablename__ = 'project_members'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    role = Column(String(50), default='member')
    join_date = Column(DateTime, default=datetime.utcnow)

    # 关系
    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="projects")

# 定义考勤相关模型

# 工作日历模型
class WorkCalendar(db.Model):
    __tablename__ = 'work_calendar'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False, unique=True)  # 日期
    is_working_day = Column(Boolean, default=True)  # 是否工作日
    is_holiday = Column(Boolean, default=False)  # 是否节假日
    note = Column(String(255))  # 备注
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'is_working_day': self.is_working_day,
            'is_holiday': self.is_holiday,
            'note': self.note,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# 班次模型
class ShiftSchedule(db.Model):
    __tablename__ = 'shift_schedules'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)  # 班次名称
    start_time = Column(String(5), nullable=False)  # 开始时间（格式：HH:MM）
    end_time = Column(String(5), nullable=False)  # 结束时间（格式：HH:MM）
    shift_type = Column(String(50), nullable=False)  # 班次类型（如：白班、夜班）
    flexible_range = Column(Integer, default=30)  # 弹性范围（分钟）
    overtime_threshold = Column(Integer, default=60)  # 加班起算点（分钟）
    is_active = Column(Boolean, default=True)  # 是否启用
    description = Column(Text)  # 班次描述
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'shift_type': self.shift_type,
            'flexible_range': self.flexible_range,
            'overtime_threshold': self.overtime_threshold,
            'is_active': self.is_active,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# 用户班次分配模型
class UserShift(db.Model):
    __tablename__ = 'user_shifts'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # 用户ID
    shift_id = Column(Integer, ForeignKey('shift_schedules.id'), nullable=False)  # 班次ID
    effective_date = Column(DateTime, nullable=False)  # 生效日期
    expire_date = Column(DateTime)  # 过期日期
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User")
    shift = relationship("ShiftSchedule")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'shift_id': self.shift_id,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'expire_date': self.expire_date.isoformat() if self.expire_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# 考勤记录模型
class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # 用户ID
    record_date = Column(DateTime, nullable=False)  # 记录日期
    status = Column(String(20), default="present", nullable=False)  # 考勤状态
    clock_in_time = Column(DateTime)  # 上班打卡时间
    clock_in_ip = Column(String(50))  # 上班打卡IP
    clock_in_location = Column(String(255))  # 上班打卡地理位置
    clock_out_time = Column(DateTime)  # 下班打卡时间
    clock_out_ip = Column(String(50))  # 下班打卡IP
    clock_out_location = Column(String(255))  # 下班打卡地理位置
    work_hours = Column(Float, default=0.0)  # 工作时长（小时）
    overtime_hours = Column(Float, default=0.0)  # 加班时长（小时）
    late_minutes = Column(Integer, default=0)  # 迟到分钟数
    early_leave_minutes = Column(Integer, default=0)  # 早退分钟数
    note = Column(Text)  # 备注
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'record_date': self.record_date.isoformat() if self.record_date else None,
            'status': self.status.value if hasattr(self.status, 'value') else str(self.status),
            'clock_in_time': self.clock_in_time.isoformat() if self.clock_in_time else None,
            'clock_in_ip': self.clock_in_ip,
            'clock_in_location': self.clock_in_location,
            'clock_out_time': self.clock_out_time.isoformat() if self.clock_out_time else None,
            'clock_out_ip': self.clock_out_ip,
            'clock_out_location': self.clock_out_location,
            'work_hours': self.work_hours,
            'overtime_hours': self.overtime_hours,
            'late_minutes': self.late_minutes,
            'early_leave_minutes': self.early_leave_minutes,
            'note': self.note,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# 请假申请模型
class LeaveApplication(db.Model):
    __tablename__ = 'leave_applications'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # 申请人ID
    start_date = Column(DateTime, nullable=False)  # 开始日期
    end_date = Column(DateTime, nullable=False)  # 结束日期
    leave_type = Column(String(50), nullable=False)  # 请假类型
    days = Column(Float, nullable=False)  # 请假天数
    reason = Column(Text, nullable=False)  # 请假原因
    approval_comment = Column(Text)  # 审批意见
    status = Column(String(20), default="pending", nullable=False)  # 审批状态
    approver_id = Column(Integer, ForeignKey('users.id'))  # 当前审批人ID
    approved_at = Column(DateTime)  # 审批时间
    current_approver_level = Column(Integer, default=1)  # 当前审批层级（1=组长,2=经理,3=总监）
    approval_levels = Column(Text)  # 审批层级配置JSON，如 [{"level":1,"approver_id":5,"status":"approved"},{"level":2,"approver_id":8,"status":"pending"}]
    emergency_flag = Column(Boolean, default=False)  # 是否紧急
    attachment_path = Column(String(500))  # 附件路径
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", foreign_keys=[user_id])
    approver = relationship("User", foreign_keys=[approver_id])

    @property
    def attachment(self):
        """兼容attachment属性访问"""
        return self.attachment_path

    def to_dict(self):
        import json
        approval_levels_list = []
        if self.approval_levels:
            try:
                approval_levels_list = json.loads(self.approval_levels)
            except:
                pass
        return {
            'id': self.id,
            'user_id': self.user_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'leave_type': self.leave_type,
            'reason': self.reason,
            'status': self.status.value if hasattr(self.status, 'value') else str(self.status),
            'approver_id': self.approver_id,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'current_approver_level': self.current_approver_level or 1,
            'approval_levels': approval_levels_list,
            'emergency_flag': self.emergency_flag or False,
            'attachment_path': self.attachment_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# 加班申请模型
class OvertimeApplication(db.Model):
    __tablename__ = 'overtime_applications'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # 申请人ID
    date = Column(DateTime, nullable=False)  # 加班日期
    start_time = Column(String(5), nullable=False)  # 开始时间（格式：HH:MM）
    end_time = Column(String(5), nullable=False)  # 结束时间（格式：HH:MM）
    reason = Column(Text, nullable=False)  # 加班原因
    status = Column(String(20), default="pending", nullable=False)  # 审批状态
    approver_id = Column(Integer, ForeignKey('users.id'))  # 审批人ID
    approved_at = Column(DateTime)  # 审批时间
    rejection_reason = Column(Text)  # 拒绝原因
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", foreign_keys=[user_id])
    approver = relationship("User", foreign_keys=[approver_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'reason': self.reason,
            'status': self.status.value if hasattr(self.status, 'value') else str(self.status),
            'approver_id': self.approver_id,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# 考勤异常模型
class AttendanceException(db.Model):
    __tablename__ = 'attendance_exceptions'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # 用户ID
    record_date = Column(DateTime, nullable=False)  # 异常日期
    exception_type = Column(String(50), nullable=False)  # 异常类型
    reason = Column(Text, nullable=False)  # 异常原因
    status = Column(String(20), default="pending", nullable=False)  # 审批状态
    approver_id = Column(Integer, ForeignKey('users.id'))  # 审批人ID
    approved_at = Column(DateTime)  # 审批时间
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", foreign_keys=[user_id])
    approver = relationship("User", foreign_keys=[approver_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'record_date': self.record_date.isoformat() if self.record_date else None,
            'exception_type': self.exception_type,
            'reason': self.reason,
            'status': self.status.value if hasattr(self.status, 'value') else str(self.status),
            'approver_id': self.approver_id,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# 定义 Bug 相关模型
class Bug(db.Model):
    __tablename__ = 'bugs'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)  # Bug 标题
    description = Column(Text, nullable=False)  # Bug 描述
    status = Column(String(50), default=BugStatus.NEW.value, nullable=False)  # Bug 状态
    priority = Column(String(20), default=Priority.MEDIUM.value, nullable=False)  # 优先级
    severity = Column(String(20), default=Severity.HIGH.value, nullable=False)  # 严重程度
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)  # 所属项目ID
    reported_by = Column(Integer, ForeignKey('users.id'), nullable=False)  # 报告人ID
    assigned_to = Column(Integer, ForeignKey('users.id'))  # 分配给ID
    resolved_by = Column(Integer, ForeignKey('users.id'))  # 解决者ID
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    resolved_at = Column(DateTime)  # 解决时间
    closed_at = Column(DateTime)  # 关闭时间
    
    # 实际存在的字段
    version = Column(String(50))  # 版本号
    tags = Column(Text)  # 标签
    issue_type = Column(String(50))  # 问题类型
    reproduce_frequency = Column(String(50))  # 重现频率
    found_build = Column(String(50))  # 发现构建版本
    test_version = Column(String(50))  # 测试版本
    module = Column(String(100))  # 模块
    reproduce_steps = Column(Text)  # 重现步骤
    expected_result = Column(Text)  # 期望结果
    actual_result = Column(Text)  # 实际结果
    attachment_path = Column(String(255))  # 附件路径
    resolution = Column(Text)  # 解决方案
    resolution_version = Column(String(50))  # 解决版本
    reopened_count = Column(Integer, default=0)  # 重新打开次数
    related_bug_id = Column(Integer, ForeignKey('bugs.id'))  # 相关缺陷ID
    parent_bug_id = Column(Integer, ForeignKey('bugs.id'))  # 父缺陷ID
    estimated_hours = Column(Float)  # 预计工时
    actual_hours = Column(Float)  # 实际工时
    test_case_id = Column(String(50))  # 关联测试用例ID
    
    # 扩展字段
    bug_type = Column(String(50))  # Bug类型
    root_cause = Column(String(50))  # 根因
    verifier_id = Column(Integer, ForeignKey('users.id'))  # 验证者ID
    customer_mr_number = Column(String(100))  # 客户MR编号
    plan_resolve_version = Column(String(50))  # 计划解决版本
    resolve_build = Column(String(50))  # 解决构建
    deadline = Column(DateTime)  # 截止日期
    verified_at = Column(DateTime)  # 验证时间
    verified_by = Column(Integer, ForeignKey('users.id'))  # 验证人ID
    steps_to_reproduce = Column(Text)  # 重现步骤
    
    # 关系
    project = relationship("Project", backref="bugs")
    reporter = relationship("User", foreign_keys=[reported_by], backref="reported_bugs")
    assignee = relationship("User", foreign_keys=[assigned_to], backref="assigned_bugs")
    resolver = relationship("User", foreign_keys=[resolved_by], backref="resolved_bugs")
    verifier = relationship("User", foreign_keys=[verifier_id], backref="verified_bugs")
    comments = relationship("Comment", foreign_keys="[Comment.commentable_id]", primaryjoin="and_(Bug.id==Comment.commentable_id, Comment.commentable_type=='bug')", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': str(self.status) if self.status else '',
            'priority': str(self.priority) if self.priority else '',
            'severity': str(self.severity) if self.severity else '',
            'project_id': self.project_id,
            'reported_by': self.reported_by,
            'assigned_to': self.assigned_to,
            'resolved_by': self.resolved_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'version': self.version,
            'tags': self.tags,
            'issue_type': self.issue_type,
            'reproduce_frequency': self.reproduce_frequency,
            'found_build': self.found_build,
            'test_version': self.test_version,
            'module': self.module,
            'reproduce_steps': self.reproduce_steps,
            'steps_to_reproduce': self.steps_to_reproduce,
            'expected_result': self.expected_result,
            'actual_result': self.actual_result,
            'attachment_path': self.attachment_path,
            'resolution': self.resolution,
            'resolution_version': self.resolution_version,
            'reopened_count': self.reopened_count,
            'related_bug_id': self.related_bug_id,
            'parent_bug_id': self.parent_bug_id,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'test_case_id': self.test_case_id,
            'bug_type': self.bug_type,
            'root_cause': self.root_cause,
            'verifier_id': self.verifier_id,
            'customer_mr_number': self.customer_mr_number,
            'plan_resolve_version': self.plan_resolve_version,
            'resolve_build': self.resolve_build,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'verified_by': self.verified_by
        }

# 定义评论模型
class Comment(db.Model):
    __tablename__ = 'comments'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)  # 评论内容
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)  # 创建人ID
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    # 多态关联
    commentable_type = Column(String(50), nullable=False)  # 评论对象类型（bug或task）
    commentable_id = Column(Integer, nullable=False)  # 评论对象ID
    
    # 关系
    creator = relationship("User", backref="comments")
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'commentable_type': self.commentable_type,
            'commentable_id': self.commentable_id,
            'author_name': self.creator.username if self.creator else None
        }

# 定义附件模型
class Attachment(db.Model):
    __tablename__ = 'attachments'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)  # 文件名
    file_path = Column(String(500), nullable=False)  # 文件路径
    file_size = Column(Integer)  # 文件大小（字节）
    mime_type = Column(String(100))  # MIME类型
    uploaded_by = Column(Integer, ForeignKey('users.id'), nullable=False)  # 上传人ID
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)  # 创建者ID
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    
    # 多态关联
    attachable_type = Column(String(50), nullable=False)  # 附件对象类型（bug、task等）
    attachable_id = Column(Integer, nullable=False)  # 附件对象ID
    
    # 关系
    uploader = relationship("User", backref="attachments", foreign_keys=[uploaded_by])
    creator = relationship("User", backref="created_attachments", foreign_keys=[created_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'uploaded_by': self.uploaded_by,
            'uploader_name': self.uploader.username if self.uploader else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'attachable_type': self.attachable_type,
            'attachable_id': self.attachable_id
        }

# 定义活动日志模型
class Activity(db.Model):
    __tablename__ = 'activities'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    action = Column(String(50), nullable=False)  # 活动类型
    description = Column(Text, nullable=False)  # 活动描述
    performed_by = Column(Integer, ForeignKey('users.id'), nullable=False)  # 执行人员ID
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    
    # 多态关联
    target_type = Column(String(50), nullable=False)  # 目标对象类型（bug、task等）
    target_id = Column(Integer, nullable=False)  # 目标对象ID
    
    # 字段变更详情（JSON格式存储）
    field_changes = Column(Text)  # 存储字段变更详情，如: [{"field": "title", "old_value": "xxx", "new_value": "yyy"}]
    
    # 关系
    performer = relationship("User", backref="activities")
    
    def to_dict(self):
        return {
            'id': self.id,
            'action': self.action,
            'description': self.description,
            'performed_by': self.performed_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'field_changes': self.field_changes
        }

class ProjectLogStatus(enum.Enum):
    """项目日志状态枚举"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class ProjectLogType(enum.Enum):
    """项目日志类型枚举"""
    PROGRESS = "progress"
    ISSUE = "issue"
    MILESTONE = "milestone"
    MEETING = "meeting"
    RISK = "risk"
    CHANGE = "change"
    GENERAL = "general"

class ProjectLog(db.Model):
    __tablename__ = 'project_logs'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    log_type = Column(String(50), default=ProjectLogType.GENERAL.value)
    status = Column(String(50), default=ProjectLogStatus.DRAFT.value)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    logged_at = Column(DateTime)
    start_date = Column(Date)
    end_date = Column(Date)

    project = relationship("Project", backref="logs")
    creator = relationship("User", foreign_keys=[created_by], backref="project_logs")

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'title': self.title,
            'content': self.content,
            'log_type': self.log_type,
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'logged_at': self.logged_at.isoformat() if self.logged_at else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'creator_name': self.creator.username if self.creator else None,
            'project_name': self.project.name if self.project else None
        }

class RiskStatus(enum.Enum):
    """风险状态枚举"""
    IDENTIFIED = "identified"
    ANALYZED = "analyzed"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ACCEPTED = "accepted"

class RiskLevel(enum.Enum):
    """风险等级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RiskCategory(enum.Enum):
    """风险类别枚举"""
    TECHNICAL = "technical"
    SCHEDULE = "schedule"
    BUDGET = "budget"
    RESOURCE = "resource"
    REQUIREMENT = "requirement"
    QUALITY = "quality"
    EXTERNAL = "external"
    OTHER = "other"

class IssueStatus(enum.Enum):
    """问题状态枚举"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    DUPLICATE = "duplicate"

class IssuePriority(enum.Enum):
    """问题优先级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Risk(db.Model):
    """风险和问题管理模型"""
    __tablename__ = 'risks'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    risk_type = Column(String(20), default='risk')  # risk 或 issue

    title = Column(String(255), nullable=False)  # 标题
    description = Column(Text)  # 描述

    status = Column(String(50), default='identified')  # 状态
    priority = Column(String(50), default='medium')  # 优先级
    level = Column(String(50), default='medium')  # 风险等级

    category = Column(String(50))  # 类别

    identified_by = Column(Integer, ForeignKey('users.id'))  # 识别人
    assigned_to = Column(Integer, ForeignKey('users.id'))  # 负责人

    probability = Column(Float, default=0.0)  # 发生概率 0-1
    impact = Column(Float, default=0.0)  # 影响程度 0-1
    exposure = Column(Float, default=0.0)  # 风险暴露度

    mitigation_strategy = Column(Text)  # 应对策略
    contingency_plan = Column(Text)  # 应急预案
    resolution = Column(Text)  # 解决方案

    identified_date = Column(Date)  # 识别日期
    due_date = Column(Date)  # 截止日期
    resolved_date = Column(Date)  # 解决日期
    closed_date = Column(Date)  # 关闭日期

    trigger_condition = Column(Text)  # 触发条件
    indicator = Column(String(255))  # 监控指标

    related_risk_id = Column(Integer, ForeignKey('risks.id'))  # 相关风险ID
    related_bug_id = Column(Integer, ForeignKey('bugs.id'))  # 相关缺陷ID
    related_task_id = Column(Integer, ForeignKey('tasks.id'))  # 相关任务ID

    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", backref="risks")
    identifier = relationship("User", foreign_keys=[identified_by], backref="identified_risks")
    assignee = relationship("User", foreign_keys=[assigned_to], backref="assigned_risks")
    creator = relationship("User", foreign_keys=[created_by], backref="created_risks")
    related_risk = relationship("Risk", remote_side=[id], backref="related_risks")
    related_bug = relationship("Bug", backref="related_risks")
    # related_task = relationship("Task", backref="related_risks")  # Task模型不存在，暂时注释

    def calculate_exposure(self):
        """计算风险暴露度"""
        if self.probability is not None and self.impact is not None:
            return round(self.probability * self.impact, 2)
        return 0.0

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'risk_type': self.risk_type,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'level': self.level,
            'category': self.category,
            'identified_by': self.identified_by,
            'assigned_to': self.assigned_to,
            'probability': self.probability,
            'impact': self.impact,
            'exposure': self.calculate_exposure(),
            'mitigation_strategy': self.mitigation_strategy,
            'contingency_plan': self.contingency_plan,
            'resolution': self.resolution,
            'identified_date': self.identified_date.isoformat() if self.identified_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'resolved_date': self.resolved_date.isoformat() if self.resolved_date else None,
            'closed_date': self.closed_date.isoformat() if self.closed_date else None,
            'trigger_condition': self.trigger_condition,
            'indicator': self.indicator,
            'related_risk_id': self.related_risk_id,
            'related_bug_id': self.related_bug_id,
            'related_task_id': self.related_task_id,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'identifier_name': self.identifier.username if self.identifier else None,
            'assignee_name': self.assignee.username if self.assignee else None,
            'creator_name': self.creator.username if self.creator else None,
            'project_name': self.project.name if self.project else None
        }

# 定义物料管理相关模型

# 物料分类模型
class MaterialCategory(db.Model):
    __tablename__ = 'material_categories'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)  # 分类名称
    code = Column(String(50), unique=True, nullable=False)  # 分类编码
    description = Column(Text)  # 分类描述
    parent_id = Column(Integer, ForeignKey('material_categories.id'))  # 父分类ID
    level = Column(Integer, default=1)  # 分类级别
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    # 关系
    parent = relationship("MaterialCategory", remote_side=[id], backref="children")
    materials = relationship("Material", backref="category", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'parent_id': self.parent_id,
            'level': self.level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# 物料主数据模型
class Material(db.Model):
    __tablename__ = 'materials'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)  # 物料名称
    code = Column(String(100), unique=True, nullable=False)  # 物料编码
    spec = Column(String(255))  # 物料规格
    unit = Column(String(20), nullable=False)  # 单位
    category_id = Column(Integer, ForeignKey('material_categories.id'))  # 分类ID
    description = Column(Text)  # 物料描述
    safety_stock = Column(Float, default=0.0)  # 安全库存
    supplier = Column(String(255))  # 供应商
    supplier_code = Column(String(100))  # 供应商物料编码
    unit_cost = Column(Float, default=0.0)  # 默认单位成本
    status = Column(String(20), default='active')  # 状态
    created_by = Column(Integer, ForeignKey('users.id'))  # 创建人ID
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    # 关系
    creator = relationship("User", foreign_keys=[created_by])
    inventories = relationship("Inventory", backref="material", cascade="all, delete-orphan")
    serial_numbers = relationship("SerialNumber", backref="material", cascade="all, delete-orphan")
    relationships = relationship("MaterialRelationship", foreign_keys="MaterialRelationship.source_material_id", backref="source_material", cascade="all, delete-orphan")
    related_materials = relationship("MaterialRelationship", foreign_keys="MaterialRelationship.target_material_id", backref="target_material", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'spec': self.spec,
            'unit': self.unit,
            'category_id': self.category_id,
            'description': self.description,
            'safety_stock': self.safety_stock,
            'supplier': self.supplier,
            'supplier_code': self.supplier_code,
            'unit_cost': self.unit_cost,
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# 仓库模型
class Warehouse(db.Model):
    __tablename__ = 'warehouses'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)  # 仓库名称
    code = Column(String(50), unique=True, nullable=False)  # 仓库编码
    location = Column(String(255))  # 仓库位置
    contact = Column(String(100))  # 联系人
    phone = Column(String(20))  # 联系电话
    description = Column(Text)  # 仓库描述
    status = Column(String(20), default='active')  # 状态
    created_by = Column(Integer, ForeignKey('users.id'))  # 创建人ID
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    # 关系
    creator = relationship("User", foreign_keys=[created_by])
    locations = relationship("Location", backref="warehouse", cascade="all, delete-orphan")
    inventories = relationship("Inventory", backref="warehouse", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'location': self.location,
            'contact': self.contact,
            'phone': self.phone,
            'description': self.description,
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# 库位模型
class Location(db.Model):
    __tablename__ = 'locations'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=False)  # 仓库ID
    name = Column(String(100), nullable=False)  # 库位名称
    code = Column(String(50), unique=True, nullable=False)  # 库位编码
    area = Column(String(50))  # 区域
    zone = Column(String(50))  # 分区
    rack = Column(String(50))  # 货架
    level = Column(String(50))  # 层级
    capacity = Column(Integer, default=0)  # 容量
    type = Column(String(20))  # 库位类型
    status = Column(String(20), default='active')  # 状态
    description = Column(Text)  # 库位描述
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    # 关系
    inventories = relationship("Inventory", backref="location", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'warehouse_id': self.warehouse_id,
            'name': self.name,
            'code': self.code,
            'area': self.area,
            'zone': self.zone,
            'rack': self.rack,
            'level': self.level,
            'capacity': self.capacity,
            'type': self.type,
            'status': self.status,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# 库存模型
class Inventory(db.Model):
    __tablename__ = 'inventories'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    material_id = Column(Integer, ForeignKey('materials.id'), nullable=False)  # 物料ID
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=False)  # 仓库ID
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=False)  # 库位ID
    quantity = Column(Float, default=0.0)  # 库存数量
    unit_cost = Column(Float, default=0.0)  # 单位成本
    total_cost = Column(Float, default=0.0)  # 总成本
    available_quantity = Column(Float, default=0.0)  # 可用数量
    locked_quantity = Column(Float, default=0.0)  # 锁定数量
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    def to_dict(self):
        return {
            'id': self.id,
            'material_id': self.material_id,
            'warehouse_id': self.warehouse_id,
            'location_id': self.location_id,
            'quantity': self.quantity,
            'unit_cost': self.unit_cost,
            'total_cost': self.total_cost,
            'available_quantity': self.available_quantity,
            'locked_quantity': self.locked_quantity,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# 序列号模型
class SerialNumber(db.Model):
    __tablename__ = 'serial_numbers'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    material_id = Column(Integer, ForeignKey('materials.id'), nullable=False)  # 物料ID
    serial_number = Column(String(100), unique=True, nullable=False)  # 序列号
    status = Column(String(20), default='available')  # 状态
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'))  # 仓库ID
    location_id = Column(Integer, ForeignKey('locations.id'))  # 库位ID
    transaction_id = Column(Integer, ForeignKey('inventory_transactions.id'))  # 交易ID
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    # 关系
    warehouse = relationship("Warehouse")
    location = relationship("Location")
    
    def to_dict(self):
        return {
            'id': self.id,
            'material_id': self.material_id,
            'serial_number': self.serial_number,
            'status': self.status,
            'warehouse_id': self.warehouse_id,
            'location_id': self.location_id,
            'transaction_id': self.transaction_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# 库存交易模型
class InventoryTransaction(db.Model):
    __tablename__ = 'inventory_transactions'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    transaction_date = Column(DateTime, default=datetime.utcnow)  # 交易日期
    transaction_type = Column(String(20), nullable=False)  # 交易类型
    reference_no = Column(String(50))  # 参考单据号
    material_id = Column(Integer, ForeignKey('materials.id'))  # 物料ID
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'))  # 仓库ID
    location_id = Column(Integer, ForeignKey('locations.id'))  # 库位ID
    quantity = Column(Float, nullable=False)  # 交易数量
    unit_cost = Column(Float, default=0.0)  # 单位成本
    total_cost = Column(Float, default=0.0)  # 总成本
    status = Column(String(20), default='completed')  # 交易状态
    created_by = Column(Integer, ForeignKey('users.id'))  # 创建人ID
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    # 关系
    material = relationship("Material")
    warehouse = relationship("Warehouse")
    location = relationship("Location")
    creator = relationship("User", foreign_keys=[created_by])
    serial_numbers = relationship("SerialNumber", backref="inventory_transaction", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'transaction_type': self.transaction_type,
            'reference_no': self.reference_no,
            'material_id': self.material_id,
            'warehouse_id': self.warehouse_id,
            'location_id': self.location_id,
            'quantity': self.quantity,
            'unit_cost': self.unit_cost,
            'total_cost': self.total_cost,
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# 物料关系模型
class MaterialRelationship(db.Model):
    __tablename__ = 'material_relationships'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    source_material_id = Column(Integer, ForeignKey('materials.id'), nullable=False)  # 源物料ID
    target_material_id = Column(Integer, ForeignKey('materials.id'), nullable=False)  # 目标物料ID
    relationship_type = Column(String(50), nullable=False)  # 关系类型
    quantity = Column(Float, default=1.0)  # 数量关系
    description = Column(Text)  # 关系描述
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    def to_dict(self):
        return {
            'id': self.id,
            'source_material_id': self.source_material_id,
            'target_material_id': self.target_material_id,
            'relationship_type': self.relationship_type,
            'quantity': self.quantity,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# 库存盘点模型
class InventoryCheck(db.Model):
    __tablename__ = 'inventory_checks'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    check_no = Column(String(50), unique=True, nullable=False)  # 盘点单号
    check_date = Column(DateTime, default=datetime.utcnow)  # 盘点日期
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'))  # 仓库ID
    status = Column(String(20), default='pending')  # 盘点状态
    total_items = Column(Integer, default=0)  # 盘点总项数
    total_quantity = Column(Float, default=0.0)  # 盘点总数量
    variance_quantity = Column(Float, default=0.0)  # 差异数量
    variance_amount = Column(Float, default=0.0)  # 差异金额
    checked_by = Column(Integer, ForeignKey('users.id'))  # 盘点人ID
    approved_by = Column(Integer, ForeignKey('users.id'))  # 审核人ID
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    # 关系
    warehouse = relationship("Warehouse")
    checker = relationship("User", foreign_keys=[checked_by])
    approver = relationship("User", foreign_keys=[approved_by])
    details = relationship("InventoryCheckDetail", backref="inventory_check", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'check_no': self.check_no,
            'check_date': self.check_date.isoformat() if self.check_date else None,
            'warehouse_id': self.warehouse_id,
            'status': self.status,
            'total_items': self.total_items,
            'total_quantity': self.total_quantity,
            'variance_quantity': self.variance_quantity,
            'variance_amount': self.variance_amount,
            'checked_by': self.checked_by,
            'approved_by': self.approved_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# 库存盘点明细模型
class InventoryCheckDetail(db.Model):
    __tablename__ = 'inventory_check_details'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    check_id = Column(Integer, ForeignKey('inventory_checks.id'), nullable=False)  # 盘点单ID
    material_id = Column(Integer, ForeignKey('materials.id'), nullable=False)  # 物料ID
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=False)  # 仓库ID
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=False)  # 库位ID
    system_quantity = Column(Float, default=0.0)  # 系统数量
    actual_quantity = Column(Float, default=0.0)  # 实际数量
    variance_quantity = Column(Float, default=0.0)  # 差异数量
    unit_cost = Column(Float, default=0.0)  # 单位成本
    variance_amount = Column(Float, default=0.0)  # 差异金额
    reason = Column(Text)  # 差异原因
    status = Column(String(20), default='pending')  # 处理状态
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    # 关系
    material = relationship("Material")
    warehouse = relationship("Warehouse")
    location = relationship("Location")
    
    def to_dict(self):
        return {
            'id': self.id,
            'check_id': self.check_id,
            'material_id': self.material_id,
            'warehouse_id': self.warehouse_id,
            'location_id': self.location_id,
            'system_quantity': self.system_quantity,
            'actual_quantity': self.actual_quantity,
            'variance_quantity': self.variance_quantity,
            'unit_cost': self.unit_cost,
            'variance_amount': self.variance_amount,
            'reason': self.reason,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# 定义通知模型
class Notification(db.Model):
    __tablename__ = 'notifications'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    related_bug_id = Column(Integer, ForeignKey('bugs.id'))
    related_comment_id = Column(Integer, ForeignKey('comments.id'))
    # 通用跳转链接，用于评审、任务等通知的跳转
    link = Column(String(500))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime)

    user = relationship("User", backref="notifications")
    related_bug = relationship("Bug")
    related_comment = relationship("Comment")

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'title': self.title,
            'content': self.content,
            'related_bug_id': self.related_bug_id,
            'related_comment_id': self.related_comment_id,
            'link': self.link,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None
        }


class Contract(db.Model):
    __tablename__ = 'contracts'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    contract_no = Column(String(50), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    contract_type = Column(String(50), nullable=False)
    status = Column(String(30), default='draft')
    risk_level = Column(String(20), default='low')
    
    party_a = Column(String(255))
    party_a_name = Column(String(255))
    party_b = Column(String(255))
    party_b_name = Column(String(255))
    
    project_id = Column(Integer, ForeignKey('projects.id'))
    project_name = Column(String(255))
    
    signing_date = Column(DateTime)
    effective_date = Column(DateTime)
    expiration_date = Column(DateTime)
    
    total_amount = Column(Float, default=0.0)
    currency = Column(String(10), default='CNY')
    
    region = Column(String(100))
    country = Column(String(100))
    
    technical_requirements = Column(Text)
    delivery_requirements = Column(Text)
    acceptance_criteria = Column(Text)
    sla_requirements = Column(Text)
    
    ip_protection_required = Column(Boolean, default=False)
    export_control_applicable = Column(Boolean, default=False)
    
    file_url = Column(String(500))
    
    # ====== 通信设备企业增强字段 ======
    # 站点信息（JSON格式：包含站点名称、站点代码、经纬度、地址等）
    site_info = Column(Text)
    # 物料清单BOM信息（JSON格式：设备型号、数量、单价等）
    bom_info = Column(Text)
    # 知识产权许可信息
    ip_license_info = Column(Text)
    # 源代码托管要求
    source_code_deposit = Column(Boolean, default=False)
    # 背景知识产权定义
    background_ip = Column(Text)
    # 前景知识产权归属
    foreground_ip = Column(Text)
    # 出口管制声明
    export_control_declaration = Column(Text)
    # 制裁清单检查状态
    sanction_check_status = Column(String(20), default='pending')
    # 本地化合规要求
    local_compliance = Column(Text)
    # 付款条款（JSON格式：付款阶段、比例、节点等）
    payment_terms = Column(Text)
    # 信用证信息
    credit_line_info = Column(Text)
    # 履约保证金
    performance_bond = Column(Float, default=0.0)
    # 保修期（月）
    warranty_period = Column(Integer, default=12)
    # 数据保护条款
    data_protection_clause = Column(Text)
    # 适用法律
    governing_law = Column(String(100))
    # 争议解决方式
    dispute_resolution = Column(Text)
    # 项目经理ID
    project_manager_id = Column(Integer, ForeignKey('users.id'))
    # 技术负责人ID
    tech_lead_id = Column(Integer, ForeignKey('users.id'))
    # 供应链负责人ID
    supply_chain_lead_id = Column(Integer, ForeignKey('users.id'))
    # 关联的采购订单IDs（JSON数组）
    related_po_ids = Column(Text)
    # 合同附件技术规范版本
    tech_spec_version = Column(String(50))
    # 核心网技术标识
    is_core_network_tech = Column(Boolean, default=False)
    # 5G技术标识
    is_5g_related = Column(Boolean, default=False)
    # 验收类型：PAC（初验）/FAC（终验）/Both
    acceptance_type = Column(String(20), default='Both')
    # 交付进度百分比
    delivery_progress = Column(Float, default=0.0)
    
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    creator = relationship("User", foreign_keys=[created_by])
    project = relationship("Project", backref="contracts")
    project_manager = relationship("User", foreign_keys=[project_manager_id])
    tech_lead = relationship("User", foreign_keys=[tech_lead_id])
    supply_chain_lead = relationship("User", foreign_keys=[supply_chain_lead_id])
    
    def to_dict(self):
        import json
        site_info_dict = None
        bom_info_list = None
        payment_terms_list = None
        related_po_list = None
        
        if self.site_info:
            try:
                site_info_dict = json.loads(self.site_info)
            except:
                pass
        
        if self.bom_info:
            try:
                bom_info_list = json.loads(self.bom_info)
            except:
                pass
                
        if self.payment_terms:
            try:
                payment_terms_list = json.loads(self.payment_terms)
            except:
                pass
                
        if self.related_po_ids:
            try:
                related_po_list = json.loads(self.related_po_ids)
            except:
                pass
        
        return {
            'id': self.id,
            'contract_no': self.contract_no,
            'title': self.title,
            'contract_type': self.contract_type,
            'status': self.status,
            'risk_level': self.risk_level,
            'party_a': self.party_a,
            'party_a_name': self.party_a_name,
            'party_b': self.party_b,
            'party_b_name': self.party_b_name,
            'project_id': self.project_id,
            'project_name': self.project_name,
            'signing_date': self.signing_date.isoformat() if self.signing_date else None,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'total_amount': self.total_amount,
            'currency': self.currency,
            'region': self.region,
            'country': self.country,
            'technical_requirements': self.technical_requirements,
            'delivery_requirements': self.delivery_requirements,
            'acceptance_criteria': self.acceptance_criteria,
            'sla_requirements': self.sla_requirements,
            'ip_protection_required': self.ip_protection_required,
            'export_control_applicable': self.export_control_applicable,
            'file_url': self.file_url,
            # 通信设备企业增强字段
            'site_info': site_info_dict,
            'bom_info': bom_info_list,
            'ip_license_info': self.ip_license_info,
            'source_code_deposit': self.source_code_deposit,
            'background_ip': self.background_ip,
            'foreground_ip': self.foreground_ip,
            'export_control_declaration': self.export_control_declaration,
            'sanction_check_status': self.sanction_check_status,
            'local_compliance': self.local_compliance,
            'payment_terms': payment_terms_list,
            'credit_line_info': self.credit_line_info,
            'performance_bond': self.performance_bond,
            'warranty_period': self.warranty_period,
            'data_protection_clause': self.data_protection_clause,
            'governing_law': self.governing_law,
            'dispute_resolution': self.dispute_resolution,
            'project_manager_id': self.project_manager_id,
            'tech_lead_id': self.tech_lead_id,
            'supply_chain_lead_id': self.supply_chain_lead_id,
            'related_po_ids': related_po_list,
            'tech_spec_version': self.tech_spec_version,
            'is_core_network_tech': self.is_core_network_tech,
            'is_5g_related': self.is_5g_related,
            'acceptance_type': self.acceptance_type,
            'delivery_progress': self.delivery_progress,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ContractClause(db.Model):
    __tablename__ = 'contract_clauses'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey('contracts.id'), nullable=False)
    clause_type = Column(String(50))
    clause_title = Column(String(255))
    clause_content = Column(Text)
    risk_level = Column(String(20), default='low')
    is_standard = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    contract = relationship("Contract", backref="clauses")
    
    def to_dict(self):
        return {
            'id': self.id,
            'contract_id': self.contract_id,
            'clause_type': self.clause_type,
            'clause_title': self.clause_title,
            'clause_content': self.clause_content,
            'risk_level': self.risk_level,
            'is_standard': self.is_standard,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ContractApproval(db.Model):
    __tablename__ = 'contract_approvals'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey('contracts.id'), nullable=False)
    approval_level = Column(Integer, default=1)
    approver_role = Column(String(50))
    approver_id = Column(Integer, ForeignKey('users.id'))
    status = Column(String(20), default='pending')
    comments = Column(Text)
    approval_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    contract = relationship("Contract", backref="approvals")
    approver = relationship("User", foreign_keys=[approver_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'contract_id': self.contract_id,
            'approval_level': self.approval_level,
            'approver_role': self.approver_role,
            'approver_id': self.approver_id,
            'status': self.status,
            'comments': self.comments,
            'approval_date': self.approval_date.isoformat() if self.approval_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ContractDelivery(db.Model):
    __tablename__ = 'contract_deliveries'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey('contracts.id'), nullable=False)
    delivery_no = Column(String(50))
    site_name = Column(String(255))
    site_code = Column(String(100))
    equipment_type = Column(String(100))
    quantity = Column(Integer, default=0)
    planned_date = Column(DateTime)
    actual_date = Column(DateTime)
    status = Column(String(30), default='pending')
    location = Column(String(255))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    contract = relationship("Contract", backref="deliveries")
    
    def to_dict(self):
        return {
            'id': self.id,
            'contract_id': self.contract_id,
            'delivery_no': self.delivery_no,
            'site_name': self.site_name,
            'site_code': self.site_code,
            'equipment_type': self.equipment_type,
            'quantity': self.quantity,
            'planned_date': self.planned_date.isoformat() if self.planned_date else None,
            'actual_date': self.actual_date.isoformat() if self.actual_date else None,
            'status': self.status,
            'location': self.location,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ContractChange(db.Model):
    __tablename__ = 'contract_changes'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey('contracts.id'), nullable=False)
    change_no = Column(String(50))
    change_type = Column(String(50))
    change_description = Column(Text)
    original_value = Column(Float)
    new_value = Column(Float)
    impact_assessment = Column(Text)
    status = Column(String(20), default='pending')
    requested_by = Column(Integer, ForeignKey('users.id'))
    approved_by = Column(Integer, ForeignKey('users.id'))
    approval_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    contract = relationship("Contract", backref="changes")
    requester = relationship("User", foreign_keys=[requested_by])
    approver = relationship("User", foreign_keys=[approved_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'contract_id': self.contract_id,
            'change_no': self.change_no,
            'change_type': self.change_type,
            'change_description': self.change_description,
            'original_value': self.original_value,
            'new_value': self.new_value,
            'impact_assessment': self.impact_assessment,
            'status': self.status,
            'requested_by': self.requested_by,
            'approved_by': self.approved_by,
            'approval_date': self.approval_date.isoformat() if self.approval_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ContractRisk(db.Model):
    __tablename__ = 'contract_risks'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey('contracts.id'), nullable=False)
    risk_type = Column(String(50))
    risk_description = Column(Text)
    risk_level = Column(String(20))
    mitigation_measures = Column(Text)
    status = Column(String(20), default='identified')
    identified_by = Column(Integer, ForeignKey('users.id'))
    identified_date = Column(DateTime)
    resolved_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    contract = relationship("Contract", backref="risks")
    identifier = relationship("User", foreign_keys=[identified_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'contract_id': self.contract_id,
            'risk_type': self.risk_type,
            'risk_description': self.risk_description,
            'risk_level': self.risk_level,
            'mitigation_measures': self.mitigation_measures,
            'status': self.status,
            'identified_by': self.identified_by,
            'identified_date': self.identified_date.isoformat() if self.identified_date else None,
            'resolved_date': self.resolved_date.isoformat() if self.resolved_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ContractPayment(db.Model):
    __tablename__ = 'contract_payments'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey('contracts.id'), nullable=False)
    payment_no = Column(String(50))
    payment_stage = Column(String(100))
    planned_amount = Column(Float)
    actual_amount = Column(Float)
    currency = Column(String(10), default='CNY')
    planned_date = Column(DateTime)
    actual_date = Column(DateTime)
    payment_method = Column(String(50))
    status = Column(String(20), default='pending')
    invoice_no = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    contract = relationship("Contract", backref="payments")
    
    def to_dict(self):
        return {
            'id': self.id,
            'contract_id': self.contract_id,
            'payment_no': self.payment_no,
            'payment_stage': self.payment_stage,
            'planned_amount': self.planned_amount,
            'actual_amount': self.actual_amount,
            'currency': self.currency,
            'planned_date': self.planned_date.isoformat() if self.planned_date else None,
            'actual_date': self.actual_date.isoformat() if self.actual_date else None,
            'payment_method': self.payment_method,
            'status': self.status,
            'invoice_no': self.invoice_no,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ContractAttachment(db.Model):
    __tablename__ = 'contract_attachments'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey('contracts.id'), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500))
    file_type = Column(String(50))
    file_size = Column(Integer)
    attachment_type = Column(String(50))
    description = Column(Text)
    uploaded_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    contract = relationship("Contract", backref="attachments")
    uploader = relationship("User", foreign_keys=[uploaded_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'contract_id': self.contract_id,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'attachment_type': self.attachment_type,
            'description': self.description,
            'uploaded_by': self.uploaded_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ==================== 需求管理模型 ====================

class RequirementDocument(db.Model):
    """需求文档表"""
    __tablename__ = 'requirement_documents'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    doc_type = Column(String(50), default='functional')  # functional, non_functional
    status = Column(String(20), default='draft')  # draft, reviewing, approved, deprecated
    version = Column(Integer, default=1)
    owner_id = Column(Integer, ForeignKey('users.id'))
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    project = relationship("Project", backref="requirement_documents")
    creator = relationship("User", foreign_keys=[created_by])
    owner = relationship("User", foreign_keys=[owner_id])
    items = relationship("RequirementItem", back_populates="document", cascade="all, delete-orphan")
    versions = relationship("RequirementVersion", back_populates="document", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'doc_type': self.doc_type,
            'status': self.status,
            'version': self.version,
            'owner_id': self.owner_id,
            'owner_name': self.owner.username if self.owner else None,
            'created_by': self.created_by,
            'creator_name': self.creator.username if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'item_count': len(self.items) if self.items else 0
        }


class RequirementItem(db.Model):
    """需求条目表"""
    __tablename__ = 'requirement_items'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    doc_id = Column(Integer, ForeignKey('requirement_documents.id'), nullable=False)
    parent_id = Column(Integer, ForeignKey('requirement_items.id'), nullable=True)
    identifier = Column(String(50), nullable=False)  # 如 REQ-001
    title = Column(String(500), nullable=False)
    description = Column(Text)
    priority = Column(Integer, default=2)  # 1-低, 2-中, 3-高
    status = Column(String(20), default='pending_review')  # pending_review, reviewed, approved, in_progress, completed, verified
    module = Column(String(100))
    owner_id = Column(Integer, ForeignKey('users.id'))
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    planned_version = Column(String(50))
    actual_version = Column(String(50))
    
    # 关系
    document = relationship("RequirementDocument", back_populates="items")
    parent = relationship("RequirementItem", remote_side=[id], backref="children")
    owner = relationship("User", foreign_keys=[owner_id])
    creator = relationship("User", foreign_keys=[created_by])
    comments = relationship("RequirementComment", back_populates="item", cascade="all, delete-orphan")
    links = relationship("RequirementLink", back_populates="requirement", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'doc_id': self.doc_id,
            'parent_id': self.parent_id,
            'identifier': self.identifier,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'module': self.module,
            'owner_id': self.owner_id,
            'owner_name': self.owner.username if self.owner else None,
            'created_by': self.created_by,
            'creator_name': self.creator.username if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'planned_version': self.planned_version,
            'actual_version': self.actual_version,
            'comment_count': len(self.comments) if self.comments else 0,
            'link_count': len(self.links) if self.links else 0
        }


class RequirementComment(db.Model):
    """需求评论表"""
    __tablename__ = 'requirement_comments'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    target_type = Column(String(20), nullable=False)  # document, item
    target_id = Column(Integer, nullable=False)
    item_id = Column(Integer, ForeignKey('requirement_items.id'), nullable=True)
    content = Column(Text, nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    reply_to = Column(Integer, ForeignKey('requirement_comments.id'), nullable=True)
    
    # 关系
    item = relationship("RequirementItem", back_populates="comments")
    creator = relationship("User", foreign_keys=[created_by])
    parent_comment = relationship("RequirementComment", remote_side=[id], backref="replies")
    
    def to_dict(self):
        return {
            'id': self.id,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'item_id': self.item_id,
            'content': self.content,
            'created_by': self.created_by,
            'creator_name': self.creator.username if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'reply_to': self.reply_to
        }


class RequirementLink(db.Model):
    """需求关联关系表"""
    __tablename__ = 'requirement_links'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    requirement_id = Column(Integer, ForeignKey('requirement_items.id'), nullable=False)
    target_type = Column(String(20), nullable=False)  # task, bug, test_case, code_commit
    target_id = Column(Integer, nullable=False)
    link_type = Column(String(20), default='implements')  # implements, verifies, affects, related
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    requirement = relationship("RequirementItem", back_populates="links")
    creator = relationship("User", foreign_keys=[created_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'requirement_id': self.requirement_id,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'link_type': self.link_type,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class RequirementVersion(db.Model):
    """需求文档版本历史表"""
    __tablename__ = 'requirement_versions'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    doc_id = Column(Integer, ForeignKey('requirement_documents.id'), nullable=False)
    version = Column(Integer, nullable=False)
    snapshot = Column(Text)  # JSON格式存储文档及条目快照
    change_summary = Column(Text)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("RequirementDocument", back_populates="versions")
    creator = relationship("User", foreign_keys=[created_by])

    def to_dict(self):
        return {
            'id': self.id,
            'doc_id': self.doc_id,
            'version': self.version,
            'change_summary': self.change_summary,
            'created_by': self.created_by,
            'creator_name': self.creator.username if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ==================== 测试管理模型 ====================

class TestSuite(db.Model):
    """测试集表"""
    __tablename__ = 'test_suites'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    parent_id = Column(Integer, ForeignKey('test_suites.id'))  # 父测试集ID，支持树形结构
    name = Column(String(200), nullable=False)
    description = Column(Text)
    type = Column(String(50), default='functional')  # 功能/性能/安全等
    status = Column(String(20), default='designing')  # 设计中/已评审/已废弃
    priority = Column(Integer, default=2)  # 1-低, 2-中, 3-高
    owner_id = Column(Integer, ForeignKey('users.id'))  # 负责人ID
    expected_duration = Column(Integer, default=0)  # 预计执行时间（分钟）
    version = Column(Integer, default=1)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", backref="test_suites")
    parent = relationship("TestSuite", remote_side=[id], backref="children")
    owner = relationship("User", foreign_keys=[owner_id])
    creator = relationship("User", foreign_keys=[created_by])
    cases = relationship("TestCase", back_populates="suite", cascade="all, delete-orphan")

    def to_dict(self, include_children=False, include_cases=False):
        result = {
            'id': self.id,
            'project_id': self.project_id,
            'parent_id': self.parent_id,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'status': self.status,
            'priority': self.priority,
            'owner_id': self.owner_id,
            'owner_name': self.owner.username if self.owner else None,
            'expected_duration': self.expected_duration,
            'version': self.version,
            'created_by': self.created_by,
            'creator_name': self.creator.username if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'case_count': len(self.cases) if self.cases else 0
        }
        if include_children and self.children:
            result['children'] = [child.to_dict(include_children=True, include_cases=include_cases) for child in self.children]
        if include_cases:
            result['cases'] = [case.to_dict() for case in self.cases] if self.cases else []
        return result


class TestCase(db.Model):
    """测试用例表"""
    __tablename__ = 'test_cases'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    suite_id = Column(Integer, ForeignKey('test_suites.id'), nullable=False)
    identifier = Column(String(50), nullable=False)  # 用例唯一标识，如 TC-001
    title = Column(String(500), nullable=False)
    description = Column(Text)  # 概述
    priority = Column(Integer, default=2)  # 0-P0, 1-P1, 2-P2, 3-P3
    type = Column(String(50), default='functional')  # 功能/性能/安全等
    status = Column(String(20), default='designing')  # 设计/待评审/已评审/已批准/废弃
    precondition = Column(Text)  # 前提条件
    test_data = Column(Text)  # 测试数据
    environment = Column(Text)  # 环境要求
    is_automated = Column(Boolean, default=False)
    automation_script = Column(String(500))  # 自动化脚本路径
    tags = Column(Text)  # 标签，逗号分隔
    estimated_duration = Column(Integer, default=0)  # 预计执行时间（分钟）
    designer_id = Column(Integer, ForeignKey('users.id'))  # 设计人ID
    reviewer_id = Column(Integer, ForeignKey('users.id'))  # 评审人ID
    approved_by = Column(Integer, ForeignKey('users.id'))  # 批准人ID
    version = Column(Integer, default=1)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    suite = relationship("TestSuite", back_populates="cases")
    designer = relationship("User", foreign_keys=[designer_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    approver = relationship("User", foreign_keys=[approved_by])
    creator = relationship("User", foreign_keys=[created_by])
    steps = relationship("TestStep", back_populates="test_case", cascade="all, delete-orphan", order_by="TestStep.step_number")
    results = relationship("TestResult", back_populates="test_case", cascade="all, delete-orphan")
    linked_requirements = relationship("TestCaseRequirementLink", back_populates="test_case", cascade="all, delete-orphan")

    def to_dict(self, include_steps=False, include_links=False):
        result = {
            'id': self.id,
            'suite_id': self.suite_id,
            'suite_name': self.suite.name if self.suite else None,
            'identifier': self.identifier,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'type': self.type,
            'status': self.status,
            'precondition': self.precondition,
            'test_data': self.test_data,
            'environment': self.environment,
            'is_automated': self.is_automated,
            'automation_script': self.automation_script,
            'tags': self.tags,
            'estimated_duration': self.estimated_duration,
            'designer_id': self.designer_id,
            'designer_name': self.designer.username if self.designer else None,
            'reviewer_id': self.reviewer_id,
            'reviewer_name': self.reviewer.username if self.reviewer else None,
            'approved_by': self.approved_by,
            'approver_name': self.approver.username if self.approver else None,
            'version': self.version,
            'created_by': self.created_by,
            'creator_name': self.creator.username if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'step_count': len(self.steps) if self.steps else 0
        }
        if include_steps:
            result['steps'] = [step.to_dict() for step in self.steps] if self.steps else []
        if include_links:
            result['linked_requirements'] = [link.to_dict() for link in self.linked_requirements] if self.linked_requirements else []
        return result


class TestStep(db.Model):
    """用例步骤表"""
    __tablename__ = 'test_steps'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey('test_cases.id'), nullable=False)
    step_number = Column(Integer, nullable=False)  # 步骤序号
    action = Column(Text, nullable=False)  # 操作描述
    expected_result = Column(Text)  # 预期结果
    attachments = Column(Text)  # 附件列表，JSON格式
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    test_case = relationship("TestCase", back_populates="steps")

    def to_dict(self):
        attachments_list = []
        if self.attachments:
            try:
                attachments_list = json.loads(self.attachments)
            except:
                pass
        return {
            'id': self.id,
            'case_id': self.case_id,
            'step_number': self.step_number,
            'action': self.action,
            'expected_result': self.expected_result,
            'attachments': attachments_list,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class TestExecution(db.Model):
    """测试执行记录表"""
    __tablename__ = 'test_executions'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    suite_id = Column(Integer, ForeignKey('test_suites.id'))  # 可为空，表示按需选择用例执行
    name = Column(String(200), nullable=False)  # 执行名称，如"回归测试-2024-03-20"
    status = Column(String(20), default='in_progress')  # 进行中/已完成
    executor_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # 执行人ID
    started_at = Column(DateTime, default=datetime.utcnow)  # 执行开始时间
    completed_at = Column(DateTime)  # 完成时间
    environment = Column(String(100))  # 执行环境
    test_version = Column(String(100))  # 测试版本
    build_number = Column(String(100))  # 构建号
    notes = Column(Text)  # 备注
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", backref="test_executions")
    suite = relationship("TestSuite", backref="executions")
    executor = relationship("User", foreign_keys=[executor_id])
    results = relationship("TestResult", back_populates="execution", cascade="all, delete-orphan")

    def to_dict(self, include_results=False):
        result = {
            'id': self.id,
            'project_id': self.project_id,
            'suite_id': self.suite_id,
            'suite_name': self.suite.name if self.suite else None,
            'name': self.name,
            'status': self.status,
            'executor_id': self.executor_id,
            'executor_name': self.executor.username if self.executor else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'environment': self.environment,
            'test_version': self.test_version,
            'build_number': self.build_number,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'result_count': len(self.results) if self.results else 0,
            'passed_count': sum(1 for r in self.results if r.result == 'passed') if self.results else 0,
            'failed_count': sum(1 for r in self.results if r.result == 'failed') if self.results else 0,
            'blocked_count': sum(1 for r in self.results if r.result == 'blocked') if self.results else 0,
            'skipped_count': sum(1 for r in self.results if r.result == 'skipped') if self.results else 0
        }
        if include_results:
            result['results'] = [r.to_dict() for r in self.results] if self.results else []
        return result


class TestResult(db.Model):
    """用例执行结果表"""
    __tablename__ = 'test_results'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, ForeignKey('test_executions.id'), nullable=False)
    case_id = Column(Integer, ForeignKey('test_cases.id'), nullable=False)
    result = Column(String(20), nullable=False)  # passed/failed/blocked/skipped
    actual_result = Column(Text)  # 实际结果
    defect_id = Column(Integer, ForeignKey('bugs.id'))  # 关联的缺陷ID
    executor_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # 执行人ID
    executed_at = Column(DateTime, default=datetime.utcnow)  # 执行时间
    duration = Column(Integer, default=0)  # 执行时长（秒）
    screenshots = Column(Text)  # 截图列表，JSON格式
    notes = Column(Text)  # 备注
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    execution = relationship("TestExecution", back_populates="results")
    test_case = relationship("TestCase", back_populates="results")
    executor = relationship("User", foreign_keys=[executor_id])
    defect = relationship("Bug")

    def to_dict(self):
        screenshots_list = []
        if self.screenshots:
            try:
                screenshots_list = json.loads(self.screenshots)
            except:
                pass
        return {
            'id': self.id,
            'execution_id': self.execution_id,
            'case_id': self.case_id,
            'case_identifier': self.test_case.identifier if self.test_case else None,
            'case_title': self.test_case.title if self.test_case else None,
            'result': self.result,
            'actual_result': self.actual_result,
            'defect_id': self.defect_id,
            'defect_title': self.defect.title if self.defect else None,
            'executor_id': self.executor_id,
            'executor_name': self.executor.username if self.executor else None,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'duration': self.duration,
            'screenshots': screenshots_list,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class TestCaseRequirementLink(db.Model):
    """测试用例与需求关联表"""
    __tablename__ = 'test_case_requirement_links'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    test_case_id = Column(Integer, ForeignKey('test_cases.id'), nullable=False)
    requirement_id = Column(Integer, ForeignKey('requirement_items.id'), nullable=False)
    link_type = Column(String(50), default='tests')  # tests/covers
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)

    test_case = relationship("TestCase", back_populates="linked_requirements")
    requirement = relationship("RequirementItem", backref="test_case_links")
    creator = relationship("User", foreign_keys=[created_by])

    def to_dict(self):
        return {
            'id': self.id,
            'test_case_id': self.test_case_id,
            'requirement_id': self.requirement_id,
            'requirement_identifier': self.requirement.identifier if self.requirement else None,
            'requirement_title': self.requirement.title if self.requirement else None,
            'link_type': self.link_type,
            'created_by': self.created_by,
            'creator_name': self.creator.username if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AuditLog(db.Model):
    """审计日志模型 - 记录所有用户操作"""
    __tablename__ = 'audit_logs'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    action = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(Integer, nullable=True, index=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship('User', backref='audit_logs', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class WorkLog(db.Model):
    """工作日志模型 - 记录用户个人工作日志"""
    __tablename__ = 'work_logs'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    log_date = Column(DateTime, nullable=False)
    work_type = Column(String(50), default='daily')
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    hours_spent = Column(Float, default=0.0)
    status = Column(String(20), default='draft')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship('User', backref='work_logs', lazy=True)
    project = relationship('Project', backref='work_logs', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'created_by': self.user_id,
            'title': self.title,
            'content': self.content,
            'log_date': self.log_date.isoformat() if self.log_date else None,
            'work_type': self.work_type,
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else None,
            'hours_spent': self.hours_spent,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_name': self.user.username if self.user else None,
            'creator_name': self.user.username if self.user else None
        }


class KnowledgeCategory(db.Model):
    """知识库分类模型"""
    __tablename__ = 'knowledge_categories'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey('knowledge_categories.id'), index=True)
    sort_order = Column(Integer, default=0)
    article_count = Column(Integer, default=0)
    is_archived = Column(Integer, default=0)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    parent = relationship('KnowledgeCategory', remote_side=[id], backref='children')
    creator = relationship('User', backref='knowledge_categories')

    def to_dict(self, include_children=False, include_article_count=True):
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description or '',
            'parent_id': self.parent_id,
            'sort_order': self.sort_order,
            'is_archived': bool(self.is_archived),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_article_count:
            result['article_count'] = self.article_count or 0
        if include_children and hasattr(self, 'children') and self.children:
            result['children'] = [child.to_dict(include_children=True, include_article_count=include_article_count) for child in sorted(self.children, key=lambda x: x.sort_order or 0)]
        return result


class KnowledgeArticle(db.Model):
    """知识库文章模型"""
    __tablename__ = 'knowledge_articles'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    cover_image = Column(String(500))
    category_id = Column(Integer, ForeignKey('knowledge_categories.id'), index=True)
    tags = Column(Text)
    author_id = Column(Integer, ForeignKey('users.id'), index=True)
    author_name = Column(String(100))
    status = Column(String(20), default='draft')
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    is_public = Column(Integer, default=1)
    is_pinned = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship('KnowledgeCategory', backref='articles')
    author = relationship('User', backref='knowledge_articles')

    def _parse_tags(self):
        """解析标签 JSON，处理异常情况"""
        if not self.tags:
            return []
        try:
            return json.loads(self.tags)
        except json.JSONDecodeError:
            return []

    def to_dict(self, include_content=False, comment_count=None):
        if comment_count is None:
            from sqlalchemy import func
            comment_count = db.session.query(func.count(KnowledgeComment.id)).filter(
                KnowledgeComment.article_id == self.id
            ).scalar() or 0
        
        result = {
            'id': self.id,
            'title': self.title,
            'summary': self.summary or '',
            'cover_image': self.cover_image or '',
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else '未分类',
            'category_path': self._get_category_path(),
            'tags': self._parse_tags(),
            'author_id': self.author_id,
            'author_name': self.author_name or '未知',
            'author_avatar': self.author.avatar if self.author else None,
            'status': self.status or 'draft',
            'view_count': self.view_count,
            'like_count': self.like_count,
            'comment_count': comment_count,
            'is_public': bool(self.is_public),
            'is_pinned': bool(self.is_pinned),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_content:
            result['content'] = self.content
        return result

    def _get_category_path(self):
        if not self.category:
            return '未分类'
        path_parts = [self.category.name]
        parent = self.category.parent
        while parent:
            path_parts.insert(0, parent.name)
            parent = parent.parent
        return ' > '.join(path_parts)


class KnowledgeAttachment(db.Model):
    """知识库附件模型"""
    __tablename__ = 'knowledge_attachments'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('knowledge_articles.id'), index=True, nullable=False)
    filename = Column(String(255), nullable=False)
    storage_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    article = relationship('KnowledgeArticle', backref='attachments')

    def to_dict(self):
        return {
            'id': self.id,
            'article_id': self.article_id,
            'filename': self.filename,
            'file_size': self.file_size,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


def init_models():
    """初始化模型类（现在所有模型都在这里定义）"""
    # 模型已经直接定义，无需额外初始化
    pass

# 文件上传辅助函数
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_category(filename):
    """根据文件扩展名获取文件类别"""
    if '.' not in filename:
        return 'unknown'
    ext = filename.rsplit('.', 1)[1].lower()
    if ext in ALLOWED_IMAGE_EXTENSIONS:
        return 'images'
    return 'unknown'

# 配置日志
logger = logging.getLogger(__name__)

# 初始化日志系统
try:
    from backend.logging_config import log_manager
    log_manager.init_app(app)
except ImportError:
    try:
        from logging_config import log_manager
        log_manager.init_app(app)
    except ImportError:
        pass  # 日志配置可选

# 导入邮件服务
try:
    from backend.services.email_service import EmailService
    email_service = EmailService()
except ImportError:
    try:
        from services.email_service import EmailService
        email_service = EmailService()
    except ImportError:
        email_service = None  # 邮件服务可选

# 邮件配置 - 优先从 system_config.json 读取，否则使用环境变量
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api', 'system_config.json')

def load_mail_config():
    """从配置文件加载邮件配置"""
    config = {
        'EMAIL_ENABLED': os.environ.get('EMAIL_ENABLED', 'false').lower() == 'true',
        'SMTP_SERVER': os.environ.get('SMTP_SERVER', 'smtp.vip.163.com'),
        'SMTP_PORT': int(os.environ.get('SMTP_PORT', 465)),
        'SMTP_USERNAME': os.environ.get('SMTP_USERNAME', ''),
        'SMTP_PASSWORD': os.environ.get('SMTP_PASSWORD', ''),
        'FROM_EMAIL': os.environ.get('FROM_EMAIL', ''),
        'USE_SSL': os.environ.get('USE_SSL', 'true').lower() == 'true'
    }

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                system_config = json.load(f)
            mail_config = system_config.get('mail_server', {})
            if mail_config.get('enabled'):
                config['EMAIL_ENABLED'] = True
                config['SMTP_SERVER'] = mail_config.get('host', config['SMTP_SERVER'])
                config['SMTP_PORT'] = mail_config.get('port', config['SMTP_PORT'])
                config['SMTP_USERNAME'] = mail_config.get('username', config['SMTP_USERNAME'])
                config['SMTP_PASSWORD'] = mail_config.get('password', config['SMTP_PASSWORD'])
                config['FROM_EMAIL'] = mail_config.get('from_address', config['FROM_EMAIL'])
                config['USE_SSL'] = mail_config.get('use_ssl', True)
        except Exception as e:
            logger.warning(f"读取邮件配置文件失败: {e}")

    return config

EMAIL_CONFIG = load_mail_config()

# 创建log
def create_audit_log(user_id, action, resource_type, resource_id=None, details="", request=None):
    """创建log记录（简化版本，仅记录日志）"""
    try:
        # 简化实现：只记录日志，不创建数据库记录
        ip_address = request.remote_addr if request else None
        user_agent = request.headers.get('User-Agent') if request else None
        
        logger.info(f"log - 用户ID: {user_id}, 操作: {action}, 资源类型: {resource_type}, "
                   f"资源ID: {resource_id}, 详情: {details}, IP: {ip_address}")
        
        # 返回一个简单的字典而不是数据库对象
        return {
            'user_id': user_id,
            'action': action,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'details': details,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'created_at': datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"创建log失败: {str(e)}")
        return None

# 权限装饰器
def require_permission(permission_name):
    """权限检查装饰器"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            # 使用全局User模型
            current_user = User.query.get(current_user_id)
            
            if not current_user:
                return jsonify({'error': '用户不存在'}), 404
            
            if not current_user.can(permission_name):
                return jsonify({'error': '权限不足'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# API 路由导入和注册（使用延迟导入避免循环导入）
_api_blueprints_registered = False

def register_api_blueprints():
    """延迟注册 API 蓝图以避免循环导入"""
    global _api_blueprints_registered
    if _api_blueprints_registered:
        return
    
    # 导入 api_bp 和所有获取子蓝图的函数
    from restful_api import (
        api_bp, get_avatar_bp, get_auth_bp, get_bugs_bp, get_materials_bp,
        get_contracts_bp, get_projects_bp, get_statistics_bp, get_users_bp,
        get_notifications_bp, get_attendance_bp, get_system_bp, get_activities_bp,
        get_work_logs_bp, get_bug_statistics_bp, get_delivery_tracking_bp,
        get_contracts_enhanced_bp, get_contracts_statistics_bp, get_requirements_bp,
        get_test_management_bp, get_audit_bp, get_search_bp, get_performance_bp,
        get_health_bp, get_docs_bp, get_export_bp, get_todos_bp, get_project_logs_bp,
        get_knowledge_bp, get_data_import_export_bp, get_monitoring_bp, get_risks_bp,
        get_personal_plan_bp
    )
    
    # 注册所有子蓝图到 api_bp，跳过有循环导入问题的蓝图
    blueprints_to_register = [
        (get_avatar_bp, '/avatar'),
        (get_auth_bp, None),
        (get_bugs_bp, None),
        (get_materials_bp, None),
        (get_contracts_bp, None),
        (get_projects_bp, None),
        (get_statistics_bp, None),
        (get_users_bp, None),
        (get_notifications_bp, None),
        (get_attendance_bp, None),
        (get_system_bp, None),
        (get_activities_bp, None),
        (get_work_logs_bp, None),
        (get_bug_statistics_bp, None),
        (get_delivery_tracking_bp, None),
        (get_contracts_enhanced_bp, None),
        (get_contracts_statistics_bp, None),
        (get_requirements_bp, None),
        (get_test_management_bp, None),
        (get_audit_bp, None),
        (get_search_bp, None),
        (get_performance_bp, None),
        (get_health_bp, None),
        (get_docs_bp, None),
        (get_export_bp, None),
        (get_todos_bp, None),
        (get_project_logs_bp, None),
        (get_knowledge_bp, None),
        (get_data_import_export_bp, None),
        (get_monitoring_bp, None),
        (get_risks_bp, None),
        (get_personal_plan_bp, None),
    ]
    
    for get_bp_func, url_prefix in blueprints_to_register:
        try:
            bp = get_bp_func()
            if url_prefix:
                api_bp.register_blueprint(bp, url_prefix=url_prefix)
            else:
                api_bp.register_blueprint(bp)
        except ImportError as e:
            print(f"Skipped blueprint {get_bp_func.__name__}: {e}")
            continue
    
    # 注册 api_bp 到 Flask app
    app.register_blueprint(api_bp)
    _api_blueprints_registered = True
    print("API blueprints registered successfully")

    # 注册全局错误处理
    @app.errorhandler(500)
    def app_internal_error(error):
        import traceback
        logger.error(f"App 500 error: {error}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': '服务器内部错误',
            'code': 'INTERNAL_ERROR'
        }), 500

    @app.errorhandler(Exception)
    def app_handle_exception(error):
        import traceback
        logger.error(f"App unhandled exception: {error}\n{traceback.format_exc()}")
        # 如果是HTTP异常，使用其状态码
        from werkzeug.exceptions import HTTPException
        if isinstance(error, HTTPException):
            return jsonify({
                'success': False,
                'error': error.description or str(error),
                'code': f'HTTP_{error.code}'
            }), error.code
        return jsonify({
            'success': False,
            'error': f'请求处理失败: {str(error)}',
            'code': 'UNHANDLED_ERROR'
        }), 500

# 注意：API 蓝图在 if __name__ == '__main__': 块中注册
# 对于 WSGI 服务器，请在 wsgi.py 中调用 register_api_blueprints()

# 邮件通知功能
def send_email_notification(to_email, subject, body, html_body=None):
    """发送邮件通知"""
    if not EMAIL_CONFIG['EMAIL_ENABLED']:
        logger.info(f"邮件通知已禁用。将发送: {subject} 到 {to_email}")
        return True

    use_ssl = EMAIL_CONFIG.get('USE_SSL', True)

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = EMAIL_CONFIG['FROM_EMAIL']
        msg['To'] = to_email

        text_part = MIMEText(body, 'plain', 'utf-8')
        msg.attach(text_part)

        if html_body:
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(html_part)

        if use_ssl:
            with smtplib.SMTP_SSL(EMAIL_CONFIG['SMTP_SERVER'], EMAIL_CONFIG['SMTP_PORT']) as server:
                server.login(EMAIL_CONFIG['SMTP_USERNAME'], EMAIL_CONFIG['SMTP_PASSWORD'])
                server.send_message(msg)
        else:
            with smtplib.SMTP(EMAIL_CONFIG['SMTP_SERVER'], EMAIL_CONFIG['SMTP_PORT']) as server:
                server.starttls()
                server.login(EMAIL_CONFIG['SMTP_USERNAME'], EMAIL_CONFIG['SMTP_PASSWORD'])
                server.send_message(msg)

        logger.info(f"邮件发送成功到 {to_email}: {subject}")
        return True

    except Exception as e:
        logger.error(f"发送邮件到 {to_email} 失败: {str(e)}")
        return False

# Webhook通知功能
def send_webhook_notification(webhook_url, data):
    """发送Webhook通知"""
    try:
        payload = {
            'event': data.get('event', 'bug_update'),
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }
        
        response = requests.post(
            webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"Webhook发送成功到 {webhook_url}")
            return True
        else:
            logger.error(f"Webhook发送失败，状态码 {response.status_code}: {webhook_url}")
            return False
            
    except Exception as e:
        logger.error(f"发送Webhook到 {webhook_url} 失败: {str(e)}")
        return False

# 创建通知
def create_notification(user_id, notification_type, title, content, related_bug_id=None, related_comment_id=None):
    """创建并发送通知"""
    try:
        # 创建数据库通知
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            content=content,
            related_bug_id=related_bug_id,
            related_comment_id=related_comment_id,
            is_read=False,
            created_at=datetime.utcnow()
        )
        db.session.add(notification)
        db.session.commit()
        
        # 获取用户邮箱并检查是否需要发送邮件
        user = User.query.get(user_id)
        should_send_email = False
        
        if user and user.email:
            # 检查用户是否启用了邮箱通知
            email_enabled = getattr(user, 'email_notification_enabled', True)
            logger.info(f"[邮件通知检查] 用户: {user.username}, email_notification_enabled: {email_enabled}, notification_type: {notification_type}")
            
            if email_enabled:
                # 根据通知类型检查是否需要发送邮件
                if notification_type == 'bug_assigned':
                    should_send_email = getattr(user, 'email_on_bug_assigned', True)
                elif notification_type == 'bug_closed':
                    should_send_email = getattr(user, 'email_on_bug_closed', True)
                elif notification_type in ['comment_mention', 'system']:
                    should_send_email = True
            
            logger.info(f"[邮件通知检查] should_send_email: {should_send_email}")
            
            if should_send_email:
                # 发送邮件通知
                email_subject = f"[TOPO系统] {title}"
                email_body = f"""
亲爱的 {user.username}，

{content}

此邮件由TOPO系统自动发送。
"""

                html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #007bff;">TOPO系统通知</h2>
        <p>亲爱的 <strong>{user.username}</strong>，</p>
        <p>{content}</p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
        <p style="font-size: 12px; color: #666;">
            此邮件由TOPO系统自动发送。<br>
            请勿回复此邮件。
        </p>
    </div>
</body>
</html>
"""
                
                send_email_notification(user.email, email_subject, email_body, html_body)
            else:
                logger.info(f"用户 {user.username} 邮件通知已关闭，不发送: {title}")
        
        return notification
        
    except Exception as e:
        logger.error(f"为用户 {user_id} 创建通知失败: {str(e)}")
        return None

# 提取@提及
def extract_mentions(text):
    """从文本中提取@提及的用户名"""
    import re
    # 匹配 @username 格式
    pattern = r'@(\w+)'
    mentions = re.findall(pattern, text)
    return mentions

# 发送@提及通知
def send_mention_notifications(comment_text, comment_id, bug_id, created_by_user_id):
    """发送@提及通知"""
    try:
        mentions = extract_mentions(comment_text)
        if not mentions:
            return
        
        # 获取当前用户信息
        current_user = User.query.get(created_by_user_id)
        if not current_user:
            return
            
        # 获取Bug信息
        bug = Bug.query.get(bug_id)
        if not bug:
            return
            
        # 为每个被提及的用户创建通知
        for username in mentions:
            user = User.query.filter_by(username=username).first()
            if user and user.id != created_by_user_id:  # 不给自己发通知
                title = f"您被@{current_user.username}在Bug中提及"
                content = f"用户 {current_user.username} 在Bug #{bug.id} '{bug.title}' 的评论中提到了您：\n\n{comment_text}"
                
                create_notification(
                    user_id=user.id,
                    notification_type="comment_mention",
                    title=title,
                    content=content,
                    related_bug_id=bug_id,
                    related_comment_id=comment_id
                )
                
                logger.info(f"已发送提及通知给用户 {user.username}")
                
    except Exception as e:
        logger.error(f"发送提及通知失败: {str(e)}")

# 构建审批链
def build_approval_chain(user_id, leave_type, start_date, end_date):
    """构建请假审批链"""
    try:
        # 使用全局User模型
        user = User.query.get(user_id)
        if not user:
            return []
        
        # 计算请假天数
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        total_days = (end_date - start_date).days + 1
        
        approval_chain = []
        
        # 1天以内：部门主管审批
        if total_days <= 1:
            department_manager = User.query.filter_by(
                department=user.department, 
                role=UserRole.PROJECT_MANAGER.value
            ).first()
            if department_manager:
                approval_chain.append({
                    'level': 1,
                    'approver_id': department_manager.id,
                    'approver_name': department_manager.username,
                    'role': '部门主管',
                    'required': True
                })
        
        # 1-3天：部门负责人审批
        elif total_days <= 3:
            department_head = User.query.filter_by(
                department=user.department,
                role=UserRole.ADMIN.value
            ).first()
            if department_head:
                approval_chain.append({
                    'level': 1,
                    'approver_id': department_head.id,
                    'approver_name': department_head.username,
                    'role': '部门负责人',
                    'required': True
                })
        
        # 3天以上或特殊假期：需要HR复核、分管领导批准
        else:
            # 部门负责人
            department_head = User.query.filter_by(
                department=user.department,
                role=UserRole.ADMIN.value
            ).first()
            if department_head:
                approval_chain.append({
                    'level': 1,
                    'approver_id': department_head.id,
                    'approver_name': department_head.username,
                    'role': '部门负责人',
                    'required': True
                })
            
            # HR复核
            hr_manager = User.query.filter_by(role=UserRole.HR.value).first()
            if hr_manager:
                approval_chain.append({
                    'level': 2,
                    'approver_id': hr_manager.id,
                    'approver_name': hr_manager.username,
                    'role': 'HR复核',
                    'required': leave_type in ['maternity', 'marriage', 'paternity']  # 特殊假期需要HR复核
                })
            
            # 部门经理
            dept_manager = User.query.filter_by(role=UserRole.DEPARTMENT_MANAGER.value).first()
            if dept_manager:
                approval_chain.append({
                    'level': 3,
                    'approver_id': dept_manager.id,
                    'approver_name': dept_manager.username,
                    'role': '部门经理',
                    'required': total_days > 3
                })
        
        return approval_chain
    except Exception as e:
        logger.error(f"构建审批链错误: {str(e)}")
        return []

# 发送审批通知
def send_approval_notification(application):
    """发送审批通知"""
    try:
        # 这里可以实现邮件、钉钉、短信等通知方式
        # 目前先记录日志
        logger.info(f"发送审批通知: 申请ID {application.id}, 审批人 {application.approver_id}")
    except Exception as e:
        logger.error(f"发送审批通知错误: {str(e)}")

# 发送审批通知（包含邮件）
def send_approval_notification_with_email(application):
    """发送审批通知（包含邮件通知）"""
    try:
        # 获取申请人和审批人信息
        # 使用全局User模型
        applicant = User.query.get(application.user_id)
        approver = User.query.get(application.approver_id)
        
        if not applicant or not approver:
            logger.error(f"无法找到申请人或审批人信息: 申请ID {application.id}")
            return
        
        # 发送邮件通知
        if approver.email:
            subject = f"[请假审批] {applicant.username}的请假申请待审批"
            
            # 邮件正文
            body = f"""
尊敬的 {approver.username}：

您收到一个新的请假申请需要审批：

申请人：{applicant.username}
请假类型：{application.leave_type}
请假时间：{application.start_date} 至 {application.end_date}
请假天数：{(application.end_date - application.start_date).days + 1}天
请假事由：{application.reason}

请登录系统进行审批：
http://localhost:5173/attendance/approval

此邮件由TOPO系统自动发送。
"""
            
            # HTML格式邮件
            html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
        <h2 style="color: #007bff; text-align: center;">请假审批通知</h2>
        
        <p>尊敬的 <strong>{approver.username}</strong>：</p>
        
        <p>您收到一个新的请假申请需要审批：</p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
            <p><strong>申请人：</strong>{applicant.username}</p>
            <p><strong>请假类型：</strong>{application.leave_type}</p>
            <p><strong>请假时间：</strong>{application.start_date} 至 {application.end_date}</p>
            <p><strong>请假天数：</strong>{(application.end_date - application.start_date).days + 1}天</p>
            <p><strong>请假事由：</strong>{application.reason}</p>
        </div>
        
        <p style="text-align: center;">
            <a href="http://localhost:5173/attendance/approval" 
               style="display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px;">
                前往审批页面
            </a>
        </p>
        
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
        <p style="font-size: 12px; color: #666;">
            此邮件由TOPO系统自动发送。<br>
            请勿回复此邮件。
        </p>
    </div>
</body>
</html>
"""
            
            send_email_notification(approver.email, subject, body, html_body)
            
    except Exception as e:
        logger.error(f"发送审批邮件通知错误: {str(e)}")

# 数据库迁移：添加缺失的列
def migrate_database():
    """检查并添加缺失的数据库列"""
    try:
        from sqlalchemy import inspect
        
        inspector = inspect(db.engine)
        
        # 检查 users 表
        if inspector.has_table('users'):
            existing_columns = [col['name'] for col in inspector.get_columns('users')]
            
            # 定义需要检查的列及其配置
            columns_to_check = {
                'custom_permissions': 'TEXT DEFAULT \'{}\'',
                'is_super_admin': 'BOOLEAN DEFAULT 0',
                'email_notification_enabled': 'BOOLEAN DEFAULT 1',
                'email_on_bug_assigned': 'BOOLEAN DEFAULT 1',
                'email_on_bug_closed': 'BOOLEAN DEFAULT 1',
                'accessible_modules': 'TEXT DEFAULT NULL',
            }
            
            for col_name, col_type in columns_to_check.items():
                if col_name not in existing_columns:
                    try:
                        db.session.execute(db.text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                        db.session.commit()
                        logger.info(f"数据库迁移成功：已添加缺失列 {col_name}")
                    except Exception as e:
                        db.session.rollback()
                        logger.warning(f"添加列 {col_name} 失败（可能已存在）: {str(e)}")
        
        # 检查 leave_applications 表 - 添加缺失的 days 列
        if inspector.has_table('leave_applications'):
            existing_columns = [col['name'] for col in inspector.get_columns('leave_applications')]
            
            if 'days' not in existing_columns:
                try:
                    db.session.execute(db.text("ALTER TABLE leave_applications ADD COLUMN days FLOAT DEFAULT 0"))
                    db.session.commit()
                    logger.info("数据库迁移成功：已添加缺失列 days 到 leave_applications 表")
                except Exception as e:
                    db.session.rollback()
                    logger.warning(f"添加列 days 失败（可能已存在）: {str(e)}")
        
        # 迁移部门和职位数据到新表
        if inspector.has_table('users') and inspector.has_table('departments'):
            try:
                # 获取所有不重复的部门
                existing_departments = db.session.execute(
                    db.text("SELECT DISTINCT department FROM users WHERE department IS NOT NULL AND department != ''")
                ).fetchall()
                
                for dept in existing_departments:
                    dept_name = dept[0]
                    if dept_name:
                        # 检查是否已存在
                        existing = db.session.execute(
                            db.text("SELECT id FROM departments WHERE name = :name"),
                            {'name': dept_name}
                        ).fetchone()
                        if not existing:
                            db.session.execute(
                                db.text("INSERT INTO departments (name, created_at, updated_at) VALUES (:name, datetime('now'), datetime('now'))"),
                                {'name': dept_name}
                            )
                
                db.session.commit()
                logger.info("部门数据迁移成功")
            except Exception as e:
                db.session.rollback()
                logger.warning(f"部门数据迁移失败: {str(e)}")
        
        if inspector.has_table('users') and inspector.has_table('positions'):
            try:
                # 获取所有不重复的职位
                existing_positions = db.session.execute(
                    db.text("SELECT DISTINCT position FROM users WHERE position IS NOT NULL AND position != ''")
                ).fetchall()

                # 定义常见管理职位名称（中英文）
                admin_position_names = ['admin', 'manager', 'administrator', '系统管理员', '经理', '管理员', '部门经理']
                manager_position_names = ['manager', 'project_manager', 'department_manager', '经理', '项目经理', '部门经理', '主管']

                for pos in existing_positions:
                    pos_name = pos[0]
                    if pos_name:
                        # 检查是否已存在
                        existing = db.session.execute(
                            db.text("SELECT id FROM positions WHERE name = :name"),
                            {'name': pos_name}
                        ).fetchone()
                        if not existing:
                            # 判断职位是否为管理员或经理
                            pos_name_lower = pos_name.lower()
                            is_admin = any(admin_name in pos_name_lower or pos_name_lower in admin_name
                                         for admin_name in admin_position_names)
                            is_manager = any(manager_name in pos_name_lower or pos_name_lower in manager_position_names
                                           for manager_name in manager_position_names)

                            db.session.execute(
                                db.text("INSERT INTO positions (name, is_admin, is_manager, permissions, created_at, updated_at) VALUES (:name, :is_admin, :is_manager, :permissions, datetime('now'), datetime('now'))"),
                                {
                                    'name': pos_name,
                                    'is_admin': is_admin,
                                    'is_manager': is_manager,
                                    'permissions': '[]'
                                }
                            )
                            logger.info(f"创建职位: {pos_name}, is_admin={is_admin}, is_manager={is_manager}")

                db.session.commit()
                logger.info("职位数据迁移成功")

                # 修复已存在职位的权限（为Manager等职位设置正确的is_admin和is_manager）
                try:
                    all_positions = db.session.execute(
                        db.text("SELECT id, name, is_admin, is_manager FROM positions")
                    ).fetchall()

                    for pos_id, pos_name, current_is_admin, current_is_manager in all_positions:
                        pos_name_lower = pos_name.lower()
                        should_be_admin = any(admin_name in pos_name_lower or pos_name_lower in admin_name
                                             for admin_name in admin_position_names)
                        should_be_manager = any(manager_name in pos_name_lower or pos_name_lower in manager_name
                                               for manager_name in manager_position_names)

                        # 如果当前权限与应该有的权限不一致，则更新
                        if current_is_admin != should_be_admin or current_is_manager != should_be_manager:
                            db.session.execute(
                                db.text("UPDATE positions SET is_admin = :is_admin, is_manager = :is_manager WHERE id = :id"),
                                {
                                    'id': pos_id,
                                    'is_admin': should_be_admin,
                                    'is_manager': should_be_manager
                                }
                            )
                            logger.info(f"更新职位权限: {pos_name}, is_admin={should_be_admin}, is_manager={should_be_manager}")

                    db.session.commit()
                    logger.info("职位权限修复完成")
                except Exception as e:
                    db.session.rollback()
                    logger.warning(f"职位权限修复失败: {str(e)}")

            except Exception as e:
                db.session.rollback()
                logger.warning(f"职位数据迁移失败: {str(e)}")

            try:
                from models.permissions import DEFAULT_ROLES, PermissionCodes
                import json

                default_positions = [
                    {'name': '系统管理员', 'is_admin': True, 'is_manager': True, 'permissions': 'all'},
                    {'name': '经理', 'is_admin': True, 'is_manager': True, 'permissions': 'all'},
                    {'name': '项目经理', 'is_admin': False, 'is_manager': True, 'permissions': json.dumps(DEFAULT_ROLES.get('project_manager', {}).get('permissions', []))},
                    {'name': '测试工程师', 'is_admin': False, 'is_manager': False, 'permissions': json.dumps(DEFAULT_ROLES.get('test_engineer', {}).get('permissions', []))},
                    {'name': '软件工程师', 'is_admin': False, 'is_manager': False, 'permissions': json.dumps(DEFAULT_ROLES.get('software_engineer', {}).get('permissions', []))},
                    {'name': '普通用户', 'is_admin': False, 'is_manager': False, 'permissions': json.dumps(DEFAULT_ROLES.get('user', {}).get('permissions', []))},
                    {'name': '人事专员', 'is_admin': False, 'is_manager': True, 'permissions': json.dumps(DEFAULT_ROLES.get('hr', {}).get('permissions', []))},
                    {'name': '部门经理', 'is_admin': False, 'is_manager': True, 'permissions': json.dumps(DEFAULT_ROLES.get('department_manager', {}).get('permissions', []))},
                ]

                for pos_data in default_positions:
                    existing = db.session.execute(
                        db.text("SELECT id FROM positions WHERE name = :name"),
                        {'name': pos_data['name']}
                    ).fetchone()
                    if not existing:
                        perm_value = pos_data['permissions']
                        if perm_value != 'all':
                            perm_value = json.dumps(pos_data['permissions'])
                        db.session.execute(
                            db.text("INSERT INTO positions (name, is_admin, is_manager, permissions, created_at, updated_at) VALUES (:name, :is_admin, :is_manager, :permissions, datetime('now'), datetime('now'))"),
                            {
                                'name': pos_data['name'],
                                'is_admin': pos_data['is_admin'],
                                'is_manager': pos_data['is_manager'],
                                'permissions': perm_value
                            }
                        )

                db.session.commit()
                logger.info("默认职位创建成功")
            except Exception as e:
                db.session.rollback()
                logger.warning(f"创建默认职位失败: {str(e)}")

        logger.info("数据库迁移检查完成")
    except Exception as e:
        logger.error(f"数据库迁移检查失败: {str(e)}")

# 初始化数据库和创建示例数据
def init_db():
    """初始化数据库"""
    try:
        with app.app_context():
            # 初始化模型类，确保只创建一次
            init_models()
            
            # 创建所有数据库表
            db.create_all()
            
            # 执行数据库迁移，添加缺失的列
            migrate_database()
            
            logger.info("数据库表创建完成")
            
            # 创建基本的默认用户（如果不存在）
            try:
                # 检查是否已存在管理员用户
                existing_admin = User.query.filter_by(username='admin').first()
                if not existing_admin:
                    # 创建默认管理员用户
                    import secrets
                    salt = secrets.token_hex(16)
                    admin_user = User(
                        username='admin',
                        email='admin@example.com',
                        role=UserRole.ADMIN.value,
                        is_admin=True,
                        is_super_admin=True,
                        position='系统管理员',
                        department='',
                        salt=salt
                    )
                    admin_user.set_password('admin123')

                    # 添加到数据库
                    db.session.add(admin_user)
                    db.session.commit()

                    logger.info("默认管理员用户创建成功: username=admin, email=admin@example.com, password=admin123")
                else:
                    # 更新已存在的admin用户为系统管理员
                    if not existing_admin.is_super_admin:
                        existing_admin.is_super_admin = True
                        existing_admin.is_admin = True
                        existing_admin.position = '系统管理员'
                        existing_admin.department = ''
                        db.session.commit()
                        logger.info("已更新admin用户为系统管理员")
                    logger.info("管理员用户已存在，跳过创建")
                    
            except Exception as e:
                logger.warning(f"创建默认用户失败: {str(e)}")
                db.session.rollback()
                # 继续执行，不中断应用启动
            
            logger.info("数据库初始化完成")

            # 创建测试数据 - 已禁用
            # create_test_data()
            
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        # 不抛出异常，让应用能够继续启动

# JWT装饰器延迟导入函数
def get_jwt_required():
    """延迟导入jwt_required装饰器"""
    from flask_jwt_extended import jwt_required
    return jwt_required

def get_jwt_identity():
    """延迟导入get_jwt_identity函数"""
    from flask_jwt_extended import get_jwt_identity as jwt_identity_func
    return jwt_identity_func()

# 主应用入口
if __name__ == '__main__':
    # 初始化扩展
    init_extensions(app)
    
    # 初始化数据库
    init_db()
    
    # 注册API路由（如果尚未注册）
    register_api_blueprints()
    
    # 启动应用
    app.run(debug=True, host='0.0.0.0', port=5000)



# ==================== 知识库增强模型 ====================

class KnowledgeVersion(db.Model):
    """知识库文章版本历史"""
    __tablename__ = 'knowledge_versions'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('knowledge_articles.id'), nullable=False)
    version_number = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    change_summary = Column(String(500))
    
    article = relationship('KnowledgeArticle', backref='versions')
    creator = relationship('User', backref='knowledge_versions')


class KnowledgeShare(db.Model):
    """知识库文章分享"""
    __tablename__ = 'knowledge_shares'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('knowledge_articles.id'), nullable=False)
    share_token = Column(String(32), unique=True, nullable=False)
    password = Column(String(64))
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    expire_at = Column(DateTime)
    allow_download = Column(Boolean, default=True)
    view_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    article = relationship('KnowledgeArticle', backref='shares')
    creator = relationship('User', backref='knowledge_shares')


class KnowledgeLink(db.Model):
    """知识库文章双向链接"""
    __tablename__ = 'knowledge_links'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    from_article_id = Column(Integer, ForeignKey('knowledge_articles.id'), nullable=False)
    to_article_id = Column(Integer, ForeignKey('knowledge_articles.id'), nullable=False)
    context = Column(String(200))
    created_at = Column(DateTime, default=datetime.now)
    
    from_article = relationship('KnowledgeArticle', foreign_keys=[from_article_id], backref='outgoing_links')
    to_article = relationship('KnowledgeArticle', foreign_keys=[to_article_id], backref='incoming_links')


class KnowledgeTagEnhanced(db.Model):
    """知识库标签（增强版）"""
    __tablename__ = 'knowledge_tags'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    color = Column(String(7), default='#409EFF')
    description = Column(String(200))
    created_at = Column(DateTime, default=datetime.now)


# 文章标签关联表
article_tags = db.Table('article_tags',
    db.Column('article_id', db.Integer, db.ForeignKey('knowledge_articles.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('knowledge_tags.id'), primary_key=True)
)


class KnowledgeFavorite(db.Model):
    """知识库收藏"""
    __tablename__ = 'knowledge_favorites'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('knowledge_articles.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    folder_name = Column(String(100))
    
    article = relationship('KnowledgeArticle', backref='favorites')
    user = relationship('User', backref='knowledge_favorites')


class KnowledgeReadRecord(db.Model):
    """知识库阅读记录"""
    __tablename__ = 'knowledge_read_records'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('knowledge_articles.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    read_at = Column(DateTime, default=datetime.now)
    read_duration = Column(Integer, default=0)
    is_finished = Column(Boolean, default=False)
    
    article = relationship('KnowledgeArticle', backref='read_records')
    user = relationship('User', backref='knowledge_read_records')


class KnowledgeComment(db.Model):
    """知识库行内评论"""
    __tablename__ = 'knowledge_comments'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('knowledge_articles.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    block_id = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    parent_id = Column(Integer, ForeignKey('knowledge_comments.id'))
    is_resolved = Column(Boolean, default=False)
    
    article = relationship('KnowledgeArticle', backref='comments')
    user = relationship('User', backref='knowledge_comments')
    parent = relationship('KnowledgeComment', remote_side=[id], backref='replies')


# ==================== 知识库增强模型结束 ====================

# 注意：API 蓝图在 if __name__ == '__main__': 块中注册，以避免循环导入问题
