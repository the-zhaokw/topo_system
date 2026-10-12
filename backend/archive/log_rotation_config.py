import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class LogRotationConfig:
    """日志轮转配置管理器"""
    
    def __init__(self, config_file: str = "log_rotation_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """加载配置文件"""
        default_config = {
            "rotation": {
                "max_size_mb": 100,
                "backup_count": 7,
                "rotation_interval_hours": 24,
                "rotation_time": "00:00"
            },
            "archiving": {
                "archive_after_days": 7,
                "compress_archives": True,
                "archive_format": "zip",
                "archive_location": "logs/archives"
            },
            "cleanup": {
                "retention_days": 30,
                "cleanup_interval_hours": 24,
                "cleanup_enabled": True
            },
            "monitoring": {
                "disk_usage_threshold": 85,
                "check_interval_minutes": 30,
                "alert_enabled": True,
                "alert_recipients": []
            },
            "logs": {
                "log_types": ["app", "error", "audit", "performance", "business", "database"],
                "log_levels": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                "log_directory": "logs",
                "log_file_patterns": {
                    "app": "app.log",
                    "error": "error.log",
                    "audit": "audit.log",
                    "performance": "performance.log",
                    "business": "business.log",
                    "database": "database.log"
                }
            },
            "performance": {
                "slow_query_threshold_seconds": 1.0,
                "slow_request_threshold_seconds": 5.0,
                "memory_threshold_mb": 500,
                "cpu_threshold_percent": 80
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 合并默认配置
                    return self.merge_config(default_config, loaded_config)
            else:
                # 创建默认配置文件
                self.save_config(default_config)
                return default_config
        except Exception as e:
            logging.error(f"Error loading log rotation config: {e}")
            return default_config
    
    def merge_config(self, default: Dict, loaded: Dict) -> Dict:
        """合并配置，确保所有必需的键都存在"""
        for key, value in default.items():
            if key not in loaded:
                loaded[key] = value
            elif isinstance(value, dict) and isinstance(loaded[key], dict):
                loaded[key] = self.merge_config(value, loaded[key])
        return loaded
    
    def save_config(self, config: Optional[Dict] = None) -> bool:
        """保存配置到文件"""
        try:
            config_to_save = config or self.config
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logging.error(f"Error saving log rotation config: {e}")
            return False
    
    def get_rotation_config(self) -> Dict:
        """获取轮转配置"""
        return self.config.get("rotation", {})
    
    def get_archiving_config(self) -> Dict:
        """获取归档配置"""
        return self.config.get("archiving", {})
    
    def get_cleanup_config(self) -> Dict:
        """获取清理配置"""
        return self.config.get("cleanup", {})
    
    def get_monitoring_config(self) -> Dict:
        """获取监控配置"""
        return self.config.get("monitoring", {})
    
    def get_logs_config(self) -> Dict:
        """获取日志配置"""
        return self.config.get("logs", {})
    
    def get_performance_config(self) -> Dict:
        """获取性能配置"""
        return self.config.get("performance", {})
    
    def update_rotation_config(self, **kwargs) -> bool:
        """更新轮转配置"""
        try:
            rotation_config = self.get_rotation_config()
            rotation_config.update(kwargs)
            self.config["rotation"] = rotation_config
            return self.save_config()
        except Exception as e:
            logging.error(f"Error updating rotation config: {e}")
            return False
    
    def update_archiving_config(self, **kwargs) -> bool:
        """更新归档配置"""
        try:
            archiving_config = self.get_archiving_config()
            archiving_config.update(kwargs)
            self.config["archiving"] = archiving_config
            return self.save_config()
        except Exception as e:
            logging.error(f"Error updating archiving config: {e}")
            return False
    
    def update_cleanup_config(self, **kwargs) -> bool:
        """更新清理配置"""
        try:
            cleanup_config = self.get_cleanup_config()
            cleanup_config.update(kwargs)
            self.config["cleanup"] = cleanup_config
            return self.save_config()
        except Exception as e:
            logging.error(f"Error updating cleanup config: {e}")
            return False
    
    def update_monitoring_config(self, **kwargs) -> bool:
        """更新监控配置"""
        try:
            monitoring_config = self.get_monitoring_config()
            monitoring_config.update(kwargs)
            self.config["monitoring"] = monitoring_config
            return self.save_config()
        except Exception as e:
            logging.error(f"Error updating monitoring config: {e}")
            return False
    
    def get_log_file_path(self, log_type: str) -> str:
        """获取日志文件路径"""
        logs_config = self.get_logs_config()
        log_directory = logs_config.get("log_directory", "logs")
        log_patterns = logs_config.get("log_file_patterns", {})
        filename = log_patterns.get(log_type, f"{log_type}.log")
        return os.path.join(log_directory, filename)
    
    def get_all_log_files(self) -> List[str]:
        """获取所有日志文件路径"""
        logs_config = self.get_logs_config()
        log_types = logs_config.get("log_types", [])
        return [self.get_log_file_path(log_type) for log_type in log_types]
    
    def validate_config(self) -> Dict[str, bool]:
        """验证配置有效性"""
        validation_results = {}
        
        # 验证轮转配置
        rotation_config = self.get_rotation_config()
        validation_results["rotation"] = (
            isinstance(rotation_config.get("max_size_mb"), (int, float)) and
            rotation_config.get("max_size_mb") > 0 and
            isinstance(rotation_config.get("backup_count"), int) and
            rotation_config.get("backup_count") > 0
        )
        
        # 验证归档配置
        archiving_config = self.get_archiving_config()
        validation_results["archiving"] = (
            isinstance(archiving_config.get("archive_after_days"), int) and
            archiving_config.get("archive_after_days") > 0
        )
        
        # 验证清理配置
        cleanup_config = self.get_cleanup_config()
        validation_results["cleanup"] = (
            isinstance(cleanup_config.get("retention_days"), int) and
            cleanup_config.get("retention_days") > 0
        )
        
        # 验证监控配置
        monitoring_config = self.get_monitoring_config()
        validation_results["monitoring"] = (
            isinstance(monitoring_config.get("disk_usage_threshold"), (int, float)) and
            0 < monitoring_config.get("disk_usage_threshold") <= 100
        )
        
        # 验证性能配置
        performance_config = self.get_performance_config()
        validation_results["performance"] = (
            isinstance(performance_config.get("slow_query_threshold_seconds"), (int, float)) and
            performance_config.get("slow_query_threshold_seconds") > 0 and
            isinstance(performance_config.get("slow_request_threshold_seconds"), (int, float)) and
            performance_config.get("slow_request_threshold_seconds") > 0
        )
        
        return validation_results
    
    def get_config_summary(self) -> Dict:
        """获取配置摘要"""
        return {
            "rotation": self.get_rotation_config(),
            "archiving": self.get_archiving_config(),
            "cleanup": self.get_cleanup_config(),
            "monitoring": self.get_monitoring_config(),
            "performance": self.get_performance_config(),
            "validation": self.validate_config()
        }

# 全局配置实例
log_rotation_config = LogRotationConfig()

def get_log_rotation_config() -> LogRotationConfig:
    """获取日志轮转配置实例"""
    return log_rotation_config

def update_log_rotation_config(config_updates: Dict) -> bool:
    """更新日志轮转配置"""
    try:
        config = get_log_rotation_config()
        
        if "rotation" in config_updates:
            config.update_rotation_config(**config_updates["rotation"])
        
        if "archiving" in config_updates:
            config.update_archiving_config(**config_updates["archiving"])
        
        if "cleanup" in config_updates:
            config.update_cleanup_config(**config_updates["cleanup"])
        
        if "monitoring" in config_updates:
            config.update_monitoring_config(**config_updates["monitoring"])
        
        return True
    except Exception as e:
        logging.error(f"Error updating log rotation config: {e}")
        return False