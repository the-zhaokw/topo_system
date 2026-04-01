#!/usr/bin/env python3
"""
修复数据库字段
"""
import sys
import os
sys.path.insert(0, '.')

from enhanced_app import app, db
from sqlalchemy import text

def fix_database():
    with app.app_context():
        # 检查并添加缺失的字段
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        # 检查 knowledge_favorites 表
        print("Checking knowledge_favorites...")
        cols = inspector.get_columns('knowledge_favorites')
        col_names = [c['name'] for c in cols]
        
        if 'folder_name' not in col_names:
            db.session.execute(text("ALTER TABLE knowledge_favorites ADD COLUMN folder_name VARCHAR(100)"))
            print("  Added folder_name")
        
        # 检查 knowledge_read_records 表
        print("Checking knowledge_read_records...")
        cols = inspector.get_columns('knowledge_read_records')
        col_names = [c['name'] for c in cols]
        
        if 'read_duration' not in col_names:
            db.session.execute(text("ALTER TABLE knowledge_read_records ADD COLUMN read_duration INTEGER DEFAULT 0"))
            print("  Added read_duration")
        
        if 'is_finished' not in col_names:
            db.session.execute(text("ALTER TABLE knowledge_read_records ADD COLUMN is_finished BOOLEAN DEFAULT 0"))
            print("  Added is_finished")
        
        # 检查 knowledge_comments 表
        print("Checking knowledge_comments...")
        cols = inspector.get_columns('knowledge_comments')
        col_names = [c['name'] for c in cols]
        
        if 'is_resolved' not in col_names:
            db.session.execute(text("ALTER TABLE knowledge_comments ADD COLUMN is_resolved BOOLEAN DEFAULT 0"))
            print("  Added is_resolved")
        
        db.session.commit()
        print("\nDatabase fixed successfully!")

if __name__ == '__main__':
    fix_database()
