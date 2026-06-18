"""
合同管理系统API接口
包含合同全生命周期管理、审批流程、交付监控、风险管理等功能
专为通信设备企业定制
"""

from flask import Blueprint, request, jsonify, current_app
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, func
from datetime import datetime, timezone, timedelta

# 统一权限系统
from utils.permission_unified import (
    require_perm as _require_perm,
    require_any as _require_any,
    require_admin as _require_admin,
    check_perm as _check_perm,
    check_module as _check_module,
    filter_query_by_perm as _filter_query_by_perm,
    is_system_admin as _is_system_admin,
)

def get_db():
    """延迟获取数据库实例，避免循环导入"""
    from enhanced_app import get_db_instance
    return get_db_instance()

def get_app():
    from enhanced_app import app
    return app

def get_contract_models():
    from enhanced_app import Contract, ContractClause, ContractApproval, ContractDelivery, ContractChange, ContractRisk, ContractPayment, ContractAttachment
    from enhanced_app import db
    return db, Contract, ContractClause, ContractApproval, ContractDelivery, ContractChange, ContractRisk, ContractPayment, ContractAttachment

contracts_bp = Blueprint('contracts', __name__, url_prefix='/contracts')
contracts_api = Api(contracts_bp)


def _check_perm_or_admin(user, perm_code):
    """内部权限校验：管理员/超管直接放行，否则校验细分权限。"""
    if not user:
        return False
    return _check_perm(user, perm_code)


def require_contract_perm(perm_code):
    """合同子路由权限校验装饰器。"""
    from functools import wraps
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            try:
                current_user_id = int(current_user_id)
            except (TypeError, ValueError):
                pass
            from enhanced_app import User
            user = User.query.get(current_user_id)
            if not user:
                return {'error': '用户不存在'}, 404
            if not _check_perm_or_admin(user, perm_code):
                return {'error': '权限不足', 'code': 'PERMISSION_DENIED', 'required_permission': perm_code}, 403
            return f(*args, **kwargs)
        return wrapper
    return decorator


# 各资源方法的统一权限映射
_CONTRACT_PERMS = {
    'list':         'contract:view',
    'create':       'contract:create',
    'detail':       'contract:view',
    'update':       'contract:edit',
    'delete':       'contract:delete',
    'approve':      'contract:approve',
    'delivery':     'contract:edit',
    'change':       'contract:edit',
    'risk':         'contract:view',
    'payment':      'contract:view_finance',
    'attachment':   'contract:edit',
    'statistics':   'contract:view_statistics',
    'export':       'contract:export',
}


class ContractListResource(Resource):
    """合同列表API"""

    method_decorators = {
        'get': [require_contract_perm('contract:view')],
        'post': [require_contract_perm('contract:create')],
    }

    def get(self):
        db = get_db()
        app = get_app()
        db, Contract, _, _, _, _, _, _, _ = get_contract_models()

        with app.app_context():
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            status = request.args.get('status')
            contract_type = request.args.get('contract_type')
            risk_level = request.args.get('risk_level')
            project_id = request.args.get('project_id', type=int)
            region = request.args.get('region')
            country = request.args.get('country')
            keyword = request.args.get('keyword')
            
            query = db.session.query(Contract)
            
            if status:
                query = query.filter(Contract.status == status)
            if contract_type:
                query = query.filter(Contract.contract_type == contract_type)
            if risk_level:
                query = query.filter(Contract.risk_level == risk_level)
            if project_id:
                query = query.filter(Contract.project_id == project_id)
            if region:
                query = query.filter(Contract.region == region)
            if country:
                query = query.filter(Contract.country == country)
            if keyword:
                query = query.filter(
                    or_(
                        Contract.title.ilike(f'%{keyword}%'),
                        Contract.contract_no.ilike(f'%{keyword}%'),
                        Contract.party_a_name.ilike(f'%{keyword}%'),
                        Contract.party_b_name.ilike(f'%{keyword}%')
                    )
                )
            
            query = query.order_by(Contract.created_at.desc())
            
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            contracts = pagination.items
            
            return {
                'contracts': [c.to_dict() for c in contracts],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page
            }
    
    def post(self):
        db, Contract, _, _, _, _, _, _, _ = get_contract_models()
        
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return {'error': '请求数据不能为空', 'code': 'VALIDATION_ERROR'}, 400
        
        title = data.get('title')
        if not title:
            return {'error': 'title (合同标题) 字段为必填项', 'code': 'VALIDATION_ERROR'}, 400
        
        contract_no = data.get('contract_no')
        if not contract_no:
            contract_no = f"CTR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        contract = Contract(
            contract_no=contract_no,
            title=title,
            contract_type=data.get('contract_type', 'equipment_sales'),
            status=data.get('status', 'draft'),
            risk_level=data.get('risk_level', 'low'),
            party_a=data.get('party_a'),
            party_a_name=data.get('party_a_name'),
            party_b=data.get('party_b'),
            party_b_name=data.get('party_b_name'),
            project_id=data.get('project_id'),
            project_name=data.get('project_name'),
            signing_date=datetime.fromisoformat(data['signing_date']) if data.get('signing_date') else None,
            effective_date=datetime.fromisoformat(data['effective_date']) if data.get('effective_date') else None,
            expiration_date=datetime.fromisoformat(data['expiration_date']) if data.get('expiration_date') else None,
            total_amount=data.get('total_amount', 0.0),
            currency=data.get('currency', 'CNY'),
            region=data.get('region'),
            country=data.get('country'),
            technical_requirements=data.get('technical_requirements'),
            delivery_requirements=data.get('delivery_requirements'),
            acceptance_criteria=data.get('acceptance_criteria'),
            sla_requirements=data.get('sla_requirements'),
            ip_protection_required=data.get('ip_protection_required', False),
            export_control_applicable=data.get('export_control_applicable', False),
            file_url=data.get('file_url'),
            site_info=data.get('site_info'),
            bom_info=data.get('bom_info'),
            ip_license_info=data.get('ip_license_info'),
            source_code_deposit=data.get('source_code_deposit', False),
            background_ip=data.get('background_ip'),
            foreground_ip=data.get('foreground_ip'),
            export_control_declaration=data.get('export_control_declaration'),
            sanction_check_status=data.get('sanction_check_status', 'pending'),
            local_compliance=data.get('local_compliance'),
            payment_terms=data.get('payment_terms'),
            credit_line_info=data.get('credit_line_info'),
            performance_bond=data.get('performance_bond', 0.0),
            warranty_period=data.get('warranty_period', 12),
            data_protection_clause=data.get('data_protection_clause'),
            governing_law=data.get('governing_law'),
            dispute_resolution=data.get('dispute_resolution'),
            project_manager_id=data.get('project_manager_id'),
            tech_lead_id=data.get('tech_lead_id'),
            supply_chain_lead_id=data.get('supply_chain_lead_id'),
            related_po_ids=data.get('related_po_ids'),
            tech_spec_version=data.get('tech_spec_version'),
            is_core_network_tech=data.get('is_core_network_tech', False),
            is_5g_related=data.get('is_5g_related', False),
            acceptance_type=data.get('acceptance_type', 'Both'),
            delivery_progress=data.get('delivery_progress', 0.0),
            created_by=current_user_id
        )
        
        db.session.add(contract)
        db.session.commit()
        
        return {'contract': contract.to_dict(), 'message': '合同创建成功'}, 201


