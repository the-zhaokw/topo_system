"""为 users 表添加 accessible_modules 列，用于大功能模块权限管理"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhanced_app import app, db, init_extensions
from sqlalchemy import text


def migrate():
    """为 users 表添加 accessible_modules 列"""
    # 初始化扩展，确保 db 实例与 app 绑定
    init_extensions(app)

    with app.app_context():
        try:
            print("开始迁移：添加 accessible_modules 列...")

            result = db.session.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result]

            if 'accessible_modules' not in columns:
                db.session.execute(
                    text("ALTER TABLE users ADD COLUMN accessible_modules TEXT DEFAULT NULL")
                )
                db.session.commit()
                print("  - 成功为 users 表添加 accessible_modules 列")
            else:
                print("  - accessible_modules 列已存在，跳过")

            print("\n✅ 迁移完成！")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ 迁移失败: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == '__main__':
    migrate()
