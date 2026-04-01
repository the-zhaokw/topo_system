"""验证数据库结构"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'topo_system.db')
print(f"Database path: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('PRAGMA table_info(users)')
    columns = {row[1] for row in cursor.fetchall()}
    print(f"'custom_permissions' in columns: {'custom_permissions' in columns}")
    print(f"All columns: {columns}")

    # 检查当前应用使用的数据库
    from enhanced_app import app
    with app.app_context():
        from enhanced_app import db, User
        # 尝试查询用户
        try:
            user = User.query.first()
            print(f"User query successful: {user.username if user else 'No user found'}")
        except Exception as e:
            print(f"User query error: {e}")

    conn.close()