class ContractDetailResource(Resource):
    """合同详情API"""

    method_decorators = {
        'get': [require_contract_perm('contract:view')],
        'put': [require_contract_perm('contract:edit')],
        'delete': [require_contract_perm('contract:delete')],
    }
    
    def get(self, contract_id):
        db = get_db()
        app = get_app()
        db, Contract, _, _, _, _, _, _, _ = get_contract_models()
        
        with app.app_context():
            contract = db.session.get(Contract, contract_id)
            if not contract:
                return {'error': '合同不存在'}, 404
            
            contract_data = contract.to_dict()
            
            clauses = contract.clauses if hasattr(contract, 'clauses') else []
            contract_data['clauses'] = [c.to_dict() for c in clauses]
            
            approvals = contract.approvals if hasattr(contract, 'approvals') else []
            contract_data['approvals'] = [a.to_dict() for a in approvals]
            
            deliveries = contract.deliveries if hasattr(contract, 'deliveries') else []
            contract_data['deliveries'] = [d.to_dict() for d in deliveries]
            
            changes = contract.changes if hasattr(contract, 'changes') else []
            contract_data['changes'] = [c.to_dict() for c in changes]
            
            risks = contract.risks if hasattr(contract, 'risks') else []
            contract_data['risks'] = [r.to_dict() for r in risks]
            
            payments = contract.payments if hasattr(contract, 'payments') else []
            contract_data['payments'] = [p.to_dict() for p in payments]
            
            attachments = contract.attachments if hasattr(contract, 'attachments') else []
            contract_data['attachments'] = [a.to_dict() for a in attachments]
            
            return {'contract': contract_data}
    
    def put(self, contract_id):
        db = get_db()
        app = get_app()
        db, Contract, _, _, _, _, _, _, _ = get_contract_models()
        
        with app.app_context():
            contract = db.session.get(Contract, contract_id)
            if not contract:
                return {'error': '合同不存在'}, 404
            
            data = request.get_json()
            
            if 'title' in data:
                contract.title = data['title']
            if 'contract_type' in data:
                contract.contract_type = data['contract_type']
            if 'status' in data:
                contract.status = data['status']
            if 'risk_level' in data:
                contract.risk_level = data['risk_level']
            if 'party_a' in data:
                contract.party_a = data['party_a']
            if 'party_a_name' in data:
                contract.party_a_name = data['party_a_name']
            if 'party_b' in data:
                contract.party_b = data['party_b']
            if 'party_b_name' in data:
                contract.party_b_name = data['party_b_name']
            if 'project_id' in data:
                contract.project_id = data['project_id']
            if 'project_name' in data:
                contract.project_name = data['project_name']
            if 'signing_date' in data:
                contract.signing_date = datetime.fromisoformat(data['signing_date']) if data['signing_date'] else None
            if 'effective_date' in data:
                contract.effective_date = datetime.fromisoformat(data['effective_date']) if data['effective_date'] else None
            if 'expiration_date' in data:
                contract.expiration_date = datetime.fromisoformat(data['expiration_date']) if data['expiration_date'] else None
            if 'total_amount' in data:
                contract.total_amount = data['total_amount']
            if 'currency' in data:
                contract.currency = data['currency']
            if 'region' in data:
                contract.region = data['region']
            if 'country' in data:
                contract.country = data['country']
            if 'technical_requirements' in data:
                contract.technical_requirements = data['technical_requirements']
            if 'delivery_requirements' in data:
                contract.delivery_requirements = data['delivery_requirements']
            if 'acceptance_criteria' in data:
                contract.acceptance_criteria = data['acceptance_criteria']
            if 'sla_requirements' in data:
                contract.sla_requirements = data['sla_requirements']
            if 'ip_protection_required' in data:
                contract.ip_protection_required = data['ip_protection_required']
            if 'export_control_applicable' in data:
                contract.export_control_applicable = data['export_control_applicable']
            if 'file_url' in data:
                contract.file_url = data['file_url']
            # 通信设备企业增强字段
            if 'site_info' in data:
                contract.site_info = data['site_info']
            if 'bom_info' in data:
                contract.bom_info = data['bom_info']
            if 'ip_license_info' in data:
                contract.ip_license_info = data['ip_license_info']
            if 'source_code_deposit' in data:
                contract.source_code_deposit = data['source_code_deposit']
            if 'background_ip' in data:
                contract.background_ip = data['background_ip']
            if 'foreground_ip' in data:
                contract.foreground_ip = data['foreground_ip']
            if 'export_control_declaration' in data:
                contract.export_control_declaration = data['export_control_declaration']
            if 'sanction_check_status' in data:
                contract.sanction_check_status = data['sanction_check_status']
            if 'local_compliance' in data:
                contract.local_compliance = data['local_compliance']
            if 'payment_terms' in data:
                contract.payment_terms = data['payment_terms']
            if 'credit_line_info' in data:
                contract.credit_line_info = data['credit_line_info']
            if 'performance_bond' in data:
                contract.performance_bond = data['performance_bond']
            if 'warranty_period' in data:
                contract.warranty_period = data['warranty_period']
            if 'data_protection_clause' in data:
                contract.data_protection_clause = data['data_protection_clause']
            if 'governing_law' in data:
                contract.governing_law = data['governing_law']
            if 'dispute_resolution' in data:
                contract.dispute_resolution = data['dispute_resolution']
            if 'project_manager_id' in data:
                contract.project_manager_id = data['project_manager_id']
            if 'tech_lead_id' in data:
                contract.tech_lead_id = data['tech_lead_id']
            if 'supply_chain_lead_id' in data:
                contract.supply_chain_lead_id = data['supply_chain_lead_id']
            if 'related_po_ids' in data:
                contract.related_po_ids = data['related_po_ids']
            if 'tech_spec_version' in data:
                contract.tech_spec_version = data['tech_spec_version']
            if 'is_core_network_tech' in data:
                contract.is_core_network_tech = data['is_core_network_tech']
            if 'is_5g_related' in data:
                contract.is_5g_related = data['is_5g_related']
            if 'acceptance_type' in data:
                contract.acceptance_type = data['acceptance_type']
            if 'delivery_progress' in data:
                contract.delivery_progress = data['delivery_progress']
            
            contract.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {'contract': contract.to_dict(), 'message': '合同更新成功'}
    
    def delete(self, contract_id):
        db = get_db()
        app = get_app()
        db, Contract, _, _, _, _, _, _, _ = get_contract_models()
        
        with app.app_context():
            contract = db.session.get(Contract, contract_id)
            if not contract:
                return {'error': '合同不存在'}, 404
            
            db.session.delete(contract)
            db.session.commit()
            
            return {'message': '合同删除成功'}


class ContractClauseResource(Resource):
    """合同条款API"""

    method_decorators = {
        'get': [require_contract_perm('contract:view')],
        'post': [require_contract_perm('contract:edit')],
        'put': [require_contract_perm('contract:edit')],
        'delete': [require_contract_perm('contract:delete')],
    }
    
    def get(self, contract_id):
        db = get_db()
        app = get_app()
        db, Contract, ContractClause, _, _, _, _, _, _ = get_contract_models()
        
        with app.app_context():
            contract = db.session.get(Contract, contract_id)
            if not contract:
                return {'error': '合同不存在'}, 404
            
            data = request.get_json()
            
            clause = ContractClause(
                contract_id=contract_id,
                clause_type=data.get('clause_type'),
                clause_title=data.get('clause_title'),
                clause_content=data.get('clause_content'),
                risk_level=data.get('risk_level', 'low'),
                is_standard=data.get('is_standard', True),
                sort_order=data.get('sort_order', 0)
            )
            
            db.session.add(clause)
            db.session.commit()
            
            return {'clause': clause.to_dict(), 'message': '条款添加成功'}, 201
    
    def get(self, contract_id):
        db = get_db()
        app = get_app()
        db, _, ContractClause, _, _, _, _, _, _ = get_contract_models()
        
        with app.app_context():
            clauses = db.session.query(ContractClause).filter_by(contract_id=contract_id).order_by(ContractClause.sort_order).all()
            return {'clauses': [c.to_dict() for c in clauses]}


class ContractApprovalResource(Resource):
    """合同审批API"""

    method_decorators = {
        'get': [require_contract_perm('contract:view')],
        'post': [require_contract_perm('contract:approve')],
    }
    
    def post(self, contract_id):
        db = get_db()
        app = get_app()
        current_user_id = get_jwt_identity()
        db, Contract, _, ContractApproval, _, _, _, _, _ = get_contract_models()
        
        with app.app_context():
            contract = db.session.get(Contract, contract_id)
            if not contract:
                return {'error': '合同不存在'}, 404
            
            data = request.get_json()
            
            approval = ContractApproval(
                contract_id=contract_id,
                approval_level=data.get('approval_level', 1),
                approver_role=data.get('approver_role'),
                approver_id=current_user_id,
                status=data.get('status', 'pending'),
                comments=data.get('comments')
            )
            
            db.session.add(approval)
            
            if data.get('status') in ['approved', 'rejected']:
                approval.status = data['status']
                approval.approval_date = datetime.utcnow()
                
                if data.get('status') == 'approved':
                    all_approved = True
                    for ap in contract.approvals:
                        if ap.id != approval.id and ap.status != 'approved':
                            all_approved = False
                            break
                    if all_approved:
                        contract.status = 'active'
                elif data.get('status') == 'rejected':
                    contract.status = 'rejected'
            
            db.session.commit()
            
            return {'approval': approval.to_dict(), 'message': '审批提交成功'}, 201
    
    def get(self, contract_id):
        db = get_db()
        app = get_app()
        db, _, _, ContractApproval, _, _, _, _, _ = get_contract_models()
        
        with app.app_context():
            approvals = db.session.query(ContractApproval).filter_by(contract_id=contract_id).order_by(ContractApproval.approval_level).all()
            return {'approvals': [a.to_dict() for a in approvals]}


class ContractDeliveryResource(Resource):
    """合同交付API"""

    method_decorators = {
        'get': [require_contract_perm('contract:view')],
        'post': [require_contract_perm('contract:edit')],
        'put': [require_contract_perm('contract:edit')],
    }
    
    def get(self, contract_id):
        db = get_db()
        app = get_app()
        db, Contract, _, _, ContractDelivery, _, _, _, _ = get_contract_models()
        
        with app.app_context():
            deliveries = db.session.query(ContractDelivery).filter_by(contract_id=contract_id).all()
            return {'deliveries': [d.to_dict() for d in deliveries]}
    
    def post(self, contract_id):
        db = get_db()
        app = get_app()
        db, Contract, _, _, ContractDelivery, _, _, _, _ = get_contract_models()
        
        with app.app_context():
            contract = db.session.get(Contract, contract_id)
            if not contract:
                return {'error': '合同不存在'}, 404
            
            data = request.get_json()
            
            delivery = ContractDelivery(
                contract_id=contract_id,
                delivery_no=data.get('delivery_no', f'DLV-{datetime.now().strftime("%Y%m%d%H%M%S")}'),
                site_name=data.get('site_name'),
                site_code=data.get('site_code'),
                equipment_type=data.get('equipment_type'),
                quantity=data.get('quantity', 0),
                planned_date=datetime.fromisoformat(data['planned_date']) if data.get('planned_date') else None,
                actual_date=datetime.fromisoformat(data['actual_date']) if data.get('actual_date') else None,
                status=data.get('status', 'pending'),
                location=data.get('location'),
                notes=data.get('notes')
            )
            
            db.session.add(delivery)
            db.session.commit()
            
            return {'delivery': delivery.to_dict(), 'message': '交付记录添加成功'}, 201
    
    def put(self, contract_id, delivery_id):
        db = get_db()
        app = get_app()
        db, _, _, _, ContractDelivery, _, _, _, _ = get_contract_models()
        
        with app.app_context():
            delivery = db.session.get(ContractDelivery, delivery_id)
            if not delivery or delivery.contract_id != contract_id:
                return {'error': '交付记录不存在'}, 404
            
            data = request.get_json()
            
            if 'site_name' in data:
                delivery.site_name = data['site_name']
            if 'site_code' in data:
                delivery.site_code = data['site_code']
            if 'equipment_type' in data:
                delivery.equipment_type = data['equipment_type']
            if 'quantity' in data:
                delivery.quantity = data['quantity']
            if 'planned_date' in data:
                delivery.planned_date = datetime.fromisoformat(data['planned_date']) if data['planned_date'] else None
            if 'actual_date' in data:
                delivery.actual_date = datetime.fromisoformat(data['actual_date']) if data['actual_date'] else None
            if 'status' in data:
                delivery.status = data['status']
            if 'location' in data:
                delivery.location = data['location']
            if 'notes' in data:
                delivery.notes = data['notes']
            
            delivery.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {'delivery': delivery.to_dict(), 'message': '交付记录更新成功'}


class ContractChangeResource(Resource):
    """合同变更API"""

    method_decorators = {
        'get': [require_contract_perm('contract:view')],
        'post': [require_contract_perm('contract:edit')],
    }
    
    def get(self, contract_id):
        db = get_db()
        app = get_app()
        db, Contract, _, _, _, ContractChange, _, _, _ = get_contract_models()
        
        with app.app_context():
            changes = db.session.query(ContractChange).filter_by(contract_id=contract_id).all()
            return {'changes': [c.to_dict() for c in changes]}
    
    def post(self, contract_id):
        db = get_db()
        app = get_app()
        current_user_id = get_jwt_identity()
        db, Contract, _, _, _, ContractChange, _, _, _ = get_contract_models()
        
        with app.app_context():
            contract = db.session.get(Contract, contract_id)
            if not contract:
                return {'error': '合同不存在'}, 404
            
            data = request.get_json()
            
            change = ContractChange(
                contract_id=contract_id,
                change_no=data.get('change_no', f'CHG-{datetime.now().strftime("%Y%m%d%H%M%S")}'),
                change_type=data.get('change_type'),
                change_description=data.get('change_description'),
                original_value=data.get('original_value'),
                new_value=data.get('new_value'),
                impact_assessment=data.get('impact_assessment'),
                status=data.get('status', 'pending'),
                requested_by=current_user_id
            )
            
            db.session.add(change)
            db.session.commit()
            
            return {'change': change.to_dict(), 'message': '变更申请提交成功'}, 201


class ContractRiskResource(Resource):
    """合同风险API"""

    method_decorators = {
        'get': [require_contract_perm('contract:view')],
        'post': [require_contract_perm('contract:edit')],
        'put': [require_contract_perm('contract:edit')],
    }
    
    def get(self, contract_id):
        db = get_db()
        app = get_app()
        db, Contract, _, _, _, _, ContractRisk, _, _ = get_contract_models()
        
        with app.app_context():
            risks = db.session.query(ContractRisk).filter_by(contract_id=contract_id).all()
            return {'risks': [r.to_dict() for r in risks]}
    
    def post(self, contract_id):
        db = get_db()
        app = get_app()
        current_user_id = get_jwt_identity()
        db, Contract, _, _, _, _, ContractRisk, _, _ = get_contract_models()
        
        with app.app_context():
            contract = db.session.get(Contract, contract_id)
            if not contract:
                return {'error': '合同不存在'}, 404
            
            data = request.get_json()
            
            risk = ContractRisk(
                contract_id=contract_id,
                risk_type=data.get('risk_type'),
                risk_description=data.get('risk_description'),
                risk_level=data.get('risk_level', 'medium'),
                mitigation_measures=data.get('mitigation_measures'),
                status=data.get('status', 'identified'),
                identified_by=current_user_id,
                identified_date=datetime.utcnow()
            )
            
            db.session.add(risk)
            db.session.commit()
            
            return {'risk': risk.to_dict(), 'message': '风险记录添加成功'}, 201
    
    def put(self, contract_id, risk_id):
        db = get_db()
        app = get_app()
        db, _, _, _, _, _, ContractRisk, _, _ = get_contract_models()
        
        with app.app_context():
            risk = db.session.get(ContractRisk, risk_id)
            if not risk or risk.contract_id != contract_id:
                return {'error': '风险记录不存在'}, 404
            
            data = request.get_json()
            
            if 'risk_type' in data:
                risk.risk_type = data['risk_type']
            if 'risk_description' in data:
                risk.risk_description = data['risk_description']
            if 'risk_level' in data:
                risk.risk_level = data['risk_level']
            if 'mitigation_measures' in data:
                risk.mitigation_measures = data['mitigation_measures']
            if 'status' in data:
                risk.status = data['status']
                if data['status'] == 'resolved':
                    risk.resolved_date = datetime.utcnow()
            
            db.session.commit()
            
            return {'risk': risk.to_dict(), 'message': '风险记录更新成功'}


class ContractPaymentResource(Resource):
    """合同收付款API"""

    method_decorators = {
        'get': [require_contract_perm('contract:view_finance')],
        'post': [require_contract_perm('contract:view_finance')],
        'put': [require_contract_perm('contract:view_finance')],
    }
    
    def get(self, contract_id):
        db = get_db()
        app = get_app()
        db, Contract, _, _, _, _, _, ContractPayment, _ = get_contract_models()
        
        with app.app_context():
            payments = db.session.query(ContractPayment).filter_by(contract_id=contract_id).all()
            return {'payments': [p.to_dict() for p in payments]}
    
    def post(self, contract_id):
        db = get_db()
        app = get_app()
        db, Contract, _, _, _, _, _, ContractPayment, _ = get_contract_models()
        
        with app.app_context():
            contract = db.session.get(Contract, contract_id)
            if not contract:
                return {'error': '合同不存在'}, 404
            
            data = request.get_json()
            
            payment = ContractPayment(
                contract_id=contract_id,
                payment_no=data.get('payment_no', f'PAY-{datetime.now().strftime("%Y%m%d%H%M%S")}'),
                payment_stage=data.get('payment_stage'),
                planned_amount=data.get('planned_amount'),
                actual_amount=data.get('actual_amount'),
                currency=data.get('currency', 'CNY'),
                planned_date=datetime.fromisoformat(data['planned_date']) if data.get('planned_date') else None,
                actual_date=datetime.fromisoformat(data['actual_date']) if data.get('actual_date') else None,
                payment_method=data.get('payment_method'),
                status=data.get('status', 'pending'),
                invoice_no=data.get('invoice_no'),
                notes=data.get('notes')
            )
            
            db.session.add(payment)
            db.session.commit()
            
            return {'payment': payment.to_dict(), 'message': '付款计划添加成功'}, 201
    
    def put(self, contract_id, payment_id):
        db = get_db()
        app = get_app()
        db, _, _, _, _, _, _, ContractPayment, _ = get_contract_models()
        
        with app.app_context():
            payment = db.session.get(ContractPayment, payment_id)
            if not payment or payment.contract_id != contract_id:
                return {'error': '付款记录不存在'}, 404
            
            data = request.get_json()
            
            if 'payment_stage' in data:
                payment.payment_stage = data['payment_stage']
            if 'planned_amount' in data:
                payment.planned_amount = data['planned_amount']
            if 'actual_amount' in data:
                payment.actual_amount = data['actual_amount']
            if 'currency' in data:
                payment.currency = data['currency']
            if 'planned_date' in data:
                payment.planned_date = datetime.fromisoformat(data['planned_date']) if data['planned_date'] else None
            if 'actual_date' in data:
                payment.actual_date = datetime.fromisoformat(data['actual_date']) if data['actual_date'] else None
            if 'payment_method' in data:
                payment.payment_method = data['payment_method']
            if 'status' in data:
                payment.status = data['status']
            if 'invoice_no' in data:
                payment.invoice_no = data['invoice_no']
            if 'notes' in data:
                payment.notes = data['notes']
            
            db.session.commit()
            
            return {'payment': payment.to_dict(), 'message': '付款记录更新成功'}


class ContractAttachmentResource(Resource):
    """合同附件API"""

    method_decorators = {
        'get': [require_contract_perm('contract:view')],
        'post': [require_contract_perm('contract:edit')],
        'delete': [require_contract_perm('contract:delete')],
    }
    
    def get(self, contract_id):
        db = get_db()
        app = get_app()
        db, Contract, _, _, _, _, _, _, ContractAttachment = get_contract_models()
        
        with app.app_context():
            attachments = db.session.query(ContractAttachment).filter_by(contract_id=contract_id).all()
            return {'attachments': [a.to_dict() for a in attachments]}
    
    def post(self, contract_id):
        db = get_db()
        app = get_app()
        current_user_id = get_jwt_identity()
        db, Contract, _, _, _, _, _, _, ContractAttachment = get_contract_models()
        
        with app.app_context():
            contract = db.session.get(Contract, contract_id)
            if not contract:
                return {'error': '合同不存在'}, 404
            
            data = request.get_json()
            
            attachment = ContractAttachment(
                contract_id=contract_id,
                file_name=data.get('file_name'),
                file_path=data.get('file_path'),
                file_type=data.get('file_type'),
                file_size=data.get('file_size'),
                attachment_type=data.get('attachment_type'),
                description=data.get('description'),
                uploaded_by=current_user_id
            )
            
            db.session.add(attachment)
            db.session.commit()
            
            return {'attachment': attachment.to_dict(), 'message': '附件上传成功'}, 201


class ContractStatisticsResource(Resource):
    """合同统计报表API"""

    method_decorators = {
        'get': [require_contract_perm('contract:view_statistics')],
    }

    def get(self):
        db = get_db()
        app = get_app()
        db, Contract, _, _, ContractDelivery, _, _, ContractPayment, _ = get_contract_models()
        
        with app.app_context():
            total_contracts = db.session.query(Contract).count()
            
            status_counts = db.session.query(
                Contract.status,
                func.count(Contract.id)
            ).group_by(Contract.status).all()
            status_dict = {s[0]: s[1] for s in status_counts}
            
            type_counts = db.session.query(
                Contract.contract_type,
                func.count(Contract.id)
            ).group_by(Contract.contract_type).all()
            type_dict = {t[0]: t[1] for t in type_counts}
            
            risk_counts = db.session.query(
                Contract.risk_level,
                func.count(Contract.id)
            ).group_by(Contract.risk_level).all()
            risk_dict = {r[0]: r[1] for r in risk_counts}
            
            total_amount = db.session.query(func.sum(Contract.total_amount)).scalar() or 0
            
            region_stats = db.session.query(
                Contract.region,
                func.count(Contract.id),
                func.sum(Contract.total_amount)
            ).group_by(Contract.region).all()
            region_list = []
            for r in region_stats:
                region_list.append({
                    'region': r[0] or 'Unknown',
                    'count': r[1],
                    'total_amount': r[2] or 0
                })
            
            active_deliveries = db.session.query(ContractDelivery).filter(
                ContractDelivery.status.notin_(['accepted', 'rejected'])
            ).count()
            
            pending_payments = db.session.query(ContractPayment).filter(
                ContractPayment.status == 'pending'
            ).count()
            
            # 通信设备企业增强统计
            # 按技术类型统计
            core_network_count = db.session.query(Contract).filter(
                Contract.is_core_network_tech == True
            ).count()
            
            g5_related_count = db.session.query(Contract).filter(
                Contract.is_5g_related == True
            ).count()
            
            # 按验收类型统计
            acceptance_type_stats = db.session.query(
                Contract.acceptance_type,
                func.count(Contract.id)
            ).filter(
                Contract.acceptance_type != None
            ).group_by(Contract.acceptance_type).all()
            acceptance_dict = {a[0]: a[1] for a in acceptance_type_stats}
            
            # IP保护相关合同统计
            ip_protected_count = db.session.query(Contract).filter(
                Contract.ip_protection_required == True
            ).count()
            
            # 源代码托管要求统计
            source_code_count = db.session.query(Contract).filter(
                Contract.source_code_deposit == True
            ).count()
            
            # 出口管制相关合同统计
            export_control_count = db.session.query(Contract).filter(
                Contract.export_control_applicable == True
            ).count()
            
            # 交付进度统计
            avg_delivery_progress = db.session.query(
                func.avg(Contract.delivery_progress)
            ).scalar() or 0
            
            # 按保修期统计
            warranty_stats = db.session.query(
                Contract.warranty_period,
                func.count(Contract.id),
                func.sum(Contract.total_amount)
            ).group_by(Contract.warranty_period).all()
            warranty_list = []
            for w in warranty_stats:
                warranty_list.append({
                    'warranty_period': w[0] or 0,
                    'count': w[1],
                    'total_amount': w[2] or 0
                })
            
            # 按币种统计
            currency_stats = db.session.query(
                Contract.currency,
                func.count(Contract.id),
                func.sum(Contract.total_amount)
            ).group_by(Contract.currency).all()
            currency_list = []
            for c in currency_stats:
                currency_list.append({
                    'currency': c[0] or 'Unknown',
                    'count': c[1],
                    'total_amount': c[2] or 0
                })
            
            return {
                'total_contracts': total_contracts,
                'status_distribution': status_dict,
                'type_distribution': type_dict,
                'risk_distribution': risk_dict,
                'total_amount': total_amount,
                'region_stats': region_list,
                'active_deliveries': active_deliveries,
                'pending_payments': pending_payments,
                # 通信设备企业增强统计
                'core_network_contracts': core_network_count,
                'g5_related_contracts': g5_related_count,
                'acceptance_type_distribution': acceptance_dict,
                'ip_protected_contracts': ip_protected_count,
                'source_code_deposit_contracts': source_code_count,
                'export_control_contracts': export_control_count,
                'average_delivery_progress': round(avg_delivery_progress, 2),
                'warranty_stats': warranty_list,
                'currency_stats': currency_list
            }


