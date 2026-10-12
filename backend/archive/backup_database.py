#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""数据库备份脚本"""

import os
import shutil
from datetime import datetime

def backup_database():
    """备份数据库"""
    source_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'topo_system.db')
    backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
    
    # 创建备份目录
    os.makedirs(backup_dir, exist_ok=True)
    
    # 生成备份文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f'topo_system_backup_{timestamp}.db')
    
    try:
        # 复制数据库文件
        shutil.copy2(source_db, backup_file)
        print(f"✅ 数据库备份成功: {backup_file}")
        return True
    except Exception as e:
        print(f"❌ 数据库备份失败: {e}")
        return False

if __name__ == "__main__":
    backup_database()
