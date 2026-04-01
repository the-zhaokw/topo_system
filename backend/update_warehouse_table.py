"""
更新warehouse表结构，添加type和description字段
"""

from enhanced_app import app, db
from sqlalchemy import text

def update_warehouse_table():
    """更新warehouse表结构"""
    with app.app_context():
        try:
            # 检查是否已存在type字段
            result = db.session.execute(text("PRAGMA table_info(warehouses)"))
            columns = [col[1] for col in result.fetchall()]
            
            # 添加type字段（如果不存在）
            if 'type' not in columns:
                print("添加type字段到warehouses表...")
                db.session.execute(text("ALTER TABLE warehouses ADD COLUMN type VARCHAR(20) DEFAULT 'normal'"))
                print("✓ type字段添加成功")
            else:
                print("✓ type字段已存在")
            
            # 添加description字段（如果不存在）
            if 'description' not in columns:
                print("添加description字段到warehouses表...")
                db.session.execute(text("ALTER TABLE warehouses ADD COLUMN description TEXT"))
                print("✓ description字段添加成功")
            else:
                print("✓ description字段已存在")
            
            # 提交更改
            db.session.commit()
            print("\n✓ 数据库表结构更新完成")
            
            # 验证更新结果
            result = db.session.execute(text("PRAGMA table_info(warehouses)"))
            updated_columns = result.fetchall()
            print("\n更新后的warehouses表结构:")
            for col in updated_columns:
                print(f'  {col[1]} ({col[2]}) - 默认值: {col[4]}')
                
        except Exception as e:
            print(f"❌ 更新失败: {e}")
            db.session.rollback()

if __name__ == '__main__':
    update_warehouse_table()