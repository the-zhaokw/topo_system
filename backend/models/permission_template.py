"""
权限模板模型

注意：本模块刻意不放在 models.user 中，以避免触发 models.user 中重复定义的 User 类，
导致 SQLAlchemy "Multiple classes found for path 'User'" 错误。
"""
import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Text
from config.extensions import db
from models.base import BaseModel


class PermissionTemplate(BaseModel):
    """权限模板模型

    用于保存一组"可见模块 + 额外/限制细分权限"的预设，方便一键应用到用户身上。
    适用场景：项目经理模板、测试工程师模板、新人默认模板等。
    """
    __tablename__ = 'permission_templates'
    __table_args__ = {'extend_existing': True}

    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, default='')
    category = Column(String(50), default='custom')  # builtin / role / custom
    icon = Column(String(50), default='Document')

    # 核心内容（JSON 数组）
    modules = Column(Text, default='[]')               # 可见模块编码列表
    allowed_permissions = Column(Text, default='[]')   # 额外权限编码列表
    denied_permissions = Column(Text, default='[]')    # 限制权限编码列表

    # 元数据
    is_builtin = Column(Boolean, default=False)        # 内置模板不允许删除
    is_active = Column(Boolean, default=True)          # 启用/停用
    sort_order = Column(Integer, default=0)            # 排序
    # 不用 ForeignKey('users.id')，避免与 enhanced_app 重复注册冲突
    created_by = Column(Integer, nullable=True)

    def to_dict(self, with_content=True):
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description or '',
            'category': self.category or 'custom',
            'icon': self.icon or 'Document',
            'is_builtin': bool(self.is_builtin),
            'is_active': bool(self.is_active),
            'sort_order': self.sort_order or 0,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if with_content:
            result['modules'] = self.get_modules()
            result['allowed_permissions'] = self.get_allowed_permissions()
            result['denied_permissions'] = self.get_denied_permissions()
            result['module_count'] = len(result['modules'])
            result['permission_count'] = len(result['allowed_permissions']) + len(result['denied_permissions'])
        return result

    # ---------------- 辅助方法 ----------------
    def _load_json(self, raw, default):
        if not raw:
            return default
        try:
            data = json.loads(raw)
            return data if isinstance(data, list) else default
        except Exception:
            return default

    def _save_json(self, value):
        if not isinstance(value, list):
            value = []
        # 去重 + 保留顺序
        return json.dumps(list(dict.fromkeys(value)), ensure_ascii=False)

    def get_modules(self):
        return self._load_json(self.modules, [])

    def set_modules(self, value):
        self.modules = self._save_json(value)

    def get_allowed_permissions(self):
        return self._load_json(self.allowed_permissions, [])

    def set_allowed_permissions(self, value):
        self.allowed_permissions = self._save_json(value)

    def get_denied_permissions(self):
        return self._load_json(self.denied_permissions, [])

    def set_denied_permissions(self, value):
        self.denied_permissions = self._save_json(value)

    def apply_to_user(self, user):
        """把模板内容应用到一个用户

        - modules: 写入用户的 accessible_modules
        - allowed_permissions: 写入用户的 custom_permissions.allowed
        - denied_permissions: 写入用户的 custom_permissions.denied
        """
        user.set_accessible_modules(self.get_modules())
        user.set_custom_permissions({
            'allowed': self.get_allowed_permissions(),
            'denied': self.get_denied_permissions()
        })
