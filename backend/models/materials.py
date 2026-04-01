"""
物料管理系统数据库模型
包含物料分类、物料主数据、仓库库位、库存管理、序列号管理等模型
"""

from datetime import datetime
from enum import Enum

# 定义枚举类型
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

# 这个文件只包含枚举类型和辅助函数
# 实际的模型类将在enhanced_app.py中定义，以避免循环导入问题