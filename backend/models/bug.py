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
    reporter_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    assignee_id = Column(Integer, ForeignKey('users.id'))
    project_id = Column(Integer, ForeignKey('projects.id'))
    module = Column(String(100))
    version = Column(String(50))
    environment = Column(Text)
    steps_to_reproduce = Column(Text)
    expected_result = Column(Text)
    actual_result = Column(Text)
    screenshot = Column(String(255))
    attachment = Column(String(255))
    resolved_at = Column(DateTime)
    closed_at = Column(DateTime)
    
    # 关系
    reporter = relationship("User", foreign_keys=[reporter_id])
    assignee = relationship("User", foreign_keys=[assignee_id])
    comments = relationship("BugComment", back_populates="bug", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'severity': self.severity,
            'reporter_id': self.reporter_id,
            'assignee_id': self.assignee_id,
            'project_id': self.project_id,
            'module': self.module,
            'version': self.version,
            'environment': self.environment,
            'steps_to_reproduce': self.steps_to_reproduce,
            'expected_result': self.expected_result,
            'actual_result': self.actual_result,
            'screenshot': self.screenshot,
            'attachment': self.attachment,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class BugComment(BaseModel):
    """Bug评论模型"""
    __tablename__ = 'bug_comments'
    __table_args__ = {'extend_existing': True}
    
    bug_id = Column(Integer, ForeignKey('bugs.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)
    
    # 关系
    bug = relationship("Bug", back_populates="comments")
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
