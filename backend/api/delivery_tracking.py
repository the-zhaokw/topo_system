"""
交付跟踪增强 API 接口
提供站点级交付监控、里程碑管理、BOM 验证等功能
"""

from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.delivery_tracking_service import (
    get_site_tracker,
    get_bom_manager,
    get_milestone_tracker
)

delivery_tracking_bp = Blueprint('delivery_tracking', __name__, url_prefix='/contracts/delivery')
delivery_tracking_api = Api(delivery_tracking_bp)


class SiteDeliveryDashboardResource(Resource):
    """站点交付看板 API"""
    method_decorators = {'get': [jwt_required()]}

    """站点交付看板 API"""
    
    def get(self, contract_id):
        """
        获取合同交付看板数据
        
        路径参数：
        contract_id: 合同 ID
        """
        site_tracker = get_site_tracker()
        
        # 这里应该从数据库获取交付记录
        # 为演示目的，返回示例数据结构
        from enhanced_app import db, ContractDelivery
        
        deliveries = db.session.query(ContractDelivery).filter_by(contract_id=contract_id).all()
        deliveries_data = [d.to_dict() for d in deliveries]
        
        dashboard = site_tracker.get_site_delivery_dashboard(contract_id, deliveries_data)
        
        return {
            'dashboard': dashboard,
            'message': '交付看板数据获取成功'
        }


class DeliveryStatusTransitionResource(Resource):
    """交付状态流转 API"""
    method_decorators = {'get': [jwt_required()], 'post': [jwt_required()]}

    """交付状态流转 API"""
    
    def post(self, delivery_id):
        """
        更新交付状态（带验证）
        
        路径参数：
        delivery_id: 交付记录 ID
        
        请求体：
        {
            "new_status": "shipped",
            "notes": "设备已发货，物流单号：XXX"
        }
        """
        site_tracker = get_site_tracker()
        data = request.get_json()
        
        if not data:
            return {'error': '请求数据为空'}, 400
        
        new_status = data.get('new_status')
        if not new_status:
            return {'error': '缺少新状态'}, 400
        
        from enhanced_app import db, ContractDelivery
        
        delivery = db.session.get(ContractDelivery, delivery_id)
        if not delivery:
            return {'error': '交付记录不存在'}, 404
        
        current_status = delivery.status
        
        # 验证状态流转
        validation = site_tracker.validate_status_transition(current_status, new_status)
        
        if not validation['valid']:
            return {
                'error': '状态流转不合法',
                'validation': validation
            }, 400
        
        # 更新状态
        delivery.status = new_status
        if data.get('notes'):
            delivery.notes = (delivery.notes or '') + '\n' + data['notes']
        delivery.updated_at = datetime.utcnow()
        
        # 如果是到货状态，记录实际到货日期
        if new_status == 'arrived':
            delivery.actual_date = datetime.utcnow()
        
        db.session.commit()
        
        # 计算进度百分比
        progress = site_tracker.calculate_progress_percentage(new_status)
        
        return {
            'delivery': delivery.to_dict(),
            'progress_percentage': progress,
            'message': '交付状态更新成功'
        }
    
    def get(self, delivery_id):
        """
        获取交付记录允许的状态流转
        
        路径参数：
        delivery_id: 交付记录 ID
        """
        site_tracker = get_site_tracker()
        
        from enhanced_app import db, ContractDelivery
        
        delivery = db.session.get(ContractDelivery, delivery_id)
        if not delivery:
            return {'error': '交付记录不存在'}, 404
        
        current_status = delivery.status
        validation = site_tracker.validate_status_transition(current_status, 'any')
        
        return {
            'current_status': current_status,
            'allowed_transitions': validation.get('allowed_transitions', []),
            'message': '允许的状态流转获取成功'
        }


class BOMValidationResource(Resource):
    """BOM 验证 API"""
    method_decorators = {'post': [jwt_required()]}

    """BOM 验证 API"""
    
    def post(self):
        """
        验证 BOM 数据
        
        请求体：
        {
            "bom_data": [
                {
                    "equipment_type": "5G AAU",
                    "model": "AAU5613",
                    "quantity": 10,
                    "unit_price": 50000,
                    "currency": "CNY"
                },
                ...
            ]
        }
        """
        bom_manager = get_bom_manager()
        data = request.get_json()
        
        if not data:
            return {'error': '请求数据为空'}, 400
        
        bom_data = data.get('bom_data', [])
        
        # 验证 BOM
        validation = bom_manager.validate_bom(bom_data)
        
        # 计算总金额
        if validation['valid']:
            calculation = bom_manager.calculate_bom_total(bom_data)
            grouping = bom_manager.group_bom_by_category(bom_data)
            
            return {
                'validation': validation,
                'calculation': calculation,
                'grouping': grouping,
                'message': 'BOM 验证成功'
            }
        else:
            return {
                'validation': validation,
                'message': 'BOM 验证失败',
                'errors': validation['errors']
            }, 400


