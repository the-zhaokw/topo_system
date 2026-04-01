"""
初始化测试管理模块数据库表
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_app import app, db, init_db

if __name__ == '__main__':
    with app.app_context():
        print("正在初始化数据库表...")
        init_db()
        print("✅ 数据库初始化完成！")
        
        # 检查表是否创建成功
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        test_tables = [
            'test_suites',
            'test_cases',
            'test_steps',
            'test_executions',
            'test_results',
            'test_case_requirement_links'
        ]
        
        print("\n测试管理模块表检查:")
        for table in test_tables:
            if table in tables:
                print(f"✅ {table} - 已创建")
            else:
                print(f"❌ {table} - 未找到")
