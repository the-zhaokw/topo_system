"""
通信设备企业合同管理增强服务
包含：出口管制合规检查、知识产权管理、风险评估、工作流路由等功能
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any


class ExportControlService:
    """出口管制合规服务"""
    
    # 高风险国家/地区列表（示例）
    HIGH_RISK_COUNTRIES = [
        'IR', 'KP', 'SY', 'CU', 'RU', 'BY',  # 伊朗、朝鲜、叙利亚、古巴、俄罗斯、白俄罗斯
        'VE', 'MM', 'AF', 'IQ', 'LY', 'SD'   # 委内瑞拉、缅甸、阿富汗、伊拉克、利比亚、苏丹
    ]
    
    # 受管制技术列表（示例）
    CONTROLLED_TECHNOLOGIES = [
        'core_network',  # 核心网技术
        '5g_infrastructure',  # 5G 基础设施
        'encryption',  # 加密技术
        'semiconductor',  # 半导体
        'quantum_communication',  # 量子通信
        'satellite_communication',  # 卫星通信
        'military_grade',  # 军工级
        'dual_use'  # 军民两用
    ]
    
    def __init__(self):
        self.sanctioned_entities = self._load_sanctioned_entities()
    
    def _load_sanctioned_entities(self) -> List[str]:
        """加载受制裁实体清单（示例数据，实际应从数据库或外部 API 获取）"""
        return [
            'Huawei Technologies Co., Ltd.',
            'ZTE Corporation',
            'Hytera Communications Corporation',
            'Uniview Technologies',
            'Dahua Technology'
        ]
    
    def check_country_risk(self, country_code: str) -> Dict[str, Any]:
        """
        检查国家/地区风险等级
        
        Args:
            country_code: 国家代码（ISO 3166-1 alpha-2）
            
        Returns:
            风险评估结果
        """
        is_high_risk = country_code.upper() in self.HIGH_RISK_COUNTRIES
        
        return {
            'country_code': country_code,
            'is_high_risk': is_high_risk,
            'risk_level': 'high' if is_high_risk else 'low',
            'export_license_required': is_high_risk,
            'recommendations': [
                '需要进行出口许可证申请' if is_high_risk else '无需特殊许可证',
                '需要高级管理层审批' if is_high_risk else '正常审批流程',
                '需要法务合规审查' if is_high_risk else '标准合规审查'
            ] if is_high_risk else []
        }
    
    def check_entity_sanctions(self, entity_name: str) -> Dict[str, Any]:
        """
        检查实体是否在制裁清单上
        
        Args:
            entity_name: 实体名称
            
        Returns:
            制裁检查结果
        """
        is_sanctioned = any(
            sanctioned.lower() in entity_name.lower() 
            for sanctioned in self.sanctioned_entities
        )
        
        return {
            'entity_name': entity_name,
            'is_sanctioned': is_sanctioned,
            'match_results': [
                entity for entity in self.sanctioned_entities 
                if entity.lower() in entity_name.lower()
            ],
            'recommendation': '禁止交易，需要立即上报合规部门' if is_sanctioned else '可以进行交易'
        }
    
    def check_technology_control(self, technology_tags: List[str]) -> Dict[str, Any]:
        """
        检查技术是否受出口管制
        
        Args:
            technology_tags: 技术标签列表
            
        Returns:
            技术管制检查结果
        """
        controlled_techs = [
            tech for tech in technology_tags 
            if tech.lower() in self.CONTROLLED_TECHNOLOGIES
        ]
        
        return {
            'technology_tags': technology_tags,
            'is_controlled': len(controlled_techs) > 0,
            'controlled_technologies': controlled_techs,
            'export_license_required': len(controlled_techs) > 0,
            'recommendations': [
                f'技术 {tech} 受出口管制，需要申请许可证' 
                for tech in controlled_techs
            ] if controlled_techs else []
        }
    
    def comprehensive_export_check(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        综合出口管制检查
        
        Args:
            contract_data: 合同数据（包含国家、客户信息、技术标签等）
            
        Returns:
            综合检查结果
        """
        country_check = self.check_country_risk(
            contract_data.get('country', 'CN')
        )
        
        party_b_check = self.check_entity_sanctions(
            contract_data.get('party_b_name', '')
        )
        
        tech_check = self.check_technology_control(
            contract_data.get('technology_tags', [])
        )
        
        overall_risk = 'low'
        if country_check['is_high_risk'] or party_b_check['is_sanctioned'] or tech_check['is_controlled']:
            overall_risk = 'high'
        
        return {
            'overall_risk': overall_risk,
            'country_check': country_check,
            'entity_check': party_b_check,
            'technology_check': tech_check,
            'export_license_required': (
                country_check['export_license_required'] or 
                tech_check['export_license_required']
            ),
            'requires_legal_review': overall_risk == 'high',
            'requires_senior_approval': overall_risk == 'high',
            'can_proceed': not party_b_check['is_sanctioned'],
            'recommendations': (
                country_check['recommendations'] + 
                tech_check['recommendations'] +
                [party_b_check['recommendation']]
            )
        }