class DeliveryMilestoneResource(Resource):
    """交付里程碑 API"""
    method_decorators = {'get': [jwt_required()], 'post': [jwt_required()], 'put': [jwt_required()]}

    """交付里程碑 API"""
    
    def post(self, contract_id):
        """
        生成里程碑计划
        
        路径参数：
        contract_id: 合同 ID
        
        请求体：
        {
            "start_date": "2024-01-01"
        }
        """
        milestone_tracker = get_milestone_tracker()
        data = request.get_json()
        
        if not data:
            return {'error': '请求数据为空'}, 400
        
        start_date = data.get('start_date')
        if not start_date:
            return {'error': '缺少开始日期'}, 400
        
        # 生成里程碑计划
        milestone_plan = milestone_tracker.generate_milestone_plan(start_date)
        
        # 保存里程碑计划到数据库（可选）
        # 这里可以创建 ContractMilestone 记录
        
        return {
            'milestone_plan': milestone_plan,
            'message': '里程碑计划生成成功'
        }
    
    def put(self, contract_id, milestone_key):
        """
        更新里程碑状态
        
        路径参数：
        contract_id: 合同 ID
        milestone_key: 里程碑标识（production_complete/shipment/customs_clearance 等）
        
        请求体：
        {
            "status": "completed",
            "actual_date": "2024-01-15"
        }
        """
        milestone_tracker = get_milestone_tracker()
        data = request.get_json()
        
        if not data:
            return {'error': '请求数据为空'}, 400
        
        status = data.get('status')
        actual_date = data.get('actual_date')
        
        # 这里应该从数据库获取里程碑计划
        # 为演示目的，创建示例计划
        milestone_plan = milestone_tracker.generate_milestone_plan(datetime.now().isoformat())
        
        # 更新里程碑状态
        result = milestone_tracker.update_milestone_status(
            milestone_plan, milestone_key, status, actual_date
        )
        
        if not result['success']:
            return {'error': result['error']}, 404
        
        # 计算整体进度
        progress = milestone_tracker.calculate_milestone_progress(milestone_plan)
        
        return {
            'milestone': result['milestone'],
            'overall_progress': progress,
            'message': '里程碑状态更新成功'
        }
    
    def get(self, contract_id):
        """
        获取里程碑计划
        
        路径参数：
        contract_id: 合同 ID
        """
        milestone_tracker = get_milestone_tracker()
        
        # 这里应该从数据库获取里程碑计划
        # 为演示目的，生成示例计划
        from enhanced_app import db, Contract
        
        contract = db.session.get(Contract, contract_id)
        if not contract:
            return {'error': '合同不存在'}, 404
        
        start_date = contract.signing_date.isoformat() if contract.signing_date else datetime.now().isoformat()
        milestone_plan = milestone_tracker.generate_milestone_plan(start_date)
        
        return {
            'milestone_plan': milestone_plan,
            'message': '里程碑计划获取成功'
        }


class DeliveryDelayWarningResource(Resource):
    """交付延期预警 API"""
    method_decorators = {'get': [jwt_required()]}

    """交付延期预警 API"""
    
    def get(self, contract_id):
        """
        获取交付延期预警
        
        路径参数：
        contract_id: 合同 ID
        """
        site_tracker = get_site_tracker()
        
        from enhanced_app import db, ContractDelivery
        
        deliveries = db.session.query(ContractDelivery).filter_by(contract_id=contract_id).all()
        
        delayed_deliveries = []
        for delivery in deliveries:
            delivery_data = delivery.to_dict()
            delays = site_tracker.detect_delivery_delays(delivery_data)
            
            if delays:
                delayed_deliveries.append({
                    'delivery_id': delivery.id,
                    'delivery_no': delivery.delivery_no,
                    'site_name': delivery.site_name,
                    'site_code': delivery.site_code,
                    'current_status': delivery.status,
                    'delays': delays
                })
        
        return {
            'delayed_deliveries': delayed_deliveries,
            'total_delayed': len(delayed_deliveries),
            'message': '延期预警获取成功'
        }


