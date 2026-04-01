"""
站点级交付跟踪服务
实现从发货到验收的全流程跟踪，支持站点维度的进度管理
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


class DeliveryStatus(Enum):
    """交付状态枚举"""
    PENDING = "pending"  # 待处理
    IN_PRODUCTION = "in_production"  # 生产中
    SHIPPED = "shipped"  # 已发货
    IN_TRANSIT = "in_transit"  # 运输中
    CUSTOMS_CLEARANCE = "customs_clearance"  # 清关中
    ARRIVED = "arrived"  # 已到货
    INSTALLING = "installing"  # 安装中
    COMMISSIONING = "commissioning"  # 调试中
    INITIAL_ACCEPTANCE = "initial_acceptance"  # 初验中 (PAC)
    FINAL_ACCEPTANCE = "final_acceptance"  # 终验中 (FAC)
    ACCEPTED = "accepted"  # 已验收
    CLOSED = "closed"  # 已关闭


class SiteDeliveryTracker:
    """站点交付跟踪器"""
    
    # 状态流转定义
    STATUS_FLOW = {
        DeliveryStatus.PENDING: [DeliveryStatus.IN_PRODUCTION],
        DeliveryStatus.IN_PRODUCTION: [DeliveryStatus.SHIPPED],
        DeliveryStatus.SHIPPED: [DeliveryStatus.IN_TRANSIT],
        DeliveryStatus.IN_TRANSIT: [DeliveryStatus.CUSTOMS_CLEARANCE, DeliveryStatus.ARRIVED],
        DeliveryStatus.CUSTOMS_CLEARANCE: [DeliveryStatus.ARRIVED],
        DeliveryStatus.ARRIVED: [DeliveryStatus.INSTALLING],
        DeliveryStatus.INSTALLING: [DeliveryStatus.COMMISSIONING],
        DeliveryStatus.COMMISSIONING: [DeliveryStatus.INITIAL_ACCEPTANCE],
        DeliveryStatus.INITIAL_ACCEPTANCE: [DeliveryStatus.FINAL_ACCEPTANCE, DeliveryStatus.ACCEPTED],
        DeliveryStatus.FINAL_ACCEPTANCE: [DeliveryStatus.ACCEPTED],
        DeliveryStatus.ACCEPTED: [DeliveryStatus.CLOSED],
        DeliveryStatus.CLOSED: []
    }
    
    # 每个状态的标准耗时（天）
    STANDARD_DURATION = {
        DeliveryStatus.PENDING: 3,
        DeliveryStatus.IN_PRODUCTION: 15,
        DeliveryStatus.SHIPPED: 1,
        DeliveryStatus.IN_TRANSIT: 7,
        DeliveryStatus.CUSTOMS_CLEARANCE: 5,
        DeliveryStatus.ARRIVED: 2,
        DeliveryStatus.INSTALLING: 10,
        DeliveryStatus.COMMISSIONING: 5,
        DeliveryStatus.INITIAL_ACCEPTANCE: 7,
        DeliveryStatus.FINAL_ACCEPTANCE: 14,
        DeliveryStatus.ACCEPTED: 0,
        DeliveryStatus.CLOSED: 0
    }
    
    def __init__(self):
        pass
    
    def validate_status_transition(self, current_status: str, new_status: str) -> Dict[str, Any]:
        """
        验证状态流转是否合法
        
        Args:
            current_status: 当前状态
            new_status: 新状态
            
        Returns:
            验证结果
        """
        try:
            current = DeliveryStatus(current_status)
            new = DeliveryStatus(new_status)
        except ValueError:
            return {
                'valid': False,
                'error': '无效的状态值',
                'allowed_transitions': []
            }
        
        allowed = self.STATUS_FLOW.get(current, [])
        is_valid = new in allowed
        
        return {
            'valid': is_valid,
            'current_status': current_status,
            'new_status': new_status,
            'allowed_transitions': [s.value for s in allowed],
            'message': '状态流转合法' if is_valid else f'不允许从 {current_status} 流转到 {new_status}'
        }
    
    def calculate_delivery_timeline(self, site_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算交付时间轴
        
        Args:
            site_info: 站点信息（包含计划开始日期等）
            
        Returns:
            时间轴预测
        """
        start_date_str = site_info.get('planned_start_date')
        if not start_date_str:
            return {'error': '缺少计划开始日期'}
        
        try:
            start_date = datetime.fromisoformat(start_date_str)
        except:
            start_date = datetime.now()
        
        timeline = []
        current_date = start_date
        
        for status in DeliveryStatus:
            duration = self.STANDARD_DURATION.get(status, 0)
            if duration > 0:
                timeline.append({
                    'status': status.value,
                    'status_name': self._get_status_name(status),
                    'planned_date': current_date.isoformat(),
                    'duration_days': duration
                })
                current_date = current_date.replace(day=current_date.day + duration)
        
        total_duration = sum(self.STANDARD_DURATION.values())
        
        return {
            'timeline': timeline,
            'total_duration_days': total_duration,
            'estimated_completion_date': current_date.isoformat()
        }
    
    def _get_status_name(self, status: DeliveryStatus) -> str:
        """获取状态中文名称"""
        names = {
            DeliveryStatus.PENDING: "待处理",
            DeliveryStatus.IN_PRODUCTION: "生产中",
            DeliveryStatus.SHIPPED: "已发货",
            DeliveryStatus.IN_TRANSIT: "运输中",
            DeliveryStatus.CUSTOMS_CLEARANCE: "清关中",
            DeliveryStatus.ARRIVED: "已到货",
            DeliveryStatus.INSTALLING: "安装中",
            DeliveryStatus.COMMISSIONING: "调试中",
            DeliveryStatus.INITIAL_ACCEPTANCE: "初验中 (PAC)",
            DeliveryStatus.FINAL_ACCEPTANCE: "终验中 (FAC)",
            DeliveryStatus.ACCEPTED: "已验收",
            DeliveryStatus.CLOSED: "已关闭"
        }
        return names.get(status, status.value)
    
    def calculate_progress_percentage(self, current_status: str) -> float:
        """
        计算交付进度百分比
        
        Args:
            current_status: 当前状态
            
        Returns:
            进度百分比（0-100）
        """
        try:
            status = DeliveryStatus(current_status)
        except ValueError:
            return 0.0
        
        # 定义每个状态的进度值
        progress_map = {
            DeliveryStatus.PENDING: 0,
            DeliveryStatus.IN_PRODUCTION: 10,
            DeliveryStatus.SHIPPED: 20,
            DeliveryStatus.IN_TRANSIT: 30,
            DeliveryStatus.CUSTOMS_CLEARANCE: 40,
            DeliveryStatus.ARRIVED: 50,
            DeliveryStatus.INSTALLING: 60,
            DeliveryStatus.COMMISSIONING: 75,
            DeliveryStatus.INITIAL_ACCEPTANCE: 85,
            DeliveryStatus.FINAL_ACCEPTANCE: 95,
            DeliveryStatus.ACCEPTED: 100,
            DeliveryStatus.CLOSED: 100
        }
        
        return float(progress_map.get(status, 0))
    
    def detect_delivery_delays(self, delivery_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        检测交付延期
        
        Args:
            delivery_data: 交付数据（包含计划日期和实际日期）
            
        Returns:
            延期警告列表
        """
        delays = []
        
        planned_date_str = delivery_data.get('planned_date')
        actual_date_str = delivery_data.get('actual_date')
        current_status = delivery_data.get('status', 'pending')
        
        if not planned_date_str:
            return delays
        
        try:
            planned_date = datetime.fromisoformat(planned_date_str)
        except:
            return delays
        
        # 如果已有实际日期，检查是否延期
        if actual_date_str:
            try:
                actual_date = datetime.fromisoformat(actual_date_str)
                if actual_date > planned_date:
                    delay_days = (actual_date - planned_date).days
                    delays.append({
                        'type': 'completed_delay',
                        'severity': 'high' if delay_days > 7 else 'medium',
                        'delay_days': delay_days,
                        'message': f'实际日期比计划日期延期{delay_days}天'
                    })
            except:
                pass
        else:
            # 如果当前日期已超过计划日期，检测为待办延期
            if datetime.now() > planned_date and current_status in ['pending', 'in_production']:
                delay_days = (datetime.now() - planned_date).days
                delays.append({
                    'type': 'pending_delay',
                    'severity': 'high' if delay_days > 7 else 'medium',
                    'delay_days': delay_days,
                    'message': f'计划任务已逾期{delay_days}天'
                })
        
        return delays
    
    def get_site_delivery_dashboard(self, contract_id: int, deliveries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成站点交付看板
        
        Args:
            contract_id: 合同 ID
            deliveries: 交付记录列表
            
        Returns:
            交付看板数据
        """
        if not deliveries:
            return {
                'contract_id': contract_id,
                'total_sites': 0,
                'summary': {},
                'status_distribution': {},
                'delayed_sites': [],
                'recent_activities': []
            }
        
        # 统计各状态站点数量
        status_count = {}
        delayed_sites = []
        total_equipment = 0
        
        for delivery in deliveries:
            status = delivery.get('status', 'pending')
            status_count[status] = status_count.get(status, 0) + 1
            total_equipment += delivery.get('quantity', 0)
            
            # 检测延期
            delays = self.detect_delivery_delays(delivery)
            if delays:
                delayed_sites.append({
                    'site_name': delivery.get('site_name'),
                    'site_code': delivery.get('site_code'),
                    'delays': delays
                })
        
        # 计算进度
        accepted_count = status_count.get('accepted', 0) + status_count.get('closed', 0)
        total_sites = len(deliveries)
        progress_percentage = (accepted_count / total_sites * 100) if total_sites > 0 else 0
        
        return {
            'contract_id': contract_id,
            'total_sites': total_sites,
            'total_equipment': total_equipment,
            'summary': {
                'progress_percentage': round(progress_percentage, 2),
                'accepted_sites': accepted_count,
                'pending_sites': total_sites - accepted_count,
                'delayed_sites_count': len(delayed_sites)
            },
            'status_distribution': status_count,
            'delayed_sites': delayed_sites,
            'recent_activities': self._get_recent_activities(deliveries)
        }
    
    def _get_recent_activities(self, deliveries: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近活动"""
        activities = []
        
        for delivery in deliveries:
            updated_at = delivery.get('updated_at')
            if updated_at:
                activities.append({
                    'site_name': delivery.get('site_name'),
                    'site_code': delivery.get('site_code'),
                    'activity': f'状态更新为 {delivery.get("status")}',
                    'timestamp': updated_at
                })
        
        # 按时间排序
        activities.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return activities[:limit]


class BOMManager:
    """物料清单（BOM）管理器"""
    
    def __init__(self):
        pass
    
    def validate_bom(self, bom_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        验证 BOM 数据
        
        Args:
            bom_data: BOM 数据列表
            
        Returns:
            验证结果
        """
        errors = []
        warnings = []
        
        required_fields = ['equipment_type', 'model', 'quantity', 'unit_price']
        
        for i, item in enumerate(bom_data):
            # 检查必填字段
            for field in required_fields:
                if field not in item:
                    errors.append(f'第{i+1}项缺少必填字段：{field}')
            
            # 检查数量
            quantity = item.get('quantity', 0)
            if quantity <= 0:
                errors.append(f'第{i+1}项数量必须大于 0')
            
            # 检查单价
            unit_price = item.get('unit_price', 0)
            if unit_price < 0:
                errors.append(f'第{i+1}项单价不能为负数')
            
            # 检查设备类型
            equipment_type = item.get('equipment_type', '')
            if not equipment_type:
                warnings.append(f'第{i+1}项未指定设备类型')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'total_items': len(bom_data)
        }
    
    def calculate_bom_total(self, bom_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算 BOM 总金额
        
        Args:
            bom_data: BOM 数据列表
            
        Returns:
            计算结果
        """
        total_amount = 0.0
        item_count = 0
        
        for item in bom_data:
            quantity = item.get('quantity', 0)
            unit_price = item.get('unit_price', 0)
            total_amount += quantity * unit_price
            item_count += 1
        
        return {
            'total_amount': total_amount,
            'item_count': item_count,
            'currency': bom_data[0].get('currency', 'CNY') if bom_data else 'CNY'
        }
    
    def group_bom_by_category(self, bom_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        按类别分组 BOM
        
        Args:
            bom_data: BOM 数据列表
            
        Returns:
            分组结果
        """
        categories = {}
        
        for item in bom_data:
            category = item.get('category', 'other')
            if category not in categories:
                categories[category] = {
                    'items': [],
                    'total_quantity': 0,
                    'total_amount': 0
                }
            
            categories[category]['items'].append(item)
            categories[category]['total_quantity'] += item.get('quantity', 0)
            categories[category]['total_amount'] += item.get('quantity', 0) * item.get('unit_price', 0)
        
        return {
            'categories': categories,
            'total_categories': len(categories)
        }


class DeliveryMilestoneTracker:
    """交付里程碑跟踪器"""
    
    def __init__(self):
        self.milestones = [
            {'name': '合同生效', 'key': 'contract_effective', 'duration_days': 0},
            {'name': '生产完成', 'key': 'production_complete', 'duration_days': 15},
            {'name': '设备发货', 'key': 'shipment', 'duration_days': 1},
            {'name': '到港清关', 'key': 'customs_clearance', 'duration_days': 5},
            {'name': '站点到货', 'key': 'site_arrival', 'duration_days': 7},
            {'name': '安装完成', 'key': 'installation_complete', 'duration_days': 10},
            {'name': '调试完成', 'key': 'commissioning_complete', 'duration_days': 5},
            {'name': '初验 (PAC)', 'key': 'pac', 'duration_days': 7},
            {'name': '终验 (FAC)', 'key': 'fac', 'duration_days': 14}
        ]
    
    def generate_milestone_plan(self, start_date: str) -> List[Dict[str, Any]]:
        """
        生成里程碑计划
        
        Args:
            start_date: 开始日期（ISO 格式）
            
        Returns:
            里程碑计划
        """
        try:
            current_date = datetime.fromisoformat(start_date)
        except:
            current_date = datetime.now()
        
        milestone_plan = []
        
        for milestone in self.milestones:
            milestone_plan.append({
                'milestone_name': milestone['name'],
                'milestone_key': milestone['key'],
                'planned_date': current_date.isoformat(),
                'duration_days': milestone['duration_days'],
                'status': 'pending'
            })
            
            # 累加天数到下一个里程碑
            from datetime import timedelta
            current_date = current_date + timedelta(days=milestone['duration_days'])
        
        return milestone_plan
    
    def update_milestone_status(self, milestone_plan: List[Dict[str, Any]], 
                                milestone_key: str, status: str, 
                                actual_date: str = None) -> Dict[str, Any]:
        """
        更新里程碑状态
        
        Args:
            milestone_plan: 里程碑计划
            milestone_key: 里程碑标识
            status: 新状态（completed/pending/delayed）
            actual_date: 实际日期
            
        Returns:
            更新结果
        """
        for milestone in milestone_plan:
            if milestone['milestone_key'] == milestone_key:
                milestone['status'] = status
                if actual_date:
                    milestone['actual_date'] = actual_date
                
                # 检查是否延期
                if actual_date and milestone.get('planned_date'):
                    planned = datetime.fromisoformat(milestone['planned_date'])
                    actual = datetime.fromisoformat(actual_date)
                    if actual > planned:
                        milestone['delay_days'] = (actual - planned).days
                        milestone['status'] = 'delayed'
                
                return {
                    'success': True,
                    'milestone': milestone,
                    'message': '里程碑状态更新成功'
                }
        
        return {
            'success': False,
            'error': '未找到指定的里程碑'
        }
    
    def calculate_milestone_progress(self, milestone_plan: List[Dict[str, Any]]) -> float:
        """
        计算里程碑进度
        
        Args:
            milestone_plan: 里程碑计划
            
        Returns:
            进度百分比
        """
        if not milestone_plan:
            return 0.0
        
        completed = sum(1 for m in milestone_plan if m.get('status') == 'completed')
        return round(completed / len(milestone_plan) * 100, 2)


# 单例模式
_site_tracker = None
_bom_manager = None
_milestone_tracker = None


def get_site_tracker() -> SiteDeliveryTracker:
    """获取站点跟踪器实例"""
    global _site_tracker
    if _site_tracker is None:
        _site_tracker = SiteDeliveryTracker()
    return _site_tracker


def get_bom_manager() -> BOMManager:
    """获取 BOM 管理器实例"""
    global _bom_manager
    if _bom_manager is None:
        _bom_manager = BOMManager()
    return _bom_manager


def get_milestone_tracker() -> DeliveryMilestoneTracker:
    """获取里程碑跟踪器实例"""
    global _milestone_tracker
    if _milestone_tracker is None:
        _milestone_tracker = DeliveryMilestoneTracker()
    return _milestone_tracker
