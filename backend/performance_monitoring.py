import time
import psutil
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from functools import wraps
import os
import sys
import json
from collections import defaultdict, deque
import gc
import tracemalloc

class PerformanceMonitor:
    """性能监控器，提供系统性能和应用性能监控"""
    
    def __init__(self, log_manager=None, config: Dict = None):
        """初始化性能监控器"""
        self.log_manager = log_manager
        self.config = config or self.get_default_config()
        self.monitoring_thread = None
        self.running = False
        self.lock = threading.Lock()
        
        # 性能数据存储
        self.metrics_history = {
            'cpu': deque(maxlen=1000),
            'memory': deque(maxlen=1000),
            'disk': deque(maxlen=1000),
            'network': deque(maxlen=1000),
            'response_times': deque(maxlen=1000),
            'database_queries': deque(maxlen=1000),
            'errors': deque(maxlen=100)
        }
        
        # 当前指标
        self.current_metrics = {}
        
        # 性能告警阈值
        self.alert_thresholds = {
            'cpu_percent': 80,
            'memory_percent': 85,
            'disk_percent': 90,
            'response_time_ms': 5000,
            'error_rate_percent': 5,
            'database_query_time_ms': 1000
        }
        
        # 设置日志记录器
        self.logger = logging.getLogger('performance_monitor')
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        # 启动内存追踪
        if self.config.get('memory_profiling', False):
            tracemalloc.start()
    
    def get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            'system_monitoring': {
                'enabled': True,
                'interval_seconds': 60,  # 每60秒检查一次
                'cpu_monitoring': True,
                'memory_monitoring': True,
                'disk_monitoring': True,
                'network_monitoring': True
            },
            'application_monitoring': {
                'enabled': True,
                'response_time_tracking': True,
                'error_rate_tracking': True,
                'database_query_tracking': True,
                'api_endpoint_tracking': True
            },
            'memory_profiling': {
                'enabled': False,
                'snapshot_interval_seconds': 300,  # 每5分钟生成内存快照
                'top_stats_count': 10  # 显示前10个内存使用统计
            },
            'alerting': {
                'enabled': True,
                'check_interval_seconds': 300,  # 每5分钟检查告警
                'email_alerts': False,
                'webhook_alerts': False,
                'log_alerts': True
            },
            'reporting': {
                'enabled': True,
                'report_interval_hours': 24,  # 每24小时生成报告
                'include_system_stats': True,
                'include_application_stats': True
            }
        }
    
    def start_monitoring(self):
        """启动性能监控"""
        with self.lock:
            if self.running:
                self.logger.warning("性能监控已在运行中")
                return
            
            self.running = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_worker, daemon=True)
            self.monitoring_thread.start()
            self.logger.info("性能监控已启动")
    
    def stop_monitoring(self):
        """停止性能监控"""
        with self.lock:
            if not self.running:
                return
            
            self.running = False
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=5)
            self.logger.info("性能监控已停止")
    
    def _monitoring_worker(self):
        """监控工作线程"""
        while self.running:
            try:
                # 收集系统性能数据
                if self.config['system_monitoring']['enabled']:
                    self.collect_system_metrics()
                
                # 检查告警
                if self.config['alerting']['enabled']:
                    self.check_alerts()
                
                # 生成内存快照（如果启用）
                if self.config['memory_profiling']['enabled']:
                    self.take_memory_snapshot()
                
                # 等待下一次检查
                time.sleep(self.config['system_monitoring']['interval_seconds'])
                
            except Exception as e:
                self.logger.error(f"性能监控异常: {str(e)}")
                time.sleep(60)  # 异常后等待1分钟再试
    
    def collect_system_metrics(self):
        """收集系统性能指标"""
        timestamp = datetime.now()
        
        # CPU使用率
        if self.config['system_monitoring']['cpu_monitoring']:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.metrics_history['cpu'].append({
                'timestamp': timestamp,
                'value': cpu_percent
            })
            self.current_metrics['cpu_percent'] = cpu_percent
        
        # 内存使用率
        if self.config['system_monitoring']['memory_monitoring']:
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            available_gb = memory.available / (1024**3)  # 转换为GB
            total_gb = memory.total / (1024**3)  # 转换为GB
            self.metrics_history['memory'].append({
                'timestamp': timestamp,
                'percent': memory_percent,
                'available_gb': round(available_gb, 2),
                'total_gb': round(total_gb, 2)
            })
            self.current_metrics['memory_percent'] = memory_percent
            self.current_metrics['memory_available_gb'] = round(available_gb, 2)
        
        # 磁盘使用率
        if self.config['system_monitoring']['disk_monitoring']:
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            free_gb = disk.free / (1024**3)  # 转换为GB
            total_gb = disk.total / (1024**3)  # 转换为GB
            self.metrics_history['disk'].append({
                'timestamp': timestamp,
                'percent': disk_percent,
                'free_gb': round(free_gb, 2),
                'total_gb': round(total_gb, 2)
            })
            self.current_metrics['disk_percent'] = disk_percent
            self.current_metrics['disk_free_gb'] = round(free_gb, 2)
        
        # 网络统计
        if self.config['system_monitoring']['network_monitoring']:
            net_io = psutil.net_io_counters()
            bytes_sent_mb = net_io.bytes_sent / (1024**2)  # 转换为MB
            bytes_recv_mb = net_io.bytes_recv / (1024**2)  # 转换为MB
            packets_sent = net_io.packets_sent
            packets_recv = net_io.packets_recv
            self.metrics_history['network'].append({
                'timestamp': timestamp,
                'bytes_sent_mb': round(bytes_sent_mb, 2),
                'bytes_recv_mb': round(bytes_recv_mb, 2),
                'packets_sent': packets_sent,
                'packets_recv': packets_recv
            })
        
        # 记录性能日志
        if self.log_manager:
            try:
                self.log_manager.log_performance(
                    operation="system_metrics_collection",
                    duration=0,  # 可以计算收集时间
                    memory_usage=self.current_metrics.get('memory_percent', 0),
                    cpu_percent=self.current_metrics.get('cpu_percent', 0),
                    disk_percent=self.current_metrics.get('disk_percent', 0)
                )
            except Exception as e:
                self.logger.warning(f"记录性能日志失败: {str(e)}")
    
    def track_response_time(self, endpoint: str, method: str, duration_ms: float):
        """跟踪API响应时间"""
        if not self.config['application_monitoring']['response_time_tracking']:
            return
        
        timestamp = datetime.now()
        
        self.metrics_history['response_times'].append({
            'timestamp': timestamp,
            'endpoint': endpoint,
            'method': method,
            'duration_ms': duration_ms
        })
        
        # 记录性能日志
        if self.log_manager:
            try:
                self.log_manager.log_performance(
                    operation=f"api_response_{method}_{endpoint}",
                    duration=duration_ms,
                    endpoint=endpoint,
                    method=method
                )
            except Exception as e:
                self.logger.warning(f"记录API响应时间日志失败: {str(e)}")
        
        # 检查响应时间告警
        if duration_ms > self.alert_thresholds['response_time_ms']:
            self.logger.warning(f"API响应时间告警: {method} {endpoint} - {duration_ms}ms")
    
    def track_database_query(self, query: str, duration_ms: float, table: str = None):
        """跟踪数据库查询性能"""
        if not self.config['application_monitoring']['database_query_tracking']:
            return
        
        timestamp = datetime.now()
        
        self.metrics_history['database_queries'].append({
            'timestamp': timestamp,
            'query': query[:100] + '...' if len(query) > 100 else query,  # 截断长查询
            'duration_ms': duration_ms,
            'table': table
        })
        
        # 记录性能日志
        if self.log_manager:
            try:
                self.log_manager.log_performance(
                    operation=f"database_query_{table or 'unknown'}",
                    duration=duration_ms,
                    query_type=query.split()[0] if query else 'unknown',
                    table=table
                )
            except Exception as e:
                self.logger.warning(f"记录数据库查询日志失败: {str(e)}")
        
        # 检查查询时间告警
        if duration_ms > self.alert_thresholds['database_query_time_ms']:
            self.logger.warning(f"数据库查询时间告警: {table} - {duration_ms}ms - Query: {query[:50]}...")
    
    def track_error(self, error_type: str, error_message: str, endpoint: str = None):
        """跟踪错误"""
        if not self.config['application_monitoring']['error_rate_tracking']:
            return
        
        timestamp = datetime.now()
        
        self.metrics_history['errors'].append({
            'timestamp': timestamp,
            'error_type': error_type,
            'error_message': error_message,
            'endpoint': endpoint
        })
        
        # 记录错误日志
        if self.log_manager:
            self.log_manager.log_error(
                message=f"应用错误: {error_type} - {error_message}",
                details={'endpoint': endpoint}
            )
    
    def take_memory_snapshot(self):
        """生成内存快照"""
        if not tracemalloc.is_tracing():
            return
        
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')[:self.config['memory_profiling']['top_stats_count']]
        
        timestamp = datetime.now()
        
        memory_stats = []
        for stat in top_stats:
            traceback_lines = stat.traceback.format()
            if traceback_lines:
                last_line = traceback_lines[-1]
                # 解析文件名和行号
                if ':' in last_line:
                    filename_part, line_part = last_line.rsplit(':', 1)
                    line = line_part.strip()
                else:
                    filename_part = last_line
                    line = 'unknown'
                
                memory_stats.append({
                    'filename': filename_part.strip(),
                    'line': line,
                    'size_mb': round(stat.size / (1024**2), 2),
                    'count': stat.count
                })
        
        # 记录内存使用情况
        if self.log_manager:
            try:
                self.log_manager.log_performance(
                    operation="memory_snapshot",
                    duration=0,
                    memory_stats=memory_stats,
                    total_memory_mb=round(sum(stat['size_mb'] for stat in memory_stats), 2)
                )
            except Exception as e:
                self.logger.warning(f"记录内存快照日志失败: {str(e)}")
    
    def check_alerts(self):
        """检查性能告警"""
        # 检查CPU使用率
        cpu_percent = self.current_metrics.get('cpu_percent', 0)
        if cpu_percent > self.alert_thresholds['cpu_percent']:
            self.send_alert(f"CPU使用率告警: {cpu_percent}% (阈值: {self.alert_thresholds['cpu_percent']}%)")
        
        # 检查内存使用率
        memory_percent = self.current_metrics.get('memory_percent', 0)
        if memory_percent > self.alert_thresholds['memory_percent']:
            self.send_alert(f"内存使用率告警: {memory_percent}% (阈值: {self.alert_thresholds['memory_percent']}%)")
        
        # 检查磁盘使用率
        disk_percent = self.current_metrics.get('disk_percent', 0)
        if disk_percent > self.alert_thresholds['disk_percent']:
            self.send_alert(f"磁盘使用率告警: {disk_percent}% (阈值: {self.alert_thresholds['disk_percent']}%)")
        
        # 检查错误率（基于最近100个错误）
        recent_errors = list(self.metrics_history['errors'])[-100:]
        if len(recent_errors) > 0:
            error_rate = len(recent_errors) / 100 * 100
            if error_rate > self.alert_thresholds['error_rate_percent']:
                self.send_alert(f"应用错误率告警: {error_rate:.1f}% (阈值: {self.alert_thresholds['error_rate_percent']}%)")
    
    def send_alert(self, message: str):
        """发送性能告警"""
        self.logger.warning(f"PERFORMANCE ALERT: {message}")
        
        # 记录告警日志
        if self.log_manager:
            try:
                self.log_manager.log_performance(
                    operation="performance_alert",
                    duration=0,
                    alert_message=message
                )
            except Exception as e:
                self.logger.warning(f"记录性能告警日志失败: {str(e)}")
        
        # 这里可以添加邮件、短信、Webhook等通知方式
        # 示例：写入告警日志文件
        alert_log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'performance_alerts.log')
        os.makedirs(os.path.dirname(alert_log_path), exist_ok=True)
        
        with open(alert_log_path, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat()} - {message}\n")
    
    def get_current_metrics(self) -> Dict:
        """获取当前性能指标"""
        return self.current_metrics.copy()
    
    def get_metrics_history(self, metric_type: str = None, hours: int = 24) -> List[Dict]:
        """获取性能历史数据"""
        if metric_type and metric_type in self.metrics_history:
            # 过滤指定时间范围的数据
            cutoff_time = datetime.now() - timedelta(hours=hours)
            return [
                item for item in self.metrics_history[metric_type]
                if item['timestamp'] >= cutoff_time
            ]
        else:
            # 返回所有指标的历史数据
            return {
                metric_type: self.get_metrics_history(metric_type, hours)
                for metric_type in self.metrics_history.keys()
            }
    
    def generate_performance_report(self, hours: int = 24) -> Dict:
        """生成性能报告"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'time_range_hours': hours,
            'system_metrics': {},
            'application_metrics': {},
            'alerts': [],
            'recommendations': []
        }
        
        # 系统性能统计
        if self.config['reporting']['include_system_stats']:
            cpu_history = self.get_metrics_history('cpu', hours)
            if cpu_history:
                cpu_values = [item['value'] for item in cpu_history]
                report['system_metrics']['cpu'] = {
                    'avg_percent': sum(cpu_values) / len(cpu_values),
                    'max_percent': max(cpu_values),
                    'min_percent': min(cpu_values)
                }
            
            memory_history = self.get_metrics_history('memory', hours)
            if memory_history:
                memory_percent = [item['percent'] for item in memory_history]
                report['system_metrics']['memory'] = {
                    'avg_percent': sum(memory_percent) / len(memory_percent),
                    'max_percent': max(memory_percent),
                    'min_percent': min(memory_percent)
                }
        
        # 应用性能统计
        if self.config['reporting']['include_application_stats']:
            response_history = self.get_metrics_history('response_times', hours)
            if response_history:
                response_times = [item['duration_ms'] for item in response_history]
                report['application_metrics']['response_time'] = {
                    'avg_ms': sum(response_times) / len(response_times),
                    'max_ms': max(response_times),
                    'min_ms': min(response_times)
                }
            
            error_history = self.get_metrics_history('errors', hours)
            if error_history:
                report['application_metrics']['errors'] = {
                    'total_count': len(error_history),
                    'error_types': defaultdict(int)
                }
                for error in error_history:
                    report['application_metrics']['errors']['error_types'][error['error_type']] += 1
        
        # 生成建议
        self._generate_recommendations(report)
        
        return report
    
    def _generate_recommendations(self, report: Dict):
        """生成性能优化建议"""
        recommendations = []
        
        # CPU使用建议
        if 'cpu' in report.get('system_metrics', {}):
            cpu_avg = report['system_metrics']['cpu']['avg_percent']
            if cpu_avg > 80:
                recommendations.append({
                    'type': 'cpu',
                    'severity': 'high',
                    'message': f'CPU平均使用率过高 ({cpu_avg:.1f}%)，建议优化代码或增加服务器资源'
                })
            elif cpu_avg > 60:
                recommendations.append({
                    'type': 'cpu',
                    'severity': 'medium',
                    'message': f'CPU平均使用率较高 ({cpu_avg:.1f}%)，建议监控和优化'
                })
        
        # 内存使用建议
        if 'memory' in report.get('system_metrics', {}):
            memory_avg = report['system_metrics']['memory']['avg_percent']
            if memory_avg > 85:
                recommendations.append({
                    'type': 'memory',
                    'severity': 'high',
                    'message': f'内存平均使用率过高 ({memory_avg:.1f}%)，建议检查内存泄漏或增加内存'
                })
        
        # 响应时间建议
        if 'response_time' in report.get('application_metrics', {}):
            response_avg = report['application_metrics']['response_time']['avg_ms']
            if response_avg > 3000:
                recommendations.append({
                    'type': 'response_time',
                    'severity': 'high',
                    'message': f'API平均响应时间过长 ({response_avg:.0f}ms)，建议优化数据库查询或增加缓存'
                })
            elif response_avg > 1000:
                recommendations.append({
                    'type': 'response_time',
                    'severity': 'medium',
                    'message': f'API平均响应时间较长 ({response_avg:.0f}ms)，建议优化'
                })
        
        report['recommendations'] = recommendations
    
    def cleanup_metrics_history(self, days: int = 7):
        """清理旧的性能数据"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        for metric_type in self.metrics_history:
            # 保留最近的数据
            while (self.metrics_history[metric_type] and 
                   self.metrics_history[metric_type][0]['timestamp'] < cutoff_time):
                self.metrics_history[metric_type].popleft()
        
        self.logger.info(f"已清理 {days} 天前的性能数据")
    
    def export_config(self) -> Dict:
        """导出配置"""
        return {
            'config': self.config,
            'alert_thresholds': self.alert_thresholds,
            'service_status': {
                'running': self.running,
                'thread_alive': self.monitoring_thread.is_alive() if self.monitoring_thread else False
            }
        }
    
    def import_config(self, config: Dict):
        """导入配置"""
        if 'config' in config:
            self.config.update(config['config'])
        
        if 'alert_thresholds' in config:
            self.alert_thresholds.update(config['alert_thresholds'])
        
        self.logger.info("性能监控配置已更新")