class IntellectualPropertyService:
    """知识产权管理服务"""
    
    def __init__(self):
        self.ip_clause_templates = self._load_ip_templates()
    
    def _load_ip_templates(self) -> Dict[str, str]:
        """加载知识产权条款模板"""
        return {
            'background_ip': """
背景知识产权定义：
1. 甲方背景知识产权：指甲方在本合同签订前已拥有的，或在本合同签订后独立开发的知识产权，包括但不限于专利、商标、著作权、商业秘密等。
2. 乙方背景知识产权：指乙方在本合同签订前已拥有的，或在本合同签订后独立开发的知识产权，包括但不限于专利、商标、著作权、商业秘密等。
3. 各方背景知识产权的所有权归各自所有，本合同的签订不构成任何一方背景知识产权的转让或许可。
            """,
            
            'foreground_ip': """
前景知识产权归属：
1. 在本合同履行过程中产生的新技术成果（前景知识产权），其所有权归【甲方/乙方/双方共有】。
2. 如前景知识产权归甲方所有，乙方享有【免费/付费】使用权，使用范围为【全球/特定区域】。
3. 如前景知识产权归乙方所有，甲方享有【免费/付费】使用权，使用范围为【全球/特定区域】。
4. 如前景知识产权为双方共有，任何一方实施该知识产权所获得的收益，应当按照【甲方__%，乙方__%】的比例分配。
            """,
            
            'patent_license': """
专利许可条款：
1. 许可方（甲方/乙方）同意授予被许可方【独占/排他/普通】许可。
2. 许可专利清单详见附件《许可专利清单》，包括专利号、专利名称、申请日、授权日等信息。
3. 许可地域范围：【全球/特定国家或地区】。
4. 许可期限：自【YYYY 年 MM 月 DD 日】至【YYYY 年 MM 月 DD 日】，或至专利有效期届满之日止。
5. 许可费用：【一次性支付/分期支付/按销售额提成】，具体金额为【币种 + 金额】。
6. 许可方保证对所许可专利拥有合法权利，保证被许可方不会因实施许可专利而受到第三方侵权指控。
            """,
            
            'source_code_deposit': """
源代码托管条款：
1. 乙方应将本合同项下软件的源代码托管至双方认可的第三方托管机构。
2. 托管源代码应包括完整的设计文档、注释、编译脚本、测试用例等技术资料。
3. 在以下情况下，甲方有权获取托管的源代码：
   (a) 乙方破产或解散；
   (b) 乙方严重违反本合同约定，且在收到甲方书面通知后【30】日内未予纠正；
   (c) 乙方无法继续提供合同约定的维护服务。
4. 甲方获取源代码后，仅可为【自身内部使用/继续维护和升级】的目的使用，不得向第三方披露或转让。
5. 源代码托管费用由【甲方/乙方】承担。
            """,
            
            'ip_indemnification': """
知识产权侵权赔偿：
1. 乙方保证所提供的产品/服务不侵犯任何第三方的知识产权。
2. 如甲方因使用乙方提供的产品/服务而被第三方指控侵权，乙方应：
   (a) 承担甲方因此遭受的全部损失，包括但不限于赔偿金、律师费、诉讼费等；
   (b) 负责与第三方进行谈判或诉讼；
   (c) 采取必要措施使甲方能够继续使用产品/服务，包括但不限于修改产品、获取许可等。
3. 如产品/服务被认定为侵权，甲方有权选择：
   (a) 退货并要求乙方返还全部款项；
   (b) 要求乙方修改产品使其不侵权；
   (c) 要求乙方获取第三方许可，许可费用由乙方承担。
            """,
            
            'confidentiality': """
保密条款：
1. 保密信息定义：指一方（披露方）向另一方（接收方）披露的、具有商业价值的、不为公众所知的信息，包括但不限于技术信息、商业信息、财务信息、客户信息等。
2. 接收方应：
   (a) 对保密信息严格保密，采取与保护自己保密信息相同的保密措施；
   (b) 仅可为履行本合同的目的使用保密信息；
   (c) 仅可向有知悉必要的员工披露，并确保该等员工遵守本保密条款。
3. 以下信息不属于保密信息：
   (a) 在披露时已为公众所知的信息；
   (b) 非因接收方过错而在披露后成为公众所知的信息；
   (c) 接收方在披露前已合法拥有的信息；
   (d) 接收方从第三方合法获得的信息。
4. 保密期限：自本合同生效之日起至合同终止后【3/5/10】年。
            """
        }
    
    def analyze_ip_clause(self, clause_content: str) -> Dict[str, Any]:
        """
        分析知识产权条款风险
        
        Args:
            clause_content: 条款内容
            
        Returns:
            风险分析结果
        """
        risks = []
        suggestions = []
        
        # 检查背景知识产权定义是否清晰
        if '背景知识产权' not in clause_content and 'background ip' not in clause_content.lower():
            risks.append({
                'type': 'missing_background_ip',
                'level': 'high',
                'description': '缺少背景知识产权定义，可能导致权属争议'
            })
            suggestions.append('建议添加背景知识产权定义条款')
        
        # 检查前景知识产权归属是否明确
        if '前景知识产权' not in clause_content and 'foreground ip' not in clause_content.lower():
            risks.append({
                'type': 'missing_foreground_ip',
                'level': 'high',
                'description': '缺少前景知识产权归属约定，新产生的技术成果权属不明确'
            })
            suggestions.append('建议明确约定前景知识产权的归属')
        
        # 检查是否有侵权赔偿条款
        if '侵权' not in clause_content and 'indemnification' not in clause_content.lower():
            risks.append({
                'type': 'missing_indemnification',
                'level': 'medium',
                'description': '缺少知识产权侵权赔偿条款'
            })
            suggestions.append('建议添加知识产权侵权赔偿条款')
        
        # 检查保密条款
        if '保密' not in clause_content and 'confidential' not in clause_content.lower():
            risks.append({
                'type': 'missing_confidentiality',
                'level': 'medium',
                'description': '缺少保密条款，技术秘密可能泄露'
            })
            suggestions.append('建议添加保密条款')
        
        # 检查是否有模糊表述
        vague_terms = ['合理', '适当', '相关', '等', '其他']
        for term in vague_terms:
            if term in clause_content:
                risks.append({
                    'type': 'vague_language',
                    'level': 'low',
                    'description': f'条款中包含模糊表述"{term}"，可能引发争议'
                })
                suggestions.append(f'建议明确"{term}"的具体含义或范围')
        
        return {
            'has_risks': len(risks) > 0,
            'risk_count': len(risks),
            'risks': risks,
            'suggestions': suggestions,
            'risk_level': 'high' if any(r['level'] == 'high' for r in risks) else 'medium' if any(r['level'] == 'medium' for r in risks) else 'low'
        }
    
    def generate_ip_clause(self, clause_type: str, custom_params: Dict[str, Any] = None) -> str:
        """
        生成标准知识产权条款
        
        Args:
            clause_type: 条款类型（background_ip/foreground_ip/patent_license/source_code_deposit/ip_indemnification/confidentiality）
            custom_params: 自定义参数
            
        Returns:
            生成的条款文本
        """
        template = self.ip_clause_templates.get(clause_type, '')
        
        if not template:
            return ''
        
        if custom_params:
            # 简单的参数替换
            for key, value in custom_params.items():
                template = template.replace(f'【{key}】', str(value))
        
        return template.strip()
    
    def check_ip_risks(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        检查合同知识产权风险
        
        Args:
            contract_data: 合同数据
            
        Returns:
            知识产权风险评估结果
        """
        risks = []
        
        # 检查是否需要 IP 保护
        if contract_data.get('ip_protection_required'):
            # 检查是否有背景 IP 定义
            if not contract_data.get('background_ip'):
                risks.append({
                    'type': 'missing_background_ip_definition',
                    'level': 'high',
                    'description': '合同涉及知识产权保护，但未定义背景知识产权'
                })
            
            # 检查是否有前景 IP 归属约定
            if not contract_data.get('foreground_ip'):
                risks.append({
                    'type': 'missing_foreground_ip_ownership',
                    'level': 'high',
                    'description': '合同涉及知识产权保护，但未约定前景知识产权归属'
                })
        
        # 检查是否需要源代码托管
        if contract_data.get('source_code_deposit'):
            risks.append({
                'type': 'source_code_deposit_required',
                'level': 'medium',
                'description': '合同要求源代码托管，需要确认托管机构和具体条款'
            })
        
        # 检查是否有专利许可
        if contract_data.get('ip_license_info'):
            try:
                ip_license = json.loads(contract_data['ip_license_info'])
                if not ip_license.get('license_type'):
                    risks.append({
                        'type': 'missing_license_type',
                        'level': 'medium',
                        'description': '专利许可信息中未明确许可类型（独占/排他/普通）'
                    })
            except:
                risks.append({
                    'type': 'invalid_ip_license_format',
                    'level': 'medium',
                    'description': '专利许可信息格式不正确'
                })
        
        # 检查技术合同是否有 IP 保护
        is_tech_contract = contract_data.get('contract_type') in [
            'software_license', 'patent_license', 'tech_cooperation'
        ]
        if is_tech_contract and not contract_data.get('ip_protection_required'):
            risks.append({
                'type': 'tech_contract_missing_ip_protection',
                'level': 'high',
                'description': '技术类合同未启用知识产权保护要求'
            })
        
        return {
            'has_risks': len(risks) > 0,
            'risk_count': len(risks),
            'risks': risks,
            'risk_level': 'high' if any(r['level'] == 'high' for r in risks) else 'medium' if any(r['level'] == 'medium' for r in risks) else 'low',
            'recommendations': [
                '必须补充背景知识产权定义' if any(r['type'] == 'missing_background_ip_definition' for r in risks) else None,
                '必须明确前景知识产权归属' if any(r['type'] == 'missing_foreground_ip_ownership' for r in risks) else None,
                '建议添加知识产权侵权赔偿条款' if not any(r['type'] == 'ip_indemnification' for r in risks) else None,
            ]
        }


class ContractWorkflowService:
    """合同工作流路由服务"""
    
    def __init__(self):
        self.export_control_service = ExportControlService()
    
    def determine_approval_path(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据合同特征确定审批路径
        
        Args:
            contract_data: 合同数据
            
        Returns:
            审批路径配置
        """
        approval_levels = []
        required_reviewers = []
        
        # 基础审批：业务部门负责人
        approval_levels.append({
            'level': 1,
            'role': 'department_head',
            'name': '业务部门负责人',
            'required': True
        })
        
        # 检查合同金额
        total_amount = contract_data.get('total_amount', 0)
        currency = contract_data.get('currency', 'CNY')
        
        # 统一转换为 CNY 进行判断（简化处理）
        amount_in_cny = total_amount
        if currency == 'USD':
            amount_in_cny = total_amount * 7.2
        elif currency == 'EUR':
            amount_in_cny = total_amount * 7.8
        
        if amount_in_cny > 10000000:  # 1000 万以上
            approval_levels.append({
                'level': 2,
                'role': 'cfo',
                'name': '首席财务官',
                'required': True
            })
            required_reviewers.append('finance_reviewer')
        
        # 检查技术敏感度
        is_core_network = contract_data.get('is_core_network_tech', False)
        is_5g = contract_data.get('is_5g_related', False)
        
        if is_core_network or is_5g:
            approval_levels.append({
                'level': 3,
                'role': 'cto',
                'name': '首席技术官',
                'required': True
            })
            required_reviewers.append('tech_reviewer')
        
        # 检查出口管制风险
        country = contract_data.get('country', 'CN')
        export_check = self.export_control_service.check_country_risk(country)
        
        if export_check['is_high_risk'] or contract_data.get('export_control_applicable'):
            approval_levels.append({
                'level': 4,
                'role': 'compliance_officer',
                'name': '合规官',
                'required': True
            })
            required_reviewers.append('legal_compliance_reviewer')
        
        # 检查知识产权
        if contract_data.get('ip_protection_required'):
            approval_levels.append({
                'level': 5,
                'role': 'ip_counsel',
                'name': '知识产权法务',
                'required': True
            })
            required_reviewers.append('ip_reviewer')
        
        # 检查是否为国际合同
        if country != 'CN':
            required_reviewers.append('local_legal_counsel')
            approval_levels.append({
                'level': 6,
                'role': 'regional_legal',
                'name': f'{contract_data.get("region", "海外")}区域法务',
                'required': True
            })
        
        # 检查合同类型
        contract_type = contract_data.get('contract_type', '')
        if contract_type in ['patent_license', 'tech_cooperation', 'software_license']:
            required_reviewers.append('tech_transfer_reviewer')
        
        # 检查是否涉及供应链
        if contract_type in ['procurement', 'oem', 'supply_agreement']:
            required_reviewers.append('supply_chain_reviewer')
        
        # 最终审批：CEO（重大合同）
        is_major_contract = (
            amount_in_cny > 50000000 or  # 5000 万以上
            is_core_network or
            export_check['is_high_risk']
        )
        
        if is_major_contract:
            approval_levels.append({
                'level': 99,
                'role': 'ceo',
                'name': '首席执行官',
                'required': True
            })
        
        return {
            'approval_levels': approval_levels,
            'required_reviewers': required_reviewers,
            'total_levels': len(approval_levels),
            'estimated_duration_days': len(approval_levels) * 2,  # 每级审批预计 2 天
            'is_expedited': not is_major_contract and amount_in_cny < 1000000,
            'risk_factors': {
                'high_value': amount_in_cny > 10000000,
                'sensitive_technology': is_core_network or is_5g,
                'high_risk_country': export_check['is_high_risk'],
                'ip_involved': contract_data.get('ip_protection_required', False),
                'international': country != 'CN'
            }
        }
    
    def get_dynamic_workflow(self, contract_id: int, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取动态工作流配置
        
        Args:
            contract_id: 合同 ID
            contract_data: 合同数据
            
        Returns:
            完整的工作流配置
        """
        approval_path = self.determine_approval_path(contract_data)
        
        return {
            'contract_id': contract_id,
            'workflow_type': 'contract_approval',
            'approval_path': approval_path,
            'current_level': 0,
            'status': 'not_started',
            'notifications': {
                'on_approval': ['requester', 'next_approver'],
                'on_rejection': ['requester', 'current_approver'],
                'on_completion': ['requester', 'all_approvers', 'archive_manager']
            },
            'sla': {
                'level_timeout_hours': 48,  # 每级审批 48 小时
                'total_timeout_hours': approval_path['total_levels'] * 48,
                'escalation_enabled': True,
                'escalation_after_hours': 72
            }
        }


class ContractRiskScanner:
    """合同风险扫描服务"""
    
    def __init__(self):
        self.ip_service = IntellectualPropertyService()
        self.export_service = ExportControlService()
    
    def scan_contract(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        全面扫描合同风险
        
        Args:
            contract_data: 合同数据
            
        Returns:
            风险扫描结果
        """
        all_risks = []
        
        # 1. 出口管制风险扫描
        export_risks = self.export_service.comprehensive_export_check(contract_data)
        if export_risks['overall_risk'] in ['high', 'medium']:
            all_risks.append({
                'category': 'export_control',
                'level': export_risks['overall_risk'],
                'details': export_risks,
                'requires_action': not export_risks['can_proceed']
            })
        
        # 2. 知识产权风险扫描
        ip_risks = self.ip_service.check_ip_risks(contract_data)
        if ip_risks['has_risks']:
            all_risks.append({
                'category': 'intellectual_property',
                'level': ip_risks['risk_level'],
                'details': ip_risks,
                'requires_action': ip_risks['risk_level'] == 'high'
            })
        
        # 3. 交付风险扫描
        delivery_risks = self._scan_delivery_risks(contract_data)
        if delivery_risks['has_risks']:
            all_risks.append(delivery_risks)
        
        # 4. 财务风险扫描
        financial_risks = self._scan_financial_risks(contract_data)
        if financial_risks['has_risks']:
            all_risks.append(financial_risks)
        
        # 5. 合规风险扫描
        compliance_risks = self._scan_compliance_risks(contract_data)
        if compliance_risks['has_risks']:
            all_risks.append(compliance_risks)
        
        # 计算整体风险等级
        overall_risk = 'low'
        if any(r['level'] == 'high' for r in all_risks):
            overall_risk = 'high'
        elif any(r['level'] == 'medium' for r in all_risks):
            overall_risk = 'medium'
        
        return {
            'overall_risk': overall_risk,
            'risk_categories': [r['category'] for r in all_risks],
            'total_risk_count': len(all_risks),
            'high_risk_count': sum(1 for r in all_risks if r['level'] == 'high'),
            'medium_risk_count': sum(1 for r in all_risks if r['level'] == 'medium'),
            'low_risk_count': sum(1 for r in all_risks if r['level'] == 'low'),
            'risks': all_risks,
            'requires_legal_review': overall_risk == 'high',
            'requires_senior_approval': overall_risk == 'high',
            'can_proceed': not any(r.get('requires_action', False) for r in all_risks),
            'recommendations': self._generate_recommendations(all_risks)
        }
    
    def _scan_delivery_risks(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """扫描交付风险"""
        risks = []
        
        # 检查验收标准是否明确
        if not contract_data.get('acceptance_criteria'):
            risks.append({
                'type': 'missing_acceptance_criteria',
                'level': 'high',
                'description': '缺少明确的验收标准，可能导致交付争议'
            })
        
        # 检查交付要求是否明确
        if not contract_data.get('delivery_requirements'):
            risks.append({
                'type': 'missing_delivery_requirements',
                'level': 'medium',
                'description': '缺少详细的交付要求'
            })
        
        # 检查 SLA 要求
        if contract_data.get('contract_type') in ['maintenance_service', 'engineering_service']:
            if not contract_data.get('sla_requirements'):
                risks.append({
                    'type': 'missing_sla',
                    'level': 'high',
                    'description': '服务类合同缺少服务等级协议（SLA）'
                })
        
        # 检查保修期
        warranty_period = contract_data.get('warranty_period', 0)
        if warranty_period < 12:
            risks.append({
                'type': 'short_warranty_period',
                'level': 'low',
                'description': f'保修期{warranty_period}个月，短于行业标准（12 个月）'
            })
        
        return {
            'category': 'delivery',
            'has_risks': len(risks) > 0,
            'risk_count': len(risks),
            'risks': risks,
            'level': 'high' if any(r['level'] == 'high' for r in risks) else 'medium' if any(r['level'] == 'medium' for r in risks) else 'low'
        }
    
    def _scan_financial_risks(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """扫描财务风险"""
        risks = []
        
        # 检查币种风险
        currency = contract_data.get('currency', 'CNY')
        if currency not in ['CNY', 'USD', 'EUR']:
            risks.append({
                'type': 'currency_risk',
                'level': 'medium',
                'description': f'合同使用{currency}结算，可能存在汇率风险'
            })
        
        # 检查付款条款
        payment_terms = contract_data.get('payment_terms')
        if not payment_terms:
            risks.append({
                'type': 'missing_payment_terms',
                'level': 'high',
                'description': '缺少付款条款'
            })
        else:
            try:
                terms = json.loads(payment_terms)
                # 检查是否有预付款
                has_advance_payment = any(
                    t.get('stage') == 'advance' for t in terms
                )
                if not has_advance_payment:
                    risks.append({
                        'type': 'no_advance_payment',
                        'level': 'low',
                        'description': '合同未约定预付款，增加现金流压力'
                    })
            except:
                pass
        
        # 检查履约保证金
        performance_bond = contract_data.get('performance_bond', 0)
        total_amount = contract_data.get('total_amount', 0)
        if total_amount > 0 and performance_bond / total_amount < 0.05:
            risks.append({
                'type': 'low_performance_bond',
                'level': 'low',
                'description': '履约保证金比例低于 5%，保障力度不足'
            })
        
        return {
            'category': 'financial',
            'has_risks': len(risks) > 0,
            'risk_count': len(risks),
            'risks': risks,
            'level': 'high' if any(r['level'] == 'high' for r in risks) else 'medium' if any(r['level'] == 'medium' for r in risks) else 'low'
        }
    
    def _scan_compliance_risks(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """扫描合规风险"""
        risks = []
        
        # 检查适用法律
        if not contract_data.get('governing_law'):
            risks.append({
                'type': 'missing_governing_law',
                'level': 'high',
                'description': '未约定适用法律'
            })
        
        # 检查争议解决方式
        if not contract_data.get('dispute_resolution'):
            risks.append({
                'type': 'missing_dispute_resolution',
                'level': 'high',
                'description': '未约定争议解决方式'
            })
        
        # 检查数据保护条款
        if contract_data.get('country') in ['DE', 'FR', 'IT', 'ES', 'GB']:  # 欧盟国家
            if not contract_data.get('data_protection_clause'):
                risks.append({
                    'type': 'missing_gdpr_clause',
                    'level': 'high',
                    'description': '欧盟国家合同缺少 GDPR 数据保护条款'
                })
        
        # 检查本地化合规要求
        if contract_data.get('country') and contract_data['country'] != 'CN':
            if not contract_data.get('local_compliance'):
                risks.append({
                    'type': 'missing_local_compliance',
                    'level': 'medium',
                    'description': '海外合同缺少本地化合规要求'
                })
        
        return {
            'category': 'compliance',
            'has_risks': len(risks) > 0,
            'risk_count': len(risks),
            'risks': risks,
            'level': 'high' if any(r['level'] == 'high' for r in risks) else 'medium' if any(r['level'] == 'medium' for r in risks) else 'low'
        }
    
    def _generate_recommendations(self, risks: List[Dict[str, Any]]) -> List[str]:
        """生成风险处理建议"""
        recommendations = []
        
        for risk in risks:
            if risk['level'] == 'high':
                if risk['category'] == 'export_control':
                    recommendations.append('【紧急】立即启动出口管制合规审查，必要时申请出口许可证')
                elif risk['category'] == 'intellectual_property':
                    recommendations.append('【紧急】补充知识产权保护条款，明确背景 IP 和前景 IP 归属')
                elif risk['category'] == 'delivery':
                    recommendations.append('【紧急】完善验收标准和交付要求，避免交付争议')
                elif risk['category'] == 'compliance':
                    recommendations.append('【紧急】补充适用法律和争议解决条款，确保合规性')
        
        return recommendations


# 单例模式
_export_control_service = None
_ip_service = None
_workflow_service = None
_risk_scanner = None


def get_export_control_service() -> ExportControlService:
    """获取出口管制服务实例"""
    global _export_control_service
    if _export_control_service is None:
        _export_control_service = ExportControlService()
    return _export_control_service


def get_ip_service() -> IntellectualPropertyService:
    """获取知识产权服务实例"""
    global _ip_service
    if _ip_service is None:
        _ip_service = IntellectualPropertyService()
    return _ip_service


def get_workflow_service() -> ContractWorkflowService:
    """获取工作流服务实例"""
    global _workflow_service
    if _workflow_service is None:
        _workflow_service = ContractWorkflowService()
    return _workflow_service


def get_risk_scanner() -> ContractRiskScanner:
    """获取风险扫描器实例"""
    global _risk_scanner
    if _risk_scanner is None:
        _risk_scanner = ContractRiskScanner()
    return _risk_scanner
