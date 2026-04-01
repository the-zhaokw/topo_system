#!/usr/bin/env python3
"""检查数据库表"""

import sqlite3

def check_database_tables():
    """检查数据库中的表"""
    # 检查两个数据库文件
    db_files = ['instance/enhanced_bug_system.db', 'instance/topo_system.db']
    
    for db_file in db_files:
        try:
            print(f'检查数据库: {db_file}')
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # 检查所有表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            if tables:
                print('数据库中的表:')
                for table in tables:
                    print(f'  - {table[0]}')
            else:
                print('  数据库中没有表')
            
            conn.close()
            print()
        except Exception as e:
            print(f'检查数据库表时出错: {e}')
            print()

if __name__ == "__main__":
    check_database_tables()