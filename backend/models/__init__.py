"""
数据库模型模块
集中管理枚举类型定义，避免循环导入问题
"""
from enum import Enum

# 延迟导入模型类以避免循环导入
def get_user_model():
    from .user import User
    return User

def get_permission_models():
    """获取权限相关模型（已弃用，权限模型现在在enhanced_app.py中定义）"""
    return None, None, None, None, None, None

class BugStatus(Enum):
    """Bug状态枚举"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"

class Priority(Enum):
    """优先级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Severity(Enum):
    """严重程度枚举"""
    TRIVIAL = "trivial"
    MINOR = "minor"
    MAJOR = "major"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class UserRoleEnum(Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    MANAGER = "manager"
    DEVELOPER = "developer"
    TESTER = "tester"
    VIEWER = "viewer"

# 物料管理相关枚举
class MaterialStatus(Enum):
    """物料状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"

class TransactionType(Enum):
    """库存交易类型枚举"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    TRANSFER = "transfer"
    ADJUSTMENT = "adjustment"

# 合同管理相关枚举
class ContractStatus(Enum):
    """合同状态枚举"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    CANCELLED = "cancelled"

class ContractType(Enum):
    """合同类型枚举 - 通信设备企业定制版"""
    EQUIPMENT_SALES = "equipment_sales"  # 设备销售合同
    SOFTWARE_LICENSE = "software_license"  # 软件许可合同
    FRAMEWORK_AGREEMENT = "framework_agreement"  # 框架协议
    PURCHASE_ORDER = "purchase_order"  # 采购订单
    ENGINEERING_SERVICE = "engineering_service"  # 工程服务合同
    MAINTENANCE_SERVICE = "maintenance_service"  # 维护服务合同
    PATENT_LICENSE = "patent_license"  # 专利许可合同
    OEM_AGREEMENT = "oem_agreement"  # OEM代工协议
    SUPPLY_AGREEMENT = "supply_agreement"  # 供应协议
    INTERNATIONAL_PROJECT = "international_project"  # 国际项目合同

class ContractRiskLevel(Enum):
    """合同风险等级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class DeliveryStatus(Enum):
    """交付状态枚举 - 通信设备企业定制"""
    PENDING = "pending"
    IN_PRODUCTION = "in_production"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    CUSTOMS_CLEARANCE = "customs_clearance"
    INSTALLATION = "installation"
    COMMISSIONING = "commissioning"
    ACCEPTANCE_TESTING = "acceptance_testing"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class ApprovalStatus(Enum):
    """审批状态枚举"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"