class ContractExportControlResource(Resource):
    """出口管制检查API"""

    method_decorators = {
        'get': [require_contract_perm('contract:view')],
    }

    def get(self):
        db = get_db()
        app = get_app()
        db, Contract, _, _, _, _, _, _, _ = get_contract_models()
        
        with app.app_context():
            high_risk_countries = ['IR', 'KP', 'SY', 'CU', 'RU', 'BY']
            
            risky_contracts = db.session.query(Contract).filter(
                Contract.export_control_applicable == True,
                Contract.status.in_(['draft', 'pending_review', 'pending_approval', 'active'])
            ).all()
            
            result = []
            for contract in risky_contracts:
                is_high_risk = contract.country in high_risk_countries if contract.country else False
                result.append({
                    'id': contract.id,
                    'contract_no': contract.contract_no,
                    'title': contract.title,
                    'country': contract.country,
                    'total_amount': contract.total_amount,
                    'currency': contract.currency,
                    'is_high_risk': is_high_risk,
                    'status': contract.status
                })
            
            return {'export_control_contracts': result}


class ContractIPManagementResource(Resource):
    """知识产权管理API"""

    method_decorators = {
        'get': [require_contract_perm('contract:view')],
    }

    def get(self):
        db = get_db()
        app = get_app()
        db, Contract, _, _, _, _, _, _, _ = get_contract_models()
        
        with app.app_context():
            ip_contracts = db.session.query(Contract).filter(
                Contract.ip_protection_required == True
            ).all()
            
            result = []
            for contract in ip_contracts:
                result.append({
                    'id': contract.id,
                    'contract_no': contract.contract_no,
                    'title': contract.title,
                    'ip_license_info': contract.ip_license_info,
                    'source_code_deposit': contract.source_code_deposit,
                    'background_ip': contract.background_ip,
                    'foreground_ip': contract.foreground_ip,
                    'status': contract.status,
                    'total_amount': contract.total_amount,
                    'currency': contract.currency
                })
            
            return {'ip_contracts': result}


class ContractSiteDeliveryResource(Resource):
    """站点交付管理API"""

    method_decorators = {
        'get': [require_contract_perm('contract:view')],
    }

    def get(self):
        db = get_db()
        app = get_app()
        db, Contract, _, _, ContractDelivery, _, _, _, _ = get_contract_models()
        
        with app.app_context():
            contract_id = request.args.get('contract_id', type=int)
            status = request.args.get('status')
            
            query = db.session.query(ContractDelivery)
            
            if contract_id:
                query = query.filter(ContractDelivery.contract_id == contract_id)
            if status:
                query = query.filter(ContractDelivery.status == status)
            
            deliveries = query.order_by(ContractDelivery.planned_date).all()
            
            result = []
            for delivery in deliveries:
                contract = db.session.get(Contract, delivery.contract_id)
                result.append({
                    'id': delivery.id,
                    'contract_id': delivery.contract_id,
                    'contract_no': contract.contract_no if contract else None,
                    'delivery_no': delivery.delivery_no,
                    'site_name': delivery.site_name,
                    'site_code': delivery.site_code,
                    'equipment_type': delivery.equipment_type,
                    'quantity': delivery.quantity,
                    'planned_date': delivery.planned_date.isoformat() if delivery.planned_date else None,
                    'actual_date': delivery.actual_date.isoformat() if delivery.actual_date else None,
                    'status': delivery.status,
                    'location': delivery.location
                })
            
            return {'deliveries': result, 'total': len(result)}


