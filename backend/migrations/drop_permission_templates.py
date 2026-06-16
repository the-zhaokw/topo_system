"""重建 permission_templates 表（移除对 users 表的 FK，避免 SQLAlchemy 重复注册冲突）"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhanced_app import app, db, init_extensions
from sqlalchemy import text

init_extensions(app)
with app.app_context():
    print("Dropping permission_templates (if exists)...")
    db.session.execute(text("DROP TABLE IF EXISTS permission_templates"))
    db.session.commit()
    print("Done. Now run migrate_permission_templates.py")
