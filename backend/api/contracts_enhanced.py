"""
合同管理增强 API 接口
提供出口管制检查、知识产权分析、风险评估、工作流路由等高级功能
"""

from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

# 导入增强服务
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.contract_enhanced_service import (
    get_export_control_service,
    get_ip_service,
    get_workflow_service,
    get_risk_scanner
)

contracts_enhanced_bp = Blueprint('contracts_enhanced', __name__, url_prefix='/contracts/enhanced')
contracts_enhanced_api = Api(contracts_enhanced_bp)


class ExportControlCheckResource(Resource):
    """出口管制检查 API"""
    method_decorators = {'post': [jwt_required()]}

    """出口管制检查 API"""
    
    def post(self):
        """
        执行出口管制合规检查
        
        请求体：
        {
            "country": "IR",  # 国家代码
            "party_b_name": "XXX Company",  # 乙方名称
            "technology_tags": ["5g_infrastructure", "encryption"],  # 技术标签
            "contract_type": "equipment_sales"
        }
        """
        export_service = get_export_control_service()
        data = request.get_json()
        
        if not data:
            return {'error': '请求数据为空'}, 400
        
        # 执行综合检查
        result = export_service.comprehensive_export_check(data)
        
        # 记录检查历史（可选）
        # 可以保存到数据库用于审计
        
        return {
            'result': result,
            'message': '出口管制检查完成',
            'can_proceed': result.get('can_proceed', True),
            'requires_license': result.get('export_license_required', False)
        }


class IntellectualPropertyAnalysisResource(Resource):
    """知识产权条款分析 API"""
    method_decorators = {'get': [jwt_required()], 'post': [jwt_required()]}

    """知识产权条款分析 API"""
    
    def post(self):
        """
        分析知识产权条款风险
        
        请求体：
        {
            "clause_content": "...",  # 条款内容
            "clause_type": "background_ip"  # 条款类型
        }
        """
        ip_service = get_ip_service()
        data = request.get_json()
        
        if not data:
            return {'error': '请求数据为空'}, 400
        
        clause_content = data.get('clause_content', '')
        clause_type = data.get('clause_type', '')
        
        # 分析条款风险
        analysis = ip_service.analyze_ip_clause(clause_content)
        
        return {
            'analysis': analysis,
            'message': '知识产权条款分析完成'
        }
    
    def get(self, clause_type):
        """
        获取标准知识产权条款模板
        
        路径参数：
        clause_type: 条款类型（background_ip/foreground_ip/patent_license/source_code_deposit/ip_indemnification/confidentiality）
        """
        ip_service = get_ip_service()
        
        # 获取自定义参数（可选）
        custom_params = request.args.get('params')
        import json
        params_dict = json.loads(custom_params) if custom_params else {}
        
        # 生成标准条款
        clause = ip_service.generate_ip_clause(clause_type, params_dict)
        
        return {
            'clause_type': clause_type,
            'clause_content': clause,
            'message': '条款生成成功'
        }


class ContractRiskScanResource(Resource):
    """合同风险扫描 API"""
    method_decorators = {'post': [jwt_required()]}

    """合同风险扫描 API"""
    
    def post(self):
        """
        全面扫描合同风险
        
        请求体：完整的合同数据对象
        """
        risk_scanner = get_risk_scanner()
        data = request.get_json()
        
        if not data:
            return {'error': '请求数据为空'}, 400
        
        # 执行风险扫描
        result = risk_scanner.scan_contract(data)
        
        return {
            'risk_assessment': result,
            'message': '合同风险扫描完成',
            'overall_risk': result.get('overall_risk', 'low'),
            'requires_legal_review': result.get('requires_legal_review', False)
        }


