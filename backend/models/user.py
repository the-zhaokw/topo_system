"""
用户相关模型模块
包含User、Department、Position、PersonalTask等模型
"""
import json
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from config.extensions import db
from models.base import BaseModel
from models.enums import UserRole


class User(BaseModel):
    """用户模型"""
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    salt = Column(String(32), nullable=False)
    role = Column(String(50), default=UserRole.USER.value, nullable=True)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    department = Column(String(100))
    position = Column(String(100))
    phone = Column(String(20))
    employee_id = Column(String(50))
    company_phone = Column(String(20))
    mobile_phone = Column(String(20))
    birthday = Column(DateTime)
    gender = Column(String(20))
    work_language = Column(String(50))
    avatar = Column(String(255))
    status = Column(String(20), default='online')
    last_login = Column(DateTime)
    last_activity = Column(DateTime)
    email_notification_enabled = Column(Boolean, default=True)
    email_on_bug_assigned = Column(Boolean, default=True)
    email_on_bug_closed = Column(Boolean, default=True)
    custom_permissions = Column(Text, default='{}')
    is_super_admin = Column(Boolean, default=False)
    
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
        """是否为系统管理员"""
        if self.is_super_admin:
            return True
        if self.is_admin:
            return True
        position_info = self.get_position_info()
        if position_info:
            return position_info.is_admin or position_info.is_manager
        return False
    
    def is_department_manager(self):
        """是否为部门经理"""
        position_info = self.get_position_info()
        return position_info is not None and position_info.is_manager
    
    def is_admin_position(self):
        """是否为管理员职位"""
        position_info = self.get_position_info()
        return position_info is not None and position_info.is_admin
    
    def has_management_permission(self):
        """是否拥有管理权限"""
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
        """检查用户是否具有特定权限"""
        if self.is_super_admin:
            return True
        position_info = self.get_position_info()
        if position_info:
            if position_info.is_admin or position_info.is_manager:
                return True
            try:
                perms = json.loads(position_info.permissions) if position_info.permissions else []
                if permission in perms:
                    return True
            except:
                pass
        
        custom_perms = self.get_custom_permissions()
        if permission in custom_perms.get('allowed', []):
            return True
        if permission in custom_perms.get('denied', []):
            return False
        return False
    
    def get_custom_permissions(self):
        """获取用户的自定义权限"""
        if not self.custom_permissions:
            return {}
        try:
            return json.loads(self.custom_permissions)
        except:
            return {}
    
    def set_custom_permissions(self, permissions_dict):
        """设置用户的自定义权限"""
        self.custom_permissions = json.dumps(permissions_dict)
    
    def check_permission(self, permission_code):
        """综合检查用户是否有特定权限"""
        if self.is_super_admin:
            return True
        position_info = self.get_position_info()
        if position_info:
            if position_info.is_admin or position_info.is_manager:
                return True
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
        """获取用户的实际在线状态"""
        if self.status == 'offline':
            return 'offline'
        if self.last_activity:
            five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
            if self.last_activity >= five_minutes_ago:
                return self.status or 'online'
        return 'offline'
    
    def update_activity(self):
        """更新用户最后活动时间"""
        self.last_activity = datetime.utcnow()


class Department(BaseModel):
    """部门模型"""
    __tablename__ = 'departments'
    __table_args__ = {'extend_existing': True}
    
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Position(BaseModel):
    """职位模型"""
    __tablename__ = 'positions'
    __table_args__ = {'extend_existing': True}
    
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    permissions = Column(Text, default='[]')
    is_admin = Column(Boolean, default=False)
    is_manager = Column(Boolean, default=False)
    
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


class PersonalTask(BaseModel):
    """个人任务模型"""
    __tablename__ = 'personal_tasks'
    __table_args__ = {'extend_existing': True}
    
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
    dependencies = Column(Text)
    is_pinned = Column(Boolean, default=False)
    order_index = Column(Integer, default=0)
    reminder_config = Column(Text)
    completed = Column(Boolean, default=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # 关系
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


class FocusSession(BaseModel):
    """专注会话模型"""
    __tablename__ = 'focus_sessions'
    __table_args__ = {'extend_existing': True}
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    task_id = Column(Integer, ForeignKey('personal_tasks.id'))
    focus_type = Column(String(20), default='pomodoro')
    planned_duration = Column(Integer, default=25)
    actual_duration = Column(Integer)
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime)
    completed = Column(Boolean, default=False)
    
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


class HabitRecord(BaseModel):
    """习惯记录模型"""
    __tablename__ = 'habit_records'
    __table_args__ = {'extend_existing': True}
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    task_id = Column(Integer, ForeignKey('personal_tasks.id'))
    completed_date = Column(Date, nullable=False)
    duration_minutes = Column(Integer)
    note = Column(String(200))
    
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
