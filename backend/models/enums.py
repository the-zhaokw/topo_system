"""
枚举定义模块
集中管理所有枚举类型
"""
from models.base import CaseInsensitiveEnum


class UserRole(CaseInsensitiveEnum):
    """用户角色枚举 - 简化角色层级"""
    ADMIN = "admin"
    MANAGER = "manager"
    PROJECT_MANAGER = "project_manager"
    TEST_ENGINEER = "test_engineer"
    SOFTWARE_ENGINEER = "software_engineer"
    USER = "user"
    HR = "hr"
    DEPARTMENT_MANAGER = "department_manager"


class ProjectStatus(CaseInsensitiveEnum):
    """项目状态枚举"""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AttendanceStatus(CaseInsensitiveEnum):
    """考勤状态枚举"""
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EARLY_LEAVE = "early_leave"
    LEAVE = "leave"
    BUSINESS_TRIP = "business_trip"
    OVERTIME = "overtime"
    MISSING = "missing"


class ApprovalStatus(CaseInsensitiveEnum):
    """审批状态枚举"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class BugStatus(CaseInsensitiveEnum):
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


class Priority(CaseInsensitiveEnum):
    """优先级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Severity(CaseInsensitiveEnum):
    """严重程度枚举"""
    TRIVIAL = "trivial"
    MINOR = "minor"
    MAJOR = "major"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    BLOCKER = "blocker"


class NotificationType(CaseInsensitiveEnum):
    """通知类型枚举"""
    SYSTEM = "system"
    BUG_ASSIGNED = "bug_assigned"
    BUG_UPDATED = "bug_updated"
    BUG_CLOSED = "bug_closed"
    COMMENT_MENTION = "comment_mention"
    APPROVAL_REQUEST = "approval_request"
    APPROVAL_RESULT = "approval_result"


class LeaveType(CaseInsensitiveEnum):
    """请假类型枚举"""
    SICK_LEAVE = "sick_leave"
    PERSONAL_LEAVE = "personal_leave"
    ANNUAL_LEAVE = "annual_leave"
    MARRIAGE_LEAVE = "marriage_leave"
    MATERNITY_LEAVE = "maternity_leave"
    PATERNITY_LEAVE = "paternity_leave"
    BEREAVEMENT_LEAVE = "bereavement_leave"
    OTHER = "other"