class WorkflowRoutingResource(Resource):
    """工作流路由 API"""
    method_decorators = {'post': [jwt_required()]}

    """工作流路由 API"""
    
    def post(self):
        """
        根据合同特征确定审批路径
        
        请求体：合同数据对象
        """
        workflow_service = get_workflow_service()
        data = request.get_json()
        
        if not data:
            return {'error': '请求数据为空'}, 400
        
        # 获取合同 ID（如果是更新）
        contract_id = data.get('id', 0)
        
        # 确定审批路径
        approval_path = workflow_service.determine_approval_path(data)
        
        # 获取完整工作流配置
        workflow_config = workflow_service.get_dynamic_workflow(contract_id, data)
        
        return {
            'workflow': workflow_config,
            'approval_path': approval_path,
            'message': '工作流路由计算完成',
            'total_levels': approval_path.get('total_levels', 0),
            'estimated_duration_days': approval_path.get('estimated_duration_days', 0)
        }


class StandardClauseLibraryResource(Resource):
    """标准条款库 API"""
    
    def get(self):
        """
        获取标准条款库列表
        
        查询参数：
        category: 条款分类（legal/technical/ip/compliance/delivery）
        contract_type: 合同类型
        """
        category = request.args.get('category')
        contract_type = request.args.get('contract_type')
        
        # 示例条款库（实际应从数据库获取）
        clause_library = [
            {
                'id': 1,
                'title': '背景知识产权定义',
                'category': 'ip',
                'contract_types': ['software_license', 'tech_cooperation', 'patent_license'],
                'content': '背景知识产权指各方在本合同签订前已拥有的知识产权...',
                'is_standard': True,
                'usage_count': 156
            },
            {
                'id': 2,
                'title': '前景知识产权归属',
                'category': 'ip',
                'contract_types': ['software_license', 'tech_cooperation'],
                'content': '在本合同履行过程中产生的新技术成果归...',
                'is_standard': True,
                'usage_count': 142
            },
            {
                'id': 3,
                'title': '出口管制合规声明',
                'category': 'compliance',
                'contract_types': ['equipment_sales', 'international_project'],
                'content': '乙方保证遵守所有适用的出口管制法律法规...',
                'is_standard': True,
                'usage_count': 89
            },
            {
                'id': 4,
                'title': '5G 设备技术规范',
                'category': 'technical',
                'contract_types': ['equipment_sales'],
                'content': '设备应符合 3GPP Release 15/16/17 标准...',
                'is_standard': True,
                'usage_count': 67
            },
            {
                'id': 5,
                'title': '核心网设备安全要求',
                'category': 'technical',
                'contract_types': ['equipment_sales'],
                'content': '核心网设备应满足以下安全要求：1. 支持用户面和控制面分离...',
                'is_standard': True,
                'usage_count': 45
            },
            {
                'id': 6,
                'title': 'SLA 服务等级协议',
                'category': 'delivery',
                'contract_types': ['maintenance_service', 'engineering_service'],
                'content': '服务可用性不低于 99.99%，故障响应时间不超过 2 小时...',
                'is_standard': True,
                'usage_count': 234
            },
            {
                'id': 7,
                'title': 'GDPR 数据保护条款',
                'category': 'compliance',
                'contract_types': ['international_project'],
                'content': '双方同意遵守欧盟《通用数据保护条例》（GDPR）的要求...',
                'is_standard': True,
                'usage_count': 78
            },
            {
                'id': 8,
                'title': '不可抗力条款',
                'category': 'legal',
                'contract_types': ['all'],
                'content': '因不可抗力导致无法履行合同的，受影响方不承担违约责任...',
                'is_standard': True,
                'usage_count': 312
            }
        ]
        
        # 筛选
        if category:
            clause_library = [c for c in clause_library if c['category'] == category]
        
        if contract_type:
            clause_library = [
                c for c in clause_library 
                if contract_type in c['contract_types'] or 'all' in c['contract_types']
            ]
        
        return {
            'clauses': clause_library,
            'total': len(clause_library),
            'message': '标准条款获取成功'
        }


class ContractTemplateResource(Resource):
    """合同模板 API"""
    
    def get(self, template_type):
        """
        获取合同模板
        
        路径参数：
        template_type: 模板类型
            - base_station_sales: 基站设备销售合同
            - core_network_license: 核心网软件许可合同
            - framework_agreement: 框架协议
            - purchase_order: 采购订单
            - engineering_service: 海外工程服务合同
            - maintenance_service: 维护服务合同
            - patent_license: 专利许可合同
            - oem_agreement: OEM 代工协议
            - supply_agreement: 供应协议
            - international_project: 国际项目合同
        """
        # 模板定义（实际应从数据库或文件系统获取）
        templates = {
            'base_station_sales': {
                'name': '基站设备销售合同',
                'description': '适用于 5G/4G 基站设备销售，包含设备清单、交付、安装、验收等条款',
                'contract_type': 'equipment_sales',
                'sections': [
                    '定义与解释',
                    '设备清单与技术规范',
                    '价格与付款条件',
                    '交付与运输',
                    '安装与调试',
                    '验收标准与程序',
                    '质量保证与售后服务',
                    '知识产权',
                    '保密',
                    '违约责任',
                    '适用法律与争议解决'
                ],
                'required_fields': [
                    'party_a', 'party_b', 'total_amount', 'currency',
                    'country', 'site_info', 'bom_info', 'delivery_requirements'
                ],
                'optional_fields': [
                    'ip_protection_required', 'export_control_applicable',
                    'performance_bond', 'warranty_period'
                ]
            },
            'core_network_license': {
                'name': '核心网软件许可合同',
                'description': '适用于核心网软件产品许可，包含许可范围、使用限制、技术支持等条款',
                'contract_type': 'software_license',
                'sections': [
                    '定义与解释',
                    '许可授予',
                    '许可范围与限制',
                    '许可费用与支付',
                    '技术支持与维护',
                    '知识产权归属',
                    '保密义务',
                    '保证与免责',
                    '违约责任',
                    '合同期限与终止',
                    '适用法律与争议解决'
                ],
                'required_fields': [
                    'party_a', 'party_b', 'total_amount', 'currency',
                    'ip_license_info', 'ip_protection_required',
                    'source_code_deposit', 'sla_requirements'
                ],
                'optional_fields': [
                    'background_ip', 'foreground_ip', 'data_protection_clause'
                ]
            },
            'international_project': {
                'name': '国际项目合同',
                'description': '适用于海外交钥匙工程项目，包含设计、采购、施工、调试等全流程',
                'contract_type': 'international_project',
                'sections': [
                    '定义与解释',
                    '工程范围',
                    '合同价格与支付',
                    '工期与进度',
                    '设备材料供应',
                    '施工与安装',
                    '调试与试运行',
                    '竣工验收',
                    '质量保证',
                    '健康、安全与环境',
                    '保险',
                    '税收与关税',
                    '不可抗力',
                    '违约与索赔',
                    '知识产权',
                    '保密',
                    '适用法律与争议解决',
                    '其他条款'
                ],
                'required_fields': [
                    'party_a', 'party_b', 'total_amount', 'currency',
                    'country', 'region', 'project_name', 'site_info',
                    'delivery_requirements', 'acceptance_criteria',
                    'governing_law', 'dispute_resolution', 'local_compliance'
                ],
                'optional_fields': [
                    'export_control_applicable', 'credit_line_info',
                    'performance_bond', 'data_protection_clause'
                ]
            }
        }
        
        template = templates.get(template_type)
        
        if not template:
            return {'error': '模板不存在'}, 404
        
        return {
            'template': template,
            'message': '模板获取成功'
        }


# 注册路由
contracts_enhanced_api.add_resource(ExportControlCheckResource, '/export-control/check')
contracts_enhanced_api.add_resource(IntellectualPropertyAnalysisResource, '/ip/analyze', '/ip/template/<clause_type>')
contracts_enhanced_api.add_resource(ContractRiskScanResource, '/risk/scan')
contracts_enhanced_api.add_resource(WorkflowRoutingResource, '/workflow/routing')
contracts_enhanced_api.add_resource(StandardClauseLibraryResource, '/clauses/standard')
contracts_enhanced_api.add_resource(ContractTemplateResource, '/template/<template_type>')
