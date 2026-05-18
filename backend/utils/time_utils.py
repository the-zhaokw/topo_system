"""
时间处理工具模块
提供时区相关的工具函数
"""
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

# 中国时区
CHINA_TZ = ZoneInfo('Asia/Shanghai')


def now_china():
    """
    获取中国时区(UTC+8)的当前时间
    
    Returns:
        datetime: 中国时区的当前时间
    """
    return datetime.now(CHINA_TZ)


def utcnow():
    """
    获取中国时区当前时间（兼容原有 utcnow 用法）
    
    Returns:
        datetime: 中国时区的当前时间
    """
    return datetime.now(CHINA_TZ)


def sync_time_to_china():
    """
    同步时间到中国时区 (UTC+8)
    记录当前时间到日志
    """
    try:
        current_time = now_china()
        logging.info(f"时间已同步到中国时区 (UTC+8)，当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        logging.warning(f"时间同步设置失败: {e}")


def format_datetime(dt, fmt='%Y-%m-%d %H:%M:%S'):
    """
    格式化日期时间
    
    Args:
        dt: datetime对象
        fmt: 格式化字符串
        
    Returns:
        str: 格式化后的时间字符串
    """
    if dt is None:
        return None
    return dt.strftime(fmt)


def parse_datetime(date_string, fmt='%Y-%m-%d %H:%M:%S'):
    """
    解析日期时间字符串
    
    Args:
        date_string: 时间字符串
        fmt: 格式化字符串
        
    Returns:
        datetime: 解析后的datetime对象
    """
    if not date_string:
        return None
    return datetime.strptime(date_string, fmt)


# 初始化时区
sync_time_to_china()
