"""
通知相关模型模块
包含Notification模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from config.extensions import db
from models.base import BaseModel
from models.enums import NotificationType


class Notification(BaseModel):
    """通知模型"""
    __tablename__ = 'notifications'
    __table_args__ = {'extend_existing': True}
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type = Column(String(50), default=NotificationType.SYSTEM.value)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime)
    related_bug_id = Column(Integer, ForeignKey('bugs.id'))
    related_comment_id = Column(Integer, ForeignKey('bug_comments.id'))
    related_project_id = Column(Integer, ForeignKey('projects.id'))
    
    # 关系
    user = relationship("User")
    related_bug = relationship("Bug")
    related_comment = relationship("BugComment")
    related_project = relationship("Project")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'title': self.title,
            'content': self.content,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'related_bug_id': self.related_bug_id,
            'related_comment_id': self.related_comment_id,
            'related_project_id': self.related_project_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def mark_as_read(self):
        """标记通知为已读"""
        self.is_read = True
        self.read_at = db.func.now()
        db.session.commit()