class DeliveryTimelineResource(Resource):
    """交付时间轴 API"""
    method_decorators = {'get': [jwt_required()]}

    """交付时间轴 API"""
    
    def get(self, contract_id):
        """
        获取交付时间轴
        
        路径参数：
        contract_id: 合同 ID
        """
        site_tracker = get_site_tracker()
        
        from enhanced_app import db, Contract, ContractDelivery
        
        contract = db.session.get(Contract, contract_id)
        if not contract:
            return {'error': '合同不存在'}, 404
        
        # 获取站点信息
        site_info = {}
        if contract.site_info:
            import json
            try:
                site_info = json.loads(contract.site_info)
            except:
                pass
        
        # 添加计划开始日期
        if contract.signing_date:
            site_info['planned_start_date'] = contract.signing_date.isoformat()
        
        # 计算时间轴
        timeline = site_tracker.calculate_delivery_timeline(site_info)
        
        # 获取实际交付记录
        deliveries = db.session.query(ContractDelivery).filter_by(contract_id=contract_id).all()
        
        # 合并实际进度
        actual_progress = {}
        for delivery in deliveries:
            status = delivery.status
            if status not in actual_progress:
                actual_progress[status] = 0
            actual_progress[status] += 1
        
        return {
            'timeline': timeline,
            'actual_progress': actual_progress,
            'total_deliveries': len(deliveries),
            'message': '交付时间轴获取成功'
        }


class SiteEquipmentTrackerResource(Resource):
    """站点设备跟踪 API"""
    method_decorators = {'get': [jwt_required()]}

    """站点设备跟踪 API"""
    
    def get(self, contract_id, site_code):
        """
        获取特定站点的设备跟踪信息
        
        路径参数：
        contract_id: 合同 ID
        site_code: 站点代码
        
        查询参数：
        include_history: 是否包含历史记录（true/false）
        """
        from enhanced_app import db, ContractDelivery
        
        include_history = request.args.get('include_history', 'false').lower() == 'true'
        
        # 查询该站点的所有交付记录
        deliveries = db.session.query(ContractDelivery).filter_by(
            contract_id=contract_id,
            site_code=site_code
        ).order_by(ContractDelivery.created_at.desc()).all()
        
        if not deliveries:
            return {'error': '站点交付记录不存在'}, 404
        
        # 获取最新状态
        latest_delivery = deliveries[0]
        
        site_tracker = get_site_tracker()
        progress = site_tracker.calculate_progress_percentage(latest_delivery.status)
        
        # 构建响应
        response = {
            'contract_id': contract_id,
            'site_code': site_code,
            'site_name': latest_delivery.site_name,
            'current_status': latest_delivery.status,
            'progress_percentage': progress,
            'equipment_type': latest_delivery.equipment_type,
            'quantity': latest_delivery.quantity,
            'planned_date': latest_delivery.planned_date.isoformat() if latest_delivery.planned_date else None,
            'actual_date': latest_delivery.actual_date.isoformat() if latest_delivery.actual_date else None,
            'location': latest_delivery.location,
            'notes': latest_delivery.notes
        }
        
        if include_history:
            response['status_history'] = [d.to_dict() for d in deliveries]
        
        # 检测延期
        delays = site_tracker.detect_delivery_delays(latest_delivery.to_dict())
        response['delays'] = delays
        
        return {
            'site_tracking': response,
            'message': '站点设备跟踪信息获取成功'
        }


# 注册路由
delivery_tracking_api.add_resource(SiteDeliveryDashboardResource, '/dashboard/<int:contract_id>')
delivery_tracking_api.add_resource(DeliveryStatusTransitionResource, '/status/<int:delivery_id>')
delivery_tracking_api.add_resource(BOMValidationResource, '/bom/validate')
delivery_tracking_api.add_resource(DeliveryMilestoneResource, '/milestones/<int:contract_id>', '/milestones/<int:contract_id>/<string:milestone_key>')
delivery_tracking_api.add_resource(DeliveryDelayWarningResource, '/delays/<int:contract_id>')
delivery_tracking_api.add_resource(DeliveryTimelineResource, '/timeline/<int:contract_id>')
delivery_tracking_api.add_resource(SiteEquipmentTrackerResource, '/site/<int:contract_id>/<string:site_code>')