class ContractSanctionCheckResource(Resource):
    """制裁清单检查API"""

    method_decorators = {
        'get': [require_contract_perm('contract:view')],
    }

    def get(self):
        db = get_db()
        app = get_app()
        db, Contract, _, _, _, _, _, _, _ = get_contract_models()
        
        with app.app_context():
            sanction_countries = ['IR', 'KP', 'SY', 'CU', 'RU', 'BY', 'VE']
            
            contracts = db.session.query(Contract).filter(
                Contract.country.in_(sanction_countries),
                Contract.status.in_(['draft', 'pending_review', 'pending_approval', 'active'])
            ).all()
            
            result = []
            for contract in contracts:
                result.append({
                    'id': contract.id,
                    'contract_no': contract.contract_no,
                    'title': contract.title,
                    'country': contract.country,
                    'sanction_check_status': contract.sanction_check_status,
                    'export_control_applicable': contract.export_control_applicable,
                    'total_amount': contract.total_amount,
                    'currency': contract.currency,
                    'status': contract.status
                })
            
            return {'sanction_risk_contracts': result, 'total': len(result)}


class ContractSearchEnhancedResource(Resource):
    """增强型合同搜索API"""

    method_decorators = {
        'get': [require_contract_perm('contract:view')],
    }

    def get(self):
        db = get_db()
        app = get_app()
        db, Contract, _, _, _, _, _, _, _ = get_contract_models()
        
        with app.app_context():
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            keyword = request.args.get('keyword')
            contract_type = request.args.get('contract_type')
            region = request.args.get('region')
            country = request.args.get('country')
            status = request.args.get('status')
            is_core_network = request.args.get('is_core_network', type=bool)
            is_5g_related = request.args.get('is_5g_related', type=bool)
            ip_protection_required = request.args.get('ip_protection_required', type=bool)
            export_control_applicable = request.args.get('export_control_applicable', type=bool)
            min_amount = request.args.get('min_amount', type=float)
            max_amount = request.args.get('max_amount', type=float)
            
            query = db.session.query(Contract)
            
            if keyword:
                query = query.filter(
                    or_(
                        Contract.title.ilike(f'%{keyword}%'),
                        Contract.contract_no.ilike(f'%{keyword}%'),
                        Contract.party_a_name.ilike(f'%{keyword}%'),
                        Contract.party_b_name.ilike(f'%{keyword}%'),
                        Contract.technical_requirements.ilike(f'%{keyword}%')
                    )
                )
            
            if contract_type:
                query = query.filter(Contract.contract_type == contract_type)
            if region:
                query = query.filter(Contract.region == region)
            if country:
                query = query.filter(Contract.country == country)
            if status:
                query = query.filter(Contract.status == status)
            if is_core_network is not None:
                query = query.filter(Contract.is_core_network_tech == is_core_network)
            if is_5g_related is not None:
                query = query.filter(Contract.is_5g_related == is_5g_related)
            if ip_protection_required is not None:
                query = query.filter(Contract.ip_protection_required == ip_protection_required)
            if export_control_applicable is not None:
                query = query.filter(Contract.export_control_applicable == export_control_applicable)
            if min_amount is not None:
                query = query.filter(Contract.total_amount >= min_amount)
            if max_amount is not None:
                query = query.filter(Contract.total_amount <= max_amount)
            
            query = query.order_by(Contract.created_at.desc())
            
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            contracts = pagination.items
            
            return {
                'contracts': [c.to_dict() for c in contracts],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page
            }


contracts_api.add_resource(ContractListResource, '/')
contracts_api.add_resource(ContractDetailResource, '/<int:contract_id>')
contracts_api.add_resource(ContractClauseResource, '/<int:contract_id>/clauses')
contracts_api.add_resource(ContractApprovalResource, '/<int:contract_id>/approvals')
contracts_api.add_resource(ContractDeliveryResource, '/<int:contract_id>/deliveries', '/<int:contract_id>/deliveries/<int:delivery_id>')
contracts_api.add_resource(ContractChangeResource, '/<int:contract_id>/changes')
contracts_api.add_resource(ContractRiskResource, '/<int:contract_id>/risks', '/<int:contract_id>/risks/<int:risk_id>')
contracts_api.add_resource(ContractPaymentResource, '/<int:contract_id>/payments', '/<int:contract_id>/payments/<int:payment_id>')
contracts_api.add_resource(ContractAttachmentResource, '/<int:contract_id>/attachments')
contracts_api.add_resource(ContractStatisticsResource, '/statistics')
contracts_api.add_resource(ContractExportControlResource, '/export-control')
contracts_api.add_resource(ContractIPManagementResource, '/ip-management')
contracts_api.add_resource(ContractSiteDeliveryResource, '/site-deliveries')
contracts_api.add_resource(ContractSanctionCheckResource, '/sanction-check')
contracts_api.add_resource(ContractSearchEnhancedResource, '/search-enhanced')
