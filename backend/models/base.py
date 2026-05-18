"""
基础模型模块
提供基础模型类和通用枚举基类
"""
from datetime import datetime
from config.extensions import db
import enum


class BaseModel(db.Model):
    """
    基础模型类
    提供通用字段和方法，所有模型类都应该继承此类
    """
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """
        将模型实例转换为字典
        
        Returns:
            dict: 包含模型所有字段的字典
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            # 处理日期时间类型
            if isinstance(value, datetime):
                value = value.isoformat() if value else None
            result[column.name] = value
        return result
    
    def save(self):
        """
        保存模型实例到数据库
        """
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """
        从数据库删除模型实例
        """
        db.session.delete(self)
        db.session.commit()


class CaseInsensitiveEnum(enum.Enum):
    """
    不区分大小写的枚举基类
    支持大小写不敏感的枚举值匹配
    """
    
    @classmethod
    def _missing_(cls, value):
        """
        处理大小写不敏感的枚举匹配
        
        Args:
            value: 枚举值
            
        Returns:
            Enum: 匹配的枚举成员，如果没有匹配则返回None
        """
        if isinstance(value, str):
            # 尝试大小写不敏感匹配
            for member in cls:
                if member.value == value.lower():
                    return member
        # 如果没有匹配，让默认行为处理
        return super()._missing_(value)
