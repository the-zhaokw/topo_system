"""
模型模块
导出所有数据模型
"""
from models.base import BaseModel, CaseInsensitiveEnum
from models.enums import (
    UserRole, ProjectStatus, AttendanceStatus, ApprovalStatus,
    BugStatus, Priority, Severity, NotificationType, LeaveType
)
from models.user import User, Department, Position, PersonalTask, FocusSession, HabitRecord
from models.project import Project, ProjectMember
from models.attendance import WorkCalendar, ShiftSchedule, UserShift, AttendanceRecord, LeaveApplication
from models.bug import Bug, BugComment
from models.notification import Notification

__all__ = [
    # 基础类
    'BaseModel',
    'CaseInsensitiveEnum',
    # 枚举
    'UserRole',
    'ProjectStatus',
    'AttendanceStatus',
    'ApprovalStatus',
    'BugStatus',
    'Priority',
    'Severity',
    'NotificationType',
    'LeaveType',
    # 用户相关模型
    'User',
    'Department',
    'Position',
    'PersonalTask',
    'FocusSession',
    'HabitRecord',
    # 项目相关模型
    'Project',
    'ProjectMember',
    # 考勤相关模型
    'WorkCalendar',
    'ShiftSchedule',
    'UserShift',
    'AttendanceRecord',
    'LeaveApplication',
    # Bug相关模型
    'Bug',
    'BugComment',
    # 通知相关模型
    'Notification',
]
