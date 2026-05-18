"""
项目相关模型模块
包含Project、ProjectMember等模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from config.extensions import db
from models.base import BaseModel
from models.enums import ProjectStatus


class Project(BaseModel):
    """项目模型"""
    __tablename__ = 'projects'
    __table_args__ = {'extend_existing': True}
    
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    status = Column(String(50), default=ProjectStatus.PLANNING.value)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    owner_id = Column(Integer, ForeignKey('users.id'))
    manager_id = Column(Integer, ForeignKey('users.id'))
    created_by = Column(Integer, ForeignKey('users.id'))
    progress = Column(Integer, default=0)
    current_stage = Column(String(50))
    quality = Column(String(20))
    risk = Column(String(20))
    resources = Column(String(20))
    cost = Column(Float, default=0.0)
    priority = Column(String(20), default='medium')
    technology_stack = Column(Text)
    budget = Column(Float, default=0.0)
    actual_cost = Column(Float, default=0.0)
    project_type = Column(String(50))
    client_name = Column(String(100))
    client_contact = Column(String(100))
    contract_value = Column(Float, default=0.0)
    estimated_hours = Column(Integer, default=0)
    actual_hours = Column(Integer, default=0)
    team_size = Column(Integer, default=0)
    tags = Column(Text)
    milestones = Column(Text)
    versions = Column(Text)
    modules = Column(Text)
    
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


class ProjectMember(BaseModel):
    """项目成员模型"""
    __tablename__ = 'project_members'
    __table_args__ = {'extend_existing': True}
    
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    role = Column(String(50), default='member')
    join_date = Column(DateTime, default=db.func.now())
    
    # 关系
    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="projects")
