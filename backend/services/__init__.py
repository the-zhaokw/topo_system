"""
服务层模块初始化
提供合同管理增强服务的统一入口
"""

from services.contract_enhanced_service import (
    get_export_control_service,
    get_ip_service,
    get_workflow_service,
    get_risk_scanner,
    ExportControlService,
    IntellectualPropertyService,
    ContractWorkflowService,
    ContractRiskScanner
)

from services.delivery_tracking_service import (
    get_site_tracker,
    get_bom_manager,
    get_milestone_tracker,
    SiteDeliveryTracker,
    BOMManager,
    DeliveryMilestoneTracker
)

from services.email_service import (
    EmailService,
    email_service
)

__all__ = [
    # 合同增强服务
    'get_export_control_service',
    'get_ip_service',
    'get_workflow_service',
    'get_risk_scanner',
    'ExportControlService',
    'IntellectualPropertyService',
    'ContractWorkflowService',
    'ContractRiskScanner',
    
    # 交付跟踪服务
    'get_site_tracker',
    'get_bom_manager',
    'get_milestone_tracker',
    'SiteDeliveryTracker',
    'BOMManager',
    'DeliveryMilestoneTracker',
    
    # 邮件服务
    'EmailService',
    'email_service'
]
