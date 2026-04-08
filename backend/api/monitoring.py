#!/usr/bin/env python3
"""
系统监控和健康检查API
提供性能监控、健康检查、日志分析、告警功能
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from functools import wraps
import psutil
import os
import time
import logging
import json

logger = logging.getLogger(__name__)
monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/monitoring')

# 性能指标存储
performance_metrics = []
health_checks = {}
alerts = []

# ==================== 系统健康检查 ====================
@monitoring_bp.route('/health', methods=['GET'])
def health_check():
    """系统健康检查"""
    try:
        checks = {
            'database': check_database(),
            'disk': check_disk(),
            'memory': check_memory(),
            'api': check_api()
        }
        
        # 总体状态
        overall_status = 'healthy'
        for check in checks.values():
            if check['status'] == 'critical':
                overall_status = 'critical'
                break
            elif check['status'] == 'warning' and overall_status == 'healthy':
                overall_status = 'warning'
        
        return jsonify({
            'success': True,
            'data': {
                'status': overall_status,
                'timestamp': datetime.now().isoformat(),
                'checks': checks
            }
        })
    except Exception as e:
        logger.error(f"健康检查错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': {'status': 'critical'}
        }), 500

def check_database():
    """检查数据库连接"""
    try:
        from enhanced_app import db
        db.session.execute('SELECT 1')
        return {'status': 'healthy', 'message': '数据库连接正常'}
    except Exception as e:
        return {'status': 'critical', 'message': f'数据库连接失败: {str(e)}'}

def check_disk():
    """检查磁盘空间"""
    try:
        disk = psutil.disk_usage('/')
        percent = disk.percent
        
        if percent > 90:
            status = 'critical'
        elif percent > 80:
            status = 'warning'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'message': f'磁盘使用率: {percent}%',
            'details': {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': percent
            }
        }
    except Exception as e:
        return {'status': 'warning', 'message': f'磁盘检查失败: {str(e)}'}

def check_memory():
    """检查内存使用"""
    try:
        memory = psutil.virtual_memory()
        percent = memory.percent
        
        if percent > 90:
            status = 'critical'
        elif percent > 80:
            status = 'warning'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'message': f'内存使用率: {percent}%',
            'details': {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': percent
            }
        }
    except Exception as e:
        return {'status': 'warning', 'message': f'内存检查失败: {str(e)}'}

def check_api():
    """检查API响应"""
    try:
        # 简单的API响应时间检查
        start_time = time.time()
        # 这里可以添加实际的API调用
        response_time = (time.time() - start_time) * 1000
        
        if response_time > 5000:
            status = 'critical'
        elif response_time > 1000:
            status = 'warning'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'message': f'API响应时间: {response_time:.2f}ms',
            'details': {'response_time_ms': response_time}
        }
    except Exception as e:
        return {'status': 'warning', 'message': f'API检查失败: {str(e)}'}

# ==================== 性能监控 ====================
@monitoring_bp.route('/performance', methods=['GET'])
@jwt_required()
def get_performance_metrics():
    """获取性能指标"""
    try:
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # 内存使用
        memory = psutil.virtual_memory()
        
        # 磁盘使用
        disk = psutil.disk_usage('/')
        
        # 网络IO
        net_io = psutil.net_io_counters()
        
        # 进程信息
        process = psutil.Process()
        process_info = {
            'pid': process.pid,
            'memory_percent': process.memory_percent(),
            'cpu_percent': process.cpu_percent(),
            'num_threads': process.num_threads(),
            'create_time': datetime.fromtimestamp(process.create_time()).isoformat()
        }
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'percent': cpu_percent,
                'count': cpu_count,
                'per_cpu': psutil.cpu_percent(interval=1, percpu=True)
            },
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            },
            'network': {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            },
            'process': process_info
        }
        
        # 保存指标
        performance_metrics.append(metrics)
        # 只保留最近100条
        if len(performance_metrics) > 100:
            performance_metrics.pop(0)
        
        return jsonify({
            'success': True,
            'data': metrics
        })
    except Exception as e:
        logger.error(f"获取性能指标错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@monitoring_bp.route('/performance/history', methods=['GET'])
@jwt_required()
def get_performance_history():
    """获取性能历史"""
    try:
        # 获取时间范围
        hours = request.args.get('hours', 24, type=int)
        
        # 过滤最近的数据
        cutoff_time = datetime.now() - timedelta(hours=hours)
        filtered_metrics = [
            m for m in performance_metrics
            if datetime.fromisoformat(m['timestamp']) > cutoff_time
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'metrics': filtered_metrics,
                'count': len(filtered_metrics)
            }
        })
    except Exception as e:
        logger.error(f"获取性能历史错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== 数据库监控 ====================
@monitoring_bp.route('/database', methods=['GET'])
@jwt_required()
def get_database_stats():
    """获取数据库统计"""
    try:
        from enhanced_app import db
        
        # 获取表统计
        tables = ['users', 'projects', 'bugs', 'tasks', 'materials', 'contracts', 'attendance']
        table_stats = []
        
        for table in tables:
            try:
                result = db.session.execute(f'SELECT COUNT(*) FROM {table}').scalar()
                table_stats.append({'name': table, 'count': result})
            except:
                table_stats.append({'name': table, 'count': 0})
        
        # 获取数据库大小（SQLite）
        db_path = db.engine.url.database
        db_size = os.path.getsize(db_path) if db_path and os.path.exists(db_path) else 0
        
        return jsonify({
            'success': True,
            'data': {
                'tables': table_stats,
                'database_size': db_size,
                'database_size_mb': round(db_size / 1024 / 1024, 2)
            }
        })
    except Exception as e:
        logger.error(f"获取数据库统计错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== API监控 ====================
@monitoring_bp.route('/api/stats', methods=['GET'])
@jwt_required()
def get_api_stats():
    """获取API统计"""
    try:
        # 模拟API统计数据
        # 实际应从日志或中间件获取
        api_stats = {
            'total_requests': 12580,
            'avg_response_time': 125,
            'error_rate': 0.5,
            'top_endpoints': [
                {'endpoint': '/api/projects', 'count': 3200},
                {'endpoint': '/api/bugs', 'count': 2800},
                {'endpoint': '/api/auth/login', 'count': 2100},
                {'endpoint': '/api/users', 'count': 1500},
                {'endpoint': '/api/materials', 'count': 1200}
            ],
            'response_time_distribution': {
                '0-100ms': 8500,
                '100-500ms': 3500,
                '500-1000ms': 400,
                '1000ms+': 180
            }
        }
        
        return jsonify({
            'success': True,
            'data': api_stats
        })
    except Exception as e:
        logger.error(f"获取API统计错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== 日志监控 ====================
@monitoring_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_logs():
    """获取系统日志"""
    try:
        log_type = request.args.get('type', 'app')  # app, error, access
        level = request.args.get('level')  # DEBUG, INFO, WARNING, ERROR
        limit = request.args.get('limit', 100, type=int)
        
        # 模拟日志数据
        logs = [
            {
                'timestamp': (datetime.now() - timedelta(minutes=i)).isoformat(),
                'level': 'INFO' if i % 5 != 0 else 'WARNING',
                'message': f'示例日志消息 {i}',
                'source': 'app'
            }
            for i in range(limit)
        ]
        
        if level:
            logs = [l for l in logs if l['level'] == level.upper()]
        
        return jsonify({
            'success': True,
            'data': {
                'logs': logs,
                'total': len(logs)
            }
        })
    except Exception as e:
        logger.error(f"获取日志错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== 告警管理 ====================
@monitoring_bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_alerts():
    """获取告警列表"""
    try:
        status = request.args.get('status')  # active, resolved, all
        
        # 模拟告警数据
        alert_list = [
            {
                'id': f'alert_{i}',
                'title': f'示例告警 {i}',
                'message': f'这是示例告警消息 {i}',
                'level': 'warning' if i % 3 == 0 else 'critical' if i % 5 == 0 else 'info',
                'status': 'active' if i < 3 else 'resolved',
                'created_at': (datetime.now() - timedelta(hours=i)).isoformat(),
                'resolved_at': (datetime.now() - timedelta(hours=i-1)).isoformat() if i >= 3 else None
            }
            for i in range(10)
        ]
        
        if status:
            alert_list = [a for a in alert_list if a['status'] == status]
        
        return jsonify({
            'success': True,
            'data': {
                'alerts': alert_list,
                'total': len(alert_list),
                'active_count': sum(1 for a in alert_list if a['status'] == 'active')
            }
        })
    except Exception as e:
        logger.error(f"获取告警错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@monitoring_bp.route('/alerts', methods=['POST'])
@jwt_required()
def create_alert():
    """创建告警"""
    try:
        data = request.get_json()
        
        alert = {
            'id': f"alert_{len(alerts) + 1}",
            'title': data['title'],
            'message': data['message'],
            'level': data.get('level', 'info'),
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'created_by': get_jwt_identity()
        }
        
        alerts.append(alert)
        
        # 发送通知
        send_alert_notification(alert)
        
        return jsonify({
            'success': True,
            'message': '告警创建成功',
            'data': {'alert_id': alert['id']}
        })
    except Exception as e:
        logger.error(f"创建告警错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@monitoring_bp.route('/alerts/<alert_id>/resolve', methods=['POST'])
@jwt_required()
def resolve_alert(alert_id):
    """解决告警"""
    try:
        for alert in alerts:
            if alert['id'] == alert_id:
                alert['status'] = 'resolved'
                alert['resolved_at'] = datetime.now().isoformat()
                alert['resolved_by'] = get_jwt_identity()
                
                return jsonify({
                    'success': True,
                    'message': '告警已解决'
                })
        
        return jsonify({'success': False, 'error': '告警不存在'}), 404
    except Exception as e:
        logger.error(f"解决告警错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def send_alert_notification(alert):
    """发送告警通知"""
    logger.warning(f"告警: {alert['title']} - {alert['message']}")

# ==================== 告警规则 ====================
@monitoring_bp.route('/alert-rules', methods=['GET'])
@jwt_required()
def get_alert_rules():
    """获取告警规则"""
    try:
        rules = [
            {
                'id': 'rule_1',
                'name': 'CPU使用率过高',
                'condition': 'cpu_percent > 80',
                'level': 'warning',
                'enabled': True
            },
            {
                'id': 'rule_2',
                'name': '内存使用率过高',
                'condition': 'memory_percent > 85',
                'level': 'critical',
                'enabled': True
            },
            {
                'id': 'rule_3',
                'name': '磁盘空间不足',
                'condition': 'disk_percent > 90',
                'level': 'critical',
                'enabled': True
            },
            {
                'id': 'rule_4',
                'name': 'API响应时间过长',
                'condition': 'api_response_time > 1000',
                'level': 'warning',
                'enabled': True
            }
        ]
        
        return jsonify({
            'success': True,
            'data': rules
        })
    except Exception as e:
        logger.error(f"获取告警规则错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== 系统信息 ====================
@monitoring_bp.route('/system-info', methods=['GET'])
@jwt_required()
def get_system_info():
    """获取系统信息"""
    try:
        info = {
            'platform': os.name,
            'python_version': os.sys.version,
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            'hostname': os.uname().nodename if hasattr(os, 'uname') else 'unknown',
            'app': {
                'name': 'TOPO System',
                'version': '1.0.0',
                'start_time': datetime.now().isoformat()  # 实际应记录应用启动时间
            }
        }
        
        return jsonify({
            'success': True,
            'data': info
        })
    except Exception as e:
        logger.error(f"获取系统信息错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== 仪表盘 ====================
@monitoring_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_monitoring_dashboard():
    """获取监控仪表盘数据"""
    try:
        # 汇总所有监控数据
        dashboard = {
            'health': health_check().get_json()['data'],
            'performance': get_performance_metrics().get_json()['data'],
            'database': get_database_stats().get_json()['data'],
            'alerts': {
                'active': sum(1 for a in alerts if a.get('status') == 'active'),
                'total': len(alerts)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': dashboard
        })
    except Exception as e:
        logger.error(f"获取仪表盘错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
