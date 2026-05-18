"""
合同管理高级统计报表 API
提供全球项目交付看板、收入预测、风险分析等高级功能
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, extract, case
from datetime import datetime, timedelta
import json

# 延迟导入数据库模型
def get_db_and_models():
    from enhanced_app import db, Contract, ContractDelivery, ContractPayment, ContractRisk
    return db, Contract, ContractDelivery, ContractPayment, ContractRisk

contracts_statistics_bp = Blueprint('contracts_statistics', __name__, url_prefix='/contracts/statistics')

@contracts_statistics_bp.route('/global-delivery', methods=['GET'])
@jwt_required()
def get_global_delivery_dashboard():
    """全球项目交付看板 API"""
    db, Contract, ContractDelivery, ContractPayment, ContractRisk = get_db_and_models()
    
    current_user_id = get_jwt_identity()
    
    # 获取筛选参数
    region = request.args.get('region')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # 基础查询
    query = db.session.query(Contract)
    
    # 应用筛选
    if region:
        query = query.filter(Contract.region == region)
    if start_date:
        query = query.filter(Contract.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Contract.created_at <= datetime.fromisoformat(end_date))
    
    contracts = query.all()
    
    # 按区域统计
    region_stats = {}
    for contract in contracts:
        region = contract.region or '未分配'
        if region not in region_stats:
            region_stats[region] = {
                'total_contracts': 0,
                'total_amount': 0,
                'total_sites': 0,
                'accepted_sites': 0,
                'delayed_sites': 0
            }
        
        region_stats[region]['total_contracts'] += 1
        region_stats[region]['total_amount'] += contract.total_amount or 0
        
        # 统计站点交付情况
        deliveries = contract.deliveries if hasattr(contract, 'deliveries') else []
        region_stats[region]['total_sites'] += len(deliveries)
        region_stats[region]['accepted_sites'] += sum(
            1 for d in deliveries if d.status in ['accepted', 'closed']
        )
        region_stats[region]['delayed_sites'] += sum(
            1 for d in deliveries 
            if d.planned_date and d.planned_date < datetime.now() 
            and d.status not in ['accepted', 'closed']
        )
    
    # 计算全球总计
    global_total = {
        'total_contracts': sum(s['total_contracts'] for s in region_stats.values()),
        'total_amount': sum(s['total_amount'] for s in region_stats.values()),
        'total_sites': sum(s['total_sites'] for s in region_stats.values()),
        'accepted_sites': sum(s['accepted_sites'] for s in region_stats.values()),
        'delayed_sites': sum(s['delayed_sites'] for s in region_stats.values()),
        'overall_progress': 0
    }
    
    if global_total['total_sites'] > 0:
        global_total['overall_progress'] = round(
            global_total['accepted_sites'] / global_total['total_sites'] * 100, 2
        )
    
    # 按设备类型统计
    equipment_stats = {}
    for contract in contracts:
        deliveries = contract.deliveries if hasattr(contract, 'deliveries') else []
        for delivery in deliveries:
            equipment_type = delivery.equipment_type or '其他'
            if equipment_type not in equipment_stats:
                equipment_stats[equipment_type] = {
                    'count': 0,
                    'accepted': 0,
                    'pending': 0
                }
            equipment_stats[equipment_type]['count'] += 1
            if delivery.status in ['accepted', 'closed']:
                equipment_stats[equipment_type]['accepted'] += 1
            else:
                equipment_stats[equipment_type]['pending'] += 1
    
    # Top 交付区域排名
    top_regions = sorted(
        [(k, v['total_amount']) for k, v in region_stats.items()],
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    return jsonify({
        'global_summary': global_total,
        'region_breakdown': region_stats,
        'equipment_breakdown': equipment_stats,
        'top_regions': [{'region': r[0], 'amount': r[1]} for r in top_regions],
        'last_updated': datetime.now().isoformat(),
        'message': '全球交付看板数据获取成功'
    })


@contracts_statistics_bp.route('/revenue-forecast', methods=['GET'])
@jwt_required()
def get_revenue_forecast():
    """收入预测 API"""
    db, Contract, ContractDelivery, ContractPayment, ContractRisk = get_db_and_models()
    
    months = request.args.get('months', 6, type=int)
    contract_type = request.args.get('contract_type')
    
    # 获取所有活跃合同
    query = db.session.query(Contract).filter(
        Contract.status.in_(['active', 'executing'])
    )
    
    if contract_type:
        query = query.filter(Contract.contract_type == contract_type)
    
    contracts = query.all()
    
    # 月度收入预测
    monthly_forecast = {}
    current_month = datetime.now().replace(day=1)
    
    for i in range(months):
        month_key = (current_month + timedelta(days=30*i)).strftime('%Y-%m')
        monthly_forecast[month_key] = {
            'planned_revenue': 0,
            'confirmed_revenue': 0,
            'potential_revenue': 0
        }
    
    # 基于交付计划预测收入
    for contract in contracts:
        deliveries = contract.deliveries if hasattr(contract, 'deliveries') else []
        
        # 计算单站点平均价值
        total_deliveries = len(deliveries)
        if total_deliveries > 0:
            avg_site_value = (contract.total_amount or 0) / total_deliveries
        else:
            continue
        
        for delivery in deliveries:
            if delivery.planned_date:
                month_key = delivery.planned_date.strftime('%Y-%m')
                
                if month_key in monthly_forecast:
                    if delivery.status in ['accepted', 'closed']:
                        monthly_forecast[month_key]['confirmed_revenue'] += avg_site_value
                    elif delivery.status in ['in_production', 'shipped', 'in_transit']:
                        monthly_forecast[month_key]['confirmed_revenue'] += avg_site_value * 0.9
                    else:
                        monthly_forecast[month_key]['planned_revenue'] += avg_site_value
    
    # 基于付款计划预测现金流
    payment_forecast = {}
    for contract in contracts:
        payments = contract.payments if hasattr(contract, 'payments') else []
        
        for payment in payments:
            if payment.planned_date:
                month_key = payment.planned_date.strftime('%Y-%m')
                
                if month_key not in payment_forecast:
                    payment_forecast[month_key] = 0
                
                if payment.status == 'paid':
                    payment_forecast[month_key] += payment.actual_amount or 0
                else:
                    payment_forecast[month_key] += payment.planned_amount or 0
    
    # 汇总预测数据
    forecast_summary = {
        'total_planned': sum(m['planned_revenue'] for m in monthly_forecast.values()),
        'total_confirmed': sum(m['confirmed_revenue'] for m in monthly_forecast.values()),
        'total_potential': sum(m['potential_revenue'] for m in monthly_forecast.values()),
        'confidence_rate': 0
    }
    
    total_forecast = forecast_summary['total_planned'] + forecast_summary['total_confirmed']
    if total_forecast > 0:
        forecast_summary['confidence_rate'] = round(
            forecast_summary['total_confirmed'] / total_forecast * 100, 2
        )
    
    # 按合同类型分析
    type_breakdown = {}
    for contract in contracts:
        ctype = contract.contract_type or '其他'
        if ctype not in type_breakdown:
            type_breakdown[ctype] = {
                'contract_count': 0,
                'total_amount': 0,
                'delivery_progress': 0,
                'total_deliveries': 0,
                'accepted_deliveries': 0
            }
        
        type_breakdown[ctype]['contract_count'] += 1
        type_breakdown[ctype]['total_amount'] += contract.total_amount or 0
        
        deliveries = contract.deliveries if hasattr(contract, 'deliveries') else []
        type_breakdown[ctype]['total_deliveries'] += len(deliveries)
        type_breakdown[ctype]['accepted_deliveries'] += sum(
            1 for d in deliveries if d.status in ['accepted', 'closed']
        )
    
    # 计算各类型交付进度
    for ctype in type_breakdown:
        total = type_breakdown[ctype]['total_deliveries']
        accepted = type_breakdown[ctype]['accepted_deliveries']
        type_breakdown[ctype]['delivery_progress'] = round(
            accepted / total * 100 if total > 0 else 0, 2
        )
    
    return jsonify({
        'monthly_forecast': monthly_forecast,
        'payment_forecast': payment_forecast,
        'forecast_summary': forecast_summary,
        'type_breakdown': type_breakdown,
        'forecast_period_months': months,
        'generated_at': datetime.now().isoformat(),
        'message': '收入预测数据生成成功'
    })


@contracts_statistics_bp.route('/risk-analysis', methods=['GET'])
@jwt_required()
def get_risk_analysis():
    """风险分析仪表板 API"""
    db, Contract, ContractDelivery, ContractPayment, ContractRisk = get_db_and_models()
    
    region = request.args.get('region')
    risk_category = request.args.get('risk_category')
    
    # 获取所有合同
    query = db.session.query(Contract)
    if region:
        query = query.filter(Contract.region == region)
    
    contracts = query.all()
    
    # 风险等级分布
    risk_level_distribution = {'high': 0, 'medium': 0, 'low': 0}
    
    # 风险类别统计
    risk_category_stats = {
        'export_control': 0,
        'intellectual_property': 0,
        'delivery': 0,
        'financial': 0,
        'compliance': 0
    }
    
    # 高风险合同列表
    high_risk_contracts = []
    
    # 区域风险热力图数据
    region_risk_map = {}
    
    for contract in contracts:
        # 统计风险等级
        risk_level = contract.risk_level or 'low'
        if risk_level in risk_level_distribution:
            risk_level_distribution[risk_level] += 1
        
        # 识别高风险合同
        if risk_level == 'high':
            high_risk_contracts.append({
                'contract_id': contract.id,
                'contract_no': contract.contract_no,
                'title': contract.title,
                'region': contract.region,
                'country': contract.country,
                'risk_level': contract.risk_level,
                'total_amount': contract.total_amount
            })
        
        # 区域风险统计
        region = contract.region or '未分配'
        if region not in region_risk_map:
            region_risk_map[region] = {
                'total_contracts': 0,
                'high_risk_contracts': 0,
                'total_amount': 0,
                'high_risk_amount': 0
            }
        
        region_risk_map[region]['total_contracts'] += 1
        region_risk_map[region]['total_amount'] += contract.total_amount or 0
        
        if contract.risk_level == 'high':
            region_risk_map[region]['high_risk_contracts'] += 1
            region_risk_map[region]['high_risk_amount'] += contract.total_amount or 0
        
        # 检查具体风险类别
        if contract.export_control_applicable:
            risk_category_stats['export_control'] += 1
        
        if contract.ip_protection_required:
            risk_category_stats['intellectual_property'] += 1
        
        # 检查交付风险
        if contract.delivery_progress and contract.delivery_progress < 50:
            risk_category_stats['delivery'] += 1
        
        # 检查财务风险（简化）
        if contract.total_amount and contract.total_amount > 10000000:
            risk_category_stats['financial'] += 1
    
    # 计算风险指数
    total_contracts = len(contracts)
    overall_risk_index = 0
    if total_contracts > 0:
        overall_risk_index = round(
            (risk_level_distribution['high'] * 3 + 
             risk_level_distribution['medium'] * 2 + 
             risk_level_distribution['low'] * 1) / total_contracts, 2
        )
    
    # Top 风险区域
    top_risk_regions = sorted(
        [(k, v['high_risk_contracts']) for k, v in region_risk_map.items()],
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    return jsonify({
        'risk_level_distribution': risk_level_distribution,
        'risk_category_stats': risk_category_stats,
        'high_risk_contracts': high_risk_contracts[:20],
        'region_risk_map': region_risk_map,
        'top_risk_regions': [{'region': r[0], 'high_risk_count': r[1]} for r in top_risk_regions],
        'overall_risk_index': overall_risk_index,
        'total_contracts': total_contracts,
        'generated_at': datetime.now().isoformat(),
        'message': '风险分析数据生成成功'
    })


@contracts_statistics_bp.route('/type-analysis', methods=['GET'])
@jwt_required()
def get_type_analysis():
    """合同类型分析 API"""
    db, Contract, ContractDelivery, ContractPayment, ContractRisk = get_db_and_models()
    
    time_range = request.args.get('time_range', 'all')
    
    # 计算时间范围
    query = db.session.query(Contract)
    
    if time_range == 'last_30_days':
        cutoff_date = datetime.now() - timedelta(days=30)
        query = query.filter(Contract.created_at >= cutoff_date)
    elif time_range == 'last_90_days':
        cutoff_date = datetime.now() - timedelta(days=90)
        query = query.filter(Contract.created_at >= cutoff_date)
    elif time_range == 'last_year':
        cutoff_date = datetime.now() - timedelta(days=365)
        query = query.filter(Contract.created_at >= cutoff_date)
    
    contracts = query.all()
    
    # 按类型统计
    type_stats = {}
    for contract in contracts:
        ctype = contract.contract_type or '其他'
        
        if ctype not in type_stats:
            type_stats[ctype] = {
                'count': 0,
                'total_amount': 0,
                'avg_amount': 0,
                'status_distribution': {
                    'draft': 0,
                    'pending_approval': 0,
                    'active': 0,
                    'executing': 0,
                    'completed': 0,
                    'terminated': 0
                },
                'avg_delivery_progress': 0,
                'total_deliveries': 0
            }
        
        type_stats[ctype]['count'] += 1
        type_stats[ctype]['total_amount'] += contract.total_amount or 0
        type_stats[ctype]['status_distribution'][contract.status] = \
            type_stats[ctype]['status_distribution'].get(contract.status, 0) + 1
        
        # 统计交付进度
        if contract.delivery_progress is not None:
            type_stats[ctype]['avg_delivery_progress'] += contract.delivery_progress
        
        deliveries = contract.deliveries if hasattr(contract, 'deliveries') else []
        type_stats[ctype]['total_deliveries'] += len(deliveries)
    
    # 计算平均值
    for ctype in type_stats:
        count = type_stats[ctype]['count']
        if count > 0:
            type_stats[ctype]['avg_amount'] = round(type_stats[ctype]['total_amount'] / count, 2)
            type_stats[ctype]['avg_delivery_progress'] = round(
                type_stats[ctype]['avg_delivery_progress'] / count, 2
            )
    
    # 按金额排序
    sorted_types = sorted(
        type_stats.items(),
        key=lambda x: x[1]['total_amount'],
        reverse=True
    )
    
    return jsonify({
        'type_statistics': dict(sorted_types),
        'time_range': time_range,
        'total_contracts': len(contracts),
        'generated_at': datetime.now().isoformat(),
        'message': '合同类型分析数据生成成功'
    })


@contracts_statistics_bp.route('/regional-performance', methods=['GET'])
@jwt_required()
def get_regional_performance():
    """区域绩效分析 API"""
    db, Contract, ContractDelivery, ContractPayment, ContractRisk = get_db_and_models()
    
    # 获取所有合同
    contracts = db.session.query(Contract).all()
    
    # 按区域统计
    region_stats = {}
    
    for contract in contracts:
        region = contract.region or '未分配'
        country = contract.country or '未知'
        
        if region not in region_stats:
            region_stats[region] = {
                'region': region,
                'countries': {},
                'total_contracts': 0,
                'total_amount': 0,
                'total_sites': 0,
                'accepted_sites': 0,
                'avg_delivery_days': 0,
                'customer_satisfaction': 0,
                'revenue_contribution': 0
            }
        
        # 国家维度统计
        if country not in region_stats[region]['countries']:
            region_stats[region]['countries'][country] = {
                'contracts': 0,
                'amount': 0,
                'sites': 0
            }
        
        region_stats[region]['countries'][country]['contracts'] += 1
        region_stats[region]['countries'][country]['amount'] += contract.total_amount or 0
        
        # 区域汇总
        region_stats[region]['total_contracts'] += 1
        region_stats[region]['total_amount'] += contract.total_amount or 0
        
        # 站点统计
        deliveries = contract.deliveries if hasattr(contract, 'deliveries') else []
        region_stats[region]['total_sites'] += len(deliveries)
        region_stats[region]['accepted_sites'] += sum(
            1 for d in deliveries if d.status in ['accepted', 'closed']
        )
    
    # 计算各区域交付率
    for region in region_stats:
        total_sites = region_stats[region]['total_sites']
        accepted_sites = region_stats[region]['accepted_sites']
        
        if total_sites > 0:
            region_stats[region]['delivery_rate'] = round(
                accepted_sites / total_sites * 100, 2
            )
        else:
            region_stats[region]['delivery_rate'] = 0
    
    # 计算收入贡献占比
    total_revenue = sum(s['total_amount'] for s in region_stats.values())
    for region in region_stats:
        if total_revenue > 0:
            region_stats[region]['revenue_contribution'] = round(
                region_stats[region]['total_amount'] / total_revenue * 100, 2
            )
    
    # 按交付率排序
    sorted_regions = sorted(
        region_stats.items(),
        key=lambda x: x[1].get('delivery_rate', 0),
        reverse=True
    )
    
    return jsonify({
        'regional_performance': dict(sorted_regions),
        'total_regions': len(region_stats),
        'total_revenue': total_revenue,
        'generated_at': datetime.now().isoformat(),
        'message': '区域绩效分析数据生成成功'
    })


@contracts_statistics_bp.route('/executive-dashboard', methods=['GET'])
@jwt_required()
def get_executive_dashboard():
    """高管驾驶舱 API - 综合数据汇总"""
    db, Contract, ContractDelivery, ContractPayment, ContractRisk = get_db_and_models()
    
    # 获取关键指标
    total_contracts = db.session.query(func.count(Contract.id)).scalar()
    total_amount = db.session.query(func.sum(Contract.total_amount)).scalar() or 0
    
    # 活跃合同数
    active_contracts = db.session.query(func.count(Contract.id)).filter(
        Contract.status.in_(['active', 'executing'])
    ).scalar()
    
    # 本月新增合同
    current_month_start = datetime.now().replace(day=1)
    new_contracts_this_month = db.session.query(func.count(Contract.id)).filter(
        Contract.created_at >= current_month_start
    ).scalar()
    
    # 交付进度
    all_deliveries = db.session.query(ContractDelivery).all()
    total_deliveries = len(all_deliveries)
    accepted_deliveries = sum(1 for d in all_deliveries if d.status in ['accepted', 'closed'])
    overall_delivery_progress = round(accepted_deliveries / total_deliveries * 100, 2) if total_deliveries > 0 else 0
    
    # 高风险合同数
    high_risk_contracts = db.session.query(func.count(Contract.id)).filter(
        Contract.risk_level == 'high'
    ).scalar()
    
    # 待审批合同
    pending_approvals = db.session.query(func.count(Contract.id)).filter(
        Contract.status == 'pending_approval'
    ).scalar()
    
    # 本月预计收款
    current_month_end = (current_month_start + timedelta(days=32)).replace(day=1)
    expected_collection = db.session.query(func.sum(ContractPayment.planned_amount)).filter(
        ContractPayment.planned_date >= current_month_start,
        ContractPayment.planned_date < current_month_end,
        ContractPayment.status != 'paid'
    ).scalar() or 0
    
    # 出口管制合同
    export_control_contracts = db.session.query(func.count(Contract.id)).filter(
        Contract.export_control_applicable == True
    ).scalar()
    
    # 知识产权相关合同
    ip_contracts = db.session.query(func.count(Contract.id)).filter(
        Contract.ip_protection_required == True
    ).scalar()
    
    # 区域分布 Top 5
    region_query = db.session.query(
        Contract.region,
        func.count(Contract.id),
        func.sum(Contract.total_amount)
    ).group_by(Contract.region).all()
    
    top_regions = sorted(
        [{'region': r[0], 'count': r[1], 'amount': r[2] or 0} for r in region_query if r[0]],
        key=lambda x: x['amount'],
        reverse=True
    )[:5]
    
    # 合同类型分布
    type_query = db.session.query(
        Contract.contract_type,
        func.count(Contract.id)
    ).group_by(Contract.contract_type).all()
    
    contract_types = [{'type': t[0] or '其他', 'count': c} for t, c in type_query]
    
    return jsonify({
        'key_metrics': {
            'total_contracts': total_contracts or 0,
            'total_amount': total_amount,
            'active_contracts': active_contracts or 0,
            'new_contracts_this_month': new_contracts_this_month or 0,
            'delivery_progress_percentage': overall_delivery_progress,
            'high_risk_contracts': high_risk_contracts or 0,
            'pending_approvals': pending_approvals or 0,
            'expected_collection_this_month': expected_collection,
            'export_control_contracts': export_control_contracts or 0,
            'ip_related_contracts': ip_contracts or 0
        },
        'top_regions': top_regions,
        'contract_type_distribution': contract_types,
        'last_updated': datetime.now().isoformat(),
        'message': '高管驾驶舱数据获取成功'
    })
