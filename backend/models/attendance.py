"""
考勤相关模型模块
包含考勤记录、请假申请、班次等模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float, Date
from sqlalchemy.orm import relationship
from config.extensions import db
from models.base import BaseModel
from models.enums import AttendanceStatus, ApprovalStatus, LeaveType


class WorkCalendar(BaseModel):
    """工作日历模型"""
    __tablename__ = 'work_calendar'
    __table_args__ = {'extend_existing': True}
    
    date = Column(DateTime, nullable=False, unique=True)
    is_working_day = Column(Boolean, default=True)
    is_holiday = Column(Boolean, default=False)
    note = Column(String(255))
    
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


class ShiftSchedule(BaseModel):
    """班次模型"""
    __tablename__ = 'shift_schedules'
    __table_args__ = {'extend_existing': True}
    
    name = Column(String(100), nullable=False)
    start_time = Column(String(5), nullable=False)
    end_time = Column(String(5), nullable=False)
    shift_type = Column(String(50), nullable=False)
    flexible_range = Column(Integer, default=30)
    overtime_threshold = Column(Integer, default=60)
    is_active = Column(Boolean, default=True)
    description = Column(Text)
    
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


class UserShift(BaseModel):
    """用户班次分配模型"""
    __tablename__ = 'user_shifts'
    __table_args__ = {'extend_existing': True}
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    shift_id = Column(Integer, ForeignKey('shift_schedules.id'), nullable=False)
    effective_date = Column(DateTime, nullable=False)
    expire_date = Column(DateTime)
    
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


class AttendanceRecord(BaseModel):
    """考勤记录模型"""
    __tablename__ = 'attendance_records'
    __table_args__ = {'extend_existing': True}
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    record_date = Column(DateTime, nullable=False)
    status = Column(String(20), default="present", nullable=False)
    clock_in_time = Column(DateTime)
    clock_in_ip = Column(String(50))
    clock_in_location = Column(String(255))
    clock_out_time = Column(DateTime)
    clock_out_ip = Column(String(50))
    clock_out_location = Column(String(255))
    work_hours = Column(Float, default=0.0)
    overtime_hours = Column(Float, default=0.0)
    late_minutes = Column(Integer, default=0)
    early_leave_minutes = Column(Integer, default=0)
    note = Column(Text)
    
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


class LeaveApplication(BaseModel):
    """请假申请模型"""
    __tablename__ = 'leave_applications'
    __table_args__ = {'extend_existing': True}
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    leave_type = Column(String(50), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    days = Column(Float, nullable=False)
    reason = Column(Text)
    status = Column(String(20), default=ApprovalStatus.PENDING.value)
    approver_id = Column(Integer, ForeignKey('users.id'))
    approved_at = Column(DateTime)
    approval_comment = Column(Text)
    attachment = Column(String(255))
    
    # 关系
    applicant = relationship("User", foreign_keys=[user_id])
    approver = relationship("User", foreign_keys=[approver_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'leave_type': self.leave_type,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'days': self.days,
            'reason': self.reason,
            'status': self.status,
            'approver_id': self.approver_id,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'approval_comment': self.approval_comment,
            'attachment': self.attachment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
