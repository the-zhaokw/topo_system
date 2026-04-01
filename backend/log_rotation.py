import os
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
import gzip
import json
from typing import Dict, List, Optional
import threading
import time

class LogRotationManager:
    """日志轮转和归档管理器"""
    
    def __init__(self, log_base_dir: str = None, config: Dict = None):
        """初始化日志轮转管理器"""
        self.log_base_dir = log_base_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        self.config = config or self.get_default_config()
        self.rotation_thread = None
        self.running = False
        self.lock = threading.Lock()
        
        # 确保日志目录存在
        os.makedirs(self.log_base_dir, exist_ok=True)
        
        # 设置日志记录器
        self.logger = logging.getLogger('log_rotation')
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            'rotation': {
                'enabled': True,
                'interval_hours': 24,  # 每24小时轮转一次
                'max_file_size_mb': 100,  # 最大文件大小100MB
                'backup_count': 7,  # 保留7个备份文件
            },
            'archival': {
                'enabled': True,
                'archive_after_days': 7,  # 7天后归档
                'compress': True,  # 压缩归档文件
                'archive_dir': 'archives',  # 归档目录
            },
            'cleanup': {
                'enabled': True,
                'delete_after_days': 30,  # 30天后删除
                'cleanup_interval_hours': 24,  # 每24小时清理一次
            },
            'monitoring': {
                'enabled': True,
                'check_interval_hours': 1,  # 每小时检查一次
                'alert_threshold_mb': 500,  # 磁盘使用超过500MB时告警
            }
        }
    
    def start_rotation_service(self):
        """启动日志轮转服务"""
        with self.lock:
            if self.running:
                self.logger.warning("日志轮转服务已在运行中")
                return
            
            self.running = True
            self.rotation_thread = threading.Thread(target=self._rotation_worker, daemon=True)
            self.rotation_thread.start()
            self.logger.info("日志轮转服务已启动")
    
    def stop_rotation_service(self):
        """停止日志轮转服务"""
        with self.lock:
            if not self.running:
                return
            
            self.running = False
            if self.rotation_thread and self.rotation_thread.is_alive():
                self.rotation_thread.join(timeout=5)
            self.logger.info("日志轮转服务已停止")
    
    def _rotation_worker(self):
        """日志轮转工作线程"""
        while self.running:
            try:
                self.perform_rotation_check()
                self.perform_cleanup_check()
                self.perform_monitoring_check()
                
                # 等待下一次检查
                monitoring_config = self.config.get_monitoring_config()
                time.sleep(monitoring_config.get('check_interval_hours', 1) * 3600)
                
            except Exception as e:
                self.logger.error(f"日志轮转服务异常: {str(e)}")
                time.sleep(60)  # 异常后等待1分钟再试
    
    def perform_rotation_check(self):
        """执行日志轮转检查"""
        rotation_config = self.config.get_rotation_config()
        if not rotation_config.get('enabled', True):
            return
        
        self.logger.info("开始执行日志轮转检查")
        
        # 获取所有日志文件
        log_files = self.get_all_log_files()
        
        for log_file in log_files:
            try:
                self.check_and_rotate_log(log_file)
            except Exception as e:
                self.logger.error(f"轮转日志文件失败 {log_file}: {str(e)}")
    
    def get_all_log_files(self) -> List[str]:
        """获取所有日志文件路径"""
        log_files = []
        
        # 遍历日志目录及其子目录
        for root, dirs, files in os.walk(self.log_base_dir):
            for file in files:
                if file.endswith('.log'):
                    log_files.append(os.path.join(root, file))
        
        return log_files
    
    def check_and_rotate_log(self, log_file_path: str):
        """检查并轮转单个日志文件"""
        rotation_config = self.config.get_rotation_config()
        file_size_mb = os.path.getsize(log_file_path) / (1024 * 1024)
        max_size_mb = rotation_config.get('max_file_size_mb', 100)
        
        # 检查文件大小是否需要轮转
        if file_size_mb >= max_size_mb:
            self.rotate_log_file(log_file_path)
            return
        
        # 检查时间是否需要轮转（基于文件修改时间）
        file_mtime = datetime.fromtimestamp(os.path.getmtime(log_file_path))
        rotation_interval = timedelta(hours=rotation_config.get('interval_hours', 24))
        
        if datetime.now() - file_mtime >= rotation_interval:
            self.rotate_log_file(log_file_path)
    
    def rotate_log_file(self, log_file_path: str):
        """轮转单个日志文件"""
        self.logger.info(f"轮转日志文件: {log_file_path}")
        
        # 获取文件基本信息
        log_dir = os.path.dirname(log_file_path)
        base_name = os.path.basename(log_file_path)
        name_without_ext = os.path.splitext(base_name)[0]
        
        # 生成轮转文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        rotated_filename = f"{name_without_ext}_{timestamp}.log"
        rotated_path = os.path.join(log_dir, rotated_filename)
        
        try:
            # 复制当前日志文件到轮转文件
            shutil.copy2(log_file_path, rotated_path)
            
            # 清空原日志文件
            with open(log_file_path, 'w', encoding='utf-8') as f:
                f.write(f"# 日志文件已轮转 - {datetime.now().isoformat()}\n")
            
            self.logger.info(f"日志文件轮转完成: {rotated_path}")
            
            # 压缩轮转文件（如果启用）
            archival_config = self.config.get_archiving_config()
            if archival_config.get('compress', True):
                self.compress_log_file(rotated_path)
            
            # 清理旧轮转文件
            self.cleanup_rotated_files(log_dir, name_without_ext)
            
        except Exception as e:
            self.logger.error(f"轮转日志文件失败: {str(e)}")
            raise
    
    def compress_log_file(self, log_file_path: str):
        """压缩日志文件"""
        try:
            with open(log_file_path, 'rb') as f_in:
                with gzip.open(log_file_path + '.gz', 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # 删除原文件
            os.remove(log_file_path)
            self.logger.info(f"日志文件压缩完成: {log_file_path}.gz")
            
        except Exception as e:
            self.logger.error(f"压缩日志文件失败: {str(e)}")
    
    def cleanup_rotated_files(self, log_dir: str, base_name: str):
        """清理旧的轮转文件"""
        rotation_config = self.config.get_rotation_config()
        backup_count = rotation_config.get('backup_count', 7)
        
        # 获取所有轮转文件
        rotated_files = []
        for file in os.listdir(log_dir):
            if file.startswith(base_name + '_') and (file.endswith('.log') or file.endswith('.log.gz')):
                file_path = os.path.join(log_dir, file)
                rotated_files.append((file_path, os.path.getmtime(file_path)))
        
        # 按修改时间排序
        rotated_files.sort(key=lambda x: x[1], reverse=True)
        
        # 删除超过保留数量的旧文件
        for file_path, _ in rotated_files[backup_count:]:
            try:
                os.remove(file_path)
                self.logger.info(f"删除旧轮转文件: {file_path}")
            except Exception as e:
                self.logger.error(f"删除旧轮转文件失败 {file_path}: {str(e)}")
    
    def perform_cleanup_check(self):
        """执行清理检查"""
        cleanup_config = self.config.get_cleanup_config()
        if not cleanup_config.get('enabled', True):
            return
        
        self.logger.info("开始执行日志清理检查")
        
        # 获取所有日志文件（包括归档的）
        all_log_files = self.get_all_log_files()
        archival_config = self.config.get_archiving_config()
        archive_after_days = archival_config.get('archive_after_days', 7)
        delete_after_days = cleanup_config.get('delete_after_days', 30)
        
        current_time = datetime.now()
        
        for log_file in all_log_files:
            try:
                file_mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
                file_age_days = (current_time - file_mtime).days
                
                # 归档旧日志文件
                if file_age_days >= archive_after_days and not self.is_archived_file(log_file):
                    self.archive_log_file(log_file)
                
                # 删除非常旧的日志文件
                if file_age_days >= delete_after_days:
                    self.delete_old_log_file(log_file)
                    
            except Exception as e:
                self.logger.error(f"处理日志文件失败 {log_file}: {str(e)}")
    
    def is_archived_file(self, file_path: str) -> bool:
        """检查文件是否已归档"""
        archival_config = self.config.get_archiving_config()
        archive_dir = archival_config.get('archive_dir', 'archives')
        return archive_dir in file_path
    
    def archive_log_file(self, log_file_path: str):
        """归档日志文件"""
        self.logger.info(f"归档日志文件: {log_file_path}")
        
        # 创建归档目录
        archival_config = self.config.get_archiving_config()
        archive_dir = os.path.join(self.log_base_dir, archival_config.get('archive_dir', 'archives'))
        os.makedirs(archive_dir, exist_ok=True)
        
        # 生成归档文件名
        base_name = os.path.basename(log_file_path)
        archive_path = os.path.join(archive_dir, base_name)
        
        try:
            # 移动文件到归档目录
            shutil.move(log_file_path, archive_path)
            
            # 压缩归档文件（如果启用）
            archival_config = self.config.get_archiving_config()
            if archival_config.get('compress', True) and not archive_path.endswith('.gz'):
                self.compress_log_file(archive_path)
            
            self.logger.info(f"日志文件归档完成: {archive_path}")
            
        except Exception as e:
            self.logger.error(f"归档日志文件失败: {str(e)}")
    
    def delete_old_log_file(self, log_file_path: str):
        """删除旧的日志文件"""
        try:
            os.remove(log_file_path)
            self.logger.info(f"删除旧日志文件: {log_file_path}")
        except Exception as e:
            self.logger.error(f"删除旧日志文件失败 {log_file_path}: {str(e)}")
    
    def perform_monitoring_check(self):
        """执行监控检查"""
        if not self.config['monitoring']['enabled']:
            return
        
        try:
            total_size_mb = self.get_total_log_size() / (1024 * 1024)
            threshold_mb = self.config['monitoring']['alert_threshold_mb']
            
            if total_size_mb >= threshold_mb:
                self.logger.warning(f"日志磁盘使用告警: {total_size_mb:.2f}MB (阈值: {threshold_mb}MB)")
                
                # 这里可以添加邮件、短信等告警通知
                self.send_alert(f"日志磁盘使用超过阈值: {total_size_mb:.2f}MB")
                
        except Exception as e:
            self.logger.error(f"监控检查失败: {str(e)}")
    
    def get_total_log_size(self) -> int:
        """获取所有日志文件的总大小（字节）"""
        total_size = 0
        
        for root, dirs, files in os.walk(self.log_base_dir):
            for file in files:
                if file.endswith('.log') or file.endswith('.gz'):
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                    except OSError:
                        pass
        
        return total_size
    
    def send_alert(self, message: str):
        """发送告警通知"""
        # 这里可以实现邮件、短信、钉钉等通知方式
        self.logger.warning(f"ALERT: {message}")
        
        # 示例：写入告警日志文件
        alert_log_path = os.path.join(self.log_base_dir, 'alerts.log')
        with open(alert_log_path, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat()} - {message}\n")
    
    def get_log_statistics(self) -> Dict:
        """获取日志统计信息"""
        stats = {
            'total_size_mb': self.get_total_log_size() / (1024 * 1024),
            'log_files_count': 0,
            'archived_files_count': 0,
            'compressed_files_count': 0,
            'oldest_file_date': None,
            'newest_file_date': None,
            'log_categories': {}
        }
        
        oldest_date = None
        newest_date = None
        
        for root, dirs, files in os.walk(self.log_base_dir):
            for file in files:
                if file.endswith('.log') or file.endswith('.gz'):
                    file_path = os.path.join(root, file)
                    try:
                        file_stat = os.stat(file_path)
                        file_size_mb = file_stat.st_size / (1024 * 1024)
                        file_mtime = datetime.fromtimestamp(file_stat.st_mtime)
                        
                        stats['log_files_count'] += 1
                        
                        if file.endswith('.gz'):
                            stats['compressed_files_count'] += 1
                        
                        if self.is_archived_file(file_path):
                            stats['archived_files_count'] += 1
                        
                        # 更新最旧和最新文件日期
                        if oldest_date is None or file_mtime < oldest_date:
                            oldest_date = file_mtime
                        
                        if newest_date is None or file_mtime > newest_date:
                            newest_date = file_mtime
                        
                        # 按类别统计
                        category = os.path.basename(os.path.dirname(file_path))
                        if category not in stats['log_categories']:
                            stats['log_categories'][category] = {
                                'count': 0,
                                'size_mb': 0
                            }
                        
                        stats['log_categories'][category]['count'] += 1
                        stats['log_categories'][category]['size_mb'] += file_size_mb
                        
                    except OSError:
                        pass
        
        stats['oldest_file_date'] = oldest_date.isoformat() if oldest_date else None
        stats['newest_file_date'] = newest_date.isoformat() if newest_date else None
        
        return stats
    
    def cleanup_all_logs(self):
        """清理所有日志文件（谨慎使用）"""
        self.logger.warning("开始清理所有日志文件")
        
        for root, dirs, files in os.walk(self.log_base_dir):
            for file in files:
                if file.endswith('.log') or file.endswith('.gz'):
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        self.logger.info(f"删除日志文件: {file_path}")
                    except Exception as e:
                        self.logger.error(f"删除日志文件失败 {file_path}: {str(e)}")
        
        self.logger.info("日志清理完成")
    
    def export_log_config(self) -> Dict:
        """导出当前配置"""
        return {
            'config': self.config,
            'log_base_dir': self.log_base_dir,
            'service_status': {
                'running': self.running,
                'thread_alive': self.rotation_thread.is_alive() if self.rotation_thread else False
            }
        }
    
    def import_log_config(self, config: Dict):
        """导入配置"""
        if 'config' in config:
            self.config.update(config['config'])
            self.logger.info("日志轮转配置已更新")

# 全局日志轮转管理器实例
log_rotation_manager = LogRotationManager()

def init_log_rotation(app=None):
    """初始化日志轮转系统"""
    if app and hasattr(app, 'config'):
        # 从应用配置中获取日志轮转配置
        rotation_config = app.config.get('LOG_ROTATION_CONFIG', {})
        if rotation_config:
            log_rotation_manager.import_log_config({'config': rotation_config})
    
    # 启动日志轮转服务
    log_rotation_manager.start_rotation_service()
    
    return log_rotation_manager

def get_log_rotation_manager():
    """获取日志轮转管理器实例"""
    return log_rotation_manager