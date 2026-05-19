"""
模型模块
导出所有数据模型

注意：所有模型实际上都在 enhanced_app.py 中定义
这个模块提供了一个统一的导入接口
"""
import sys

# 使用延迟导入模式，避免循环导入
# 当其他模块从 models 导入时，我们返回 enhanced_app 中的模型

def __getattr__(name):
    """动态从 enhanced_app 获取模型类"""
    if 'enhanced_app' not in sys.modules:
        raise ImportError(f"Cannot import {name}: enhanced_app not loaded yet")
    
    _enhanced_app = sys.modules['enhanced_app']
    
    # 映射表：将 models 中的名称映射到 enhanced_app 中的属性名
    _model_mapping = {
        'User': 'User',
        'Department': 'Department',
        'Position': 'Position',
        'PersonalTask': 'PersonalTask',
        'FocusSession': 'FocusSession',
        'HabitRecord': 'HabitRecord',
        'Project': 'Project',
        'ProjectMember': 'ProjectMember',
        'WorkCalendar': 'WorkCalendar',
        'ShiftSchedule': 'ShiftSchedule',
        'UserShift': 'UserShift',
        'AttendanceRecord': 'AttendanceRecord',
        'LeaveApplication': 'LeaveApplication',
        'Bug': 'Bug',
        'BugComment': 'BugComment',
        'Notification': 'Notification',
        'UserRole': 'UserRole',
        'ProjectStatus': 'ProjectStatus',
        'AttendanceStatus': 'AttendanceStatus',
        'ApprovalStatus': 'ApprovalStatus',
        'BugStatus': 'BugStatus',
        'Priority': 'Priority',
        'Severity': 'Severity',
    }
    
    if name in _model_mapping:
        return getattr(_enhanced_app, _model_mapping[name])
    
    raise AttributeError(f"module 'models' has no attribute '{name}'")

# 从本地导入基础类和特有的枚举（这些不依赖 enhanced_app）
from models.base import BaseModel, CaseInsensitiveEnum
from models.enums import (
    NotificationType, LeaveType
)

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
