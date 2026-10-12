import sqlite3

db_path = 'topo_system.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute('ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT "online"')
    conn.commit()
    print('status列添加成功到 topo_system.db！')
except Exception as e:
    print(f'添加列失败: {e}')
finally:
    conn.close()