# 性能监控装饰器
def performance_monitor(operation_name: str = None):
    """性能监控装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            memory_before = psutil.Process().memory_info().rss / (1024**2)  # MB
            
            try:
                result = func(*args, **kwargs)
                
                # 计算性能指标
                duration_ms = (time.time() - start_time) * 1000
                memory_after = psutil.Process().memory_info().rss / (1024**2)
                memory_used_mb = memory_after - memory_before
                
                # 获取操作名称
                op_name = operation_name or f"{func.__module__}.{func.__name__}"
                
                # 记录性能日志 - 使用全局实例
                pm = performance_monitor
                if pm and pm.log_manager:
                    pm.log_manager.log_performance(
                        operation=op_name,
                        duration=duration_ms,
                        memory_usage=memory_used_mb
                    )
                
                # 跟踪响应时间（如果是API函数）
                if 'api' in func.__module__ or 'route' in func.__name__:
                    if pm:
                        pm.track_response_time(
                            endpoint=func.__name__,
                            method='FUNCTION',
                            duration_ms=duration_ms
                        )
                
                return result
                
            except Exception as e:
                # 记录错误 - 使用全局实例
                pm = performance_monitor
                if pm:
                    pm.track_error(
                        error_type=type(e).__name__,
                        error_message=str(e),
                        endpoint=func.__name__ if 'api' in func.__module__ else None
                    )
                raise
        
        return wrapper
    return decorator

# 全局性能监控器实例
performance_monitor = PerformanceMonitor()

def init_performance_monitoring(log_manager=None, app=None):
    """初始化性能监控系统"""
    global performance_monitor
    
    if app and hasattr(app, 'config'):
        # 从应用配置中获取性能监控配置
        perf_config = app.config.get('PERFORMANCE_MONITORING_CONFIG', {})
        if perf_config:
            performance_monitor.import_config({'config': perf_config})
    
    # 设置日志管理器
    if log_manager:
        performance_monitor.log_manager = log_manager
    
    # 启动性能监控
    performance_monitor.start_monitoring()
    
    return performance_monitor

def get_performance_monitor():
    """获取性能监控器实例"""
    return performance_monitor