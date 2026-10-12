#!/usr/bin/env python3
"""
数据库修复脚本 - 添加缺失的 users.status 列
"""
import os
import sys

# 添加 backend 目录到路径
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from enhanced_app import app, db
from sqlalchemy import inspect, text

def fix_users_status_column():
    """添加 users 表缺失的 status 列"""
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            
            # 检查 users 表是否存在
            if not inspector.has_table('users'):
                print("错误: users 表不存在")
                return False
            
            # 获取现有列
            existing_columns = [col['name'] for col in inspector.get_columns('users')]
            print(f"现有列: {existing_columns}")
            
            # 添加缺失的 status 列
            if 'status' not in existing_columns:
                print("正在添加 status 列...")
                db.session.execute(text("ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'online'"))
                db.session.commit()
                print("✓ status 列添加成功")
            else:
                print("✓ status 列已存在，无需添加")
            
            # 检查其他可能缺失的列
            columns_to_check = {
                'custom_permissions': "TEXT DEFAULT '{}'",
                'is_super_admin': "BOOLEAN DEFAULT 0",
                'email_notification_enabled': "BOOLEAN DEFAULT 1",
                'email_on_bug_assigned': "BOOLEAN DEFAULT 1",
                'email_on_bug_closed': "BOOLEAN DEFAULT 1",
            }
            
            for col_name, col_type in columns_to_check.items():
                if col_name not in existing_columns:
                    print(f"正在添加 {col_name} 列...")
                    try:
                        db.session.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                        db.session.commit()
                        print(f"✓ {col_name} 列添加成功")
                    except Exception as e:
                        db.session.rollback()
                        print(f"✗ 添加 {col_name} 列失败: {e}")
                else:
                    print(f"✓ {col_name} 列已存在")
            
            print("\n数据库修复完成!")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("=" * 50)
    print("数据库修复工具")
    print("=" * 50)
    success = fix_users_status_column()
    sys.exit(0 if success else 1)
