"""
Bug相关模型模块
包含Bug、BugComment等模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from config.extensions import db
from models.base import BaseModel
from models.enums import BugStatus, Priority, Severity


class Bug(BaseModel):
    """Bug模型"""
    __tablename__ = 'bugs'
    __table_args__ = {'extend_existing': True}
    
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(50), default=BugStatus.NEW.value)
    priority = Column(String(20), default=Priority.MEDIUM.value)
    severity = Column(String(20), default=Severity.MEDIUM.value)
    reported_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    assigned_to = Column(Integer, ForeignKey('users.id'))
    resolved_by = Column(Integer, ForeignKey('users.id'))
    verifier_id = Column(Integer, ForeignKey('users.id'))
    verified_by = Column(Integer, ForeignKey('users.id'))
    project_id = Column(Integer, ForeignKey('projects.id'))
    module = Column(String(100))
    version = Column(String(50))
    environment = Column(Text)
    steps_to_reproduce = Column(Text)
    expected_result = Column(Text)
    actual_result = Column(Text)
    screenshot = Column(String(255))
    attachment = Column(String(255))
    attachment_path = Column(String(255))
    resolved_at = Column(DateTime)
    closed_at = Column(DateTime)
    verified_at = Column(DateTime)
    reopened_count = Column(Integer, default=0)
    deadline = Column(DateTime)
    tags = Column(Text)
    issue_type = Column(String(50))
    reproduce_frequency = Column(String(50))
    found_build = Column(String(50))
    test_version = Column(String(50))
    resolution = Column(Text)
    resolution_version = Column(String(50))
    plan_resolve_version = Column(String(50))
    resolve_build = Column(String(50))
    estimated_hours = Column(Integer)
    actual_hours = Column(Integer)
    test_case_id = Column(String(50))
    customer_mr_number = Column(String(50))
    related_bug_id = Column(Integer)
    parent_bug_id = Column(Integer)
    
    reporter = relationship("User", foreign_keys=[reported_by])
    assignee = relationship("User", foreign_keys=[assigned_to])
    resolver = relationship("User", foreign_keys=[resolved_by])
    verifier = relationship("User", foreign_keys=[verifier_id])
    verified_by_user = relationship("User", foreign_keys=[verified_by])
    comments = relationship("Comment", 
                           primaryjoin="and_(Comment.commentable_type=='bug', Comment.commentable_id==Bug.id)",
                           cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'severity': self.severity,
            'reported_by': self.reported_by,
            'assigned_to': self.assigned_to,
            'resolved_by': self.resolved_by,
            'verifier_id': self.verifier_id,
            'verified_by': self.verified_by,
            'project_id': self.project_id,
            'module': self.module,
            'version': self.version,
            'environment': self.environment,
            'steps_to_reproduce': self.steps_to_reproduce,
            'expected_result': self.expected_result,
            'actual_result': self.actual_result,
            'screenshot': self.screenshot,
            'attachment': self.attachment,
            'attachment_path': self.attachment_path,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'reopened_count': self.reopened_count or 0,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'tags': self.tags,
            'issue_type': self.issue_type,
            'reproduce_frequency': self.reproduce_frequency,
            'found_build': self.found_build,
            'test_version': self.test_version,
            'resolution': self.resolution,
            'resolution_version': self.resolution_version,
            'plan_resolve_version': self.plan_resolve_version,
            'resolve_build': self.resolve_build,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'test_case_id': self.test_case_id,
            'customer_mr_number': self.customer_mr_number,
            'related_bug_id': self.related_bug_id,
            'parent_bug_id': self.parent_bug_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class BugComment(BaseModel):
    """Bug评论模型（保留用于兼容性）"""
    __tablename__ = 'bug_comments'
    __table_args__ = {'extend_existing': True}
    
    bug_id = Column(Integer, ForeignKey('bugs.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)
    
    bug = relationship("Bug")
    user = relationship("User")
    
    def to_dict(self):
        return {
            'id': self.id,
            'bug_id': self.bug_id,
            'user_id': self.user_id,
            'content': self.content,
            'is_internal': self.is_internal,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }