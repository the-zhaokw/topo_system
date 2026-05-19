import sqlite3
conn = sqlite3.connect('d:/topo_system/backend/instance/topo_system.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = [row[0] for row in cursor.fetchall()]
print('Tables:', tables)
try:
    cursor.execute('SELECT COUNT(*) FROM projects')
    print('Projects count:', cursor.fetchone()[0])
except Exception as e:
    print('Error querying projects:', e)
try:
    cursor.execute('SELECT COUNT(*) FROM users')
    print('Users count:', cursor.fetchone()[0])
except Exception as e:
    print('Error querying users:', e)
conn.close()