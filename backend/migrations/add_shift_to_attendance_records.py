"""
为 attendance_records 表添加 user_shift_id 和 shift_id 字段
将打卡记录与排班记录关联起来
"""
import sqlite3
import os
from datetime import datetime

DB_PATHS = [
    'topo_system.db',
    'instance/topo_system.db',
    'backend/instance/topo_system.db',
    'backend/topo_system.db',
]


def get_table_columns(cursor, table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    return {row[1] for row in cursor.fetchall()}


def has_table(cursor, table_name):
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )
    return cursor.fetchone() is not None


def migrate():
    for db_path in DB_PATHS:
        if not os.path.exists(db_path):
            print(f"[跳过] {db_path} 不存在")
            continue

        print(f"\n=== 处理数据库: {db_path} ===")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            if not has_table(cursor, 'attendance_records'):
                print(f"  [跳过] attendance_records 表不存在")
                continue

            cols = get_table_columns(cursor, 'attendance_records')

            if 'user_shift_id' not in cols:
                print(f"  [+] 添加 user_shift_id 列")
                cursor.execute(
                    "ALTER TABLE attendance_records ADD COLUMN user_shift_id INTEGER"
                )
            else:
                print(f"  [.] user_shift_id 已存在")

            if 'shift_id' not in cols:
                print(f"  [+] 添加 shift_id 列")
                cursor.execute(
                    "ALTER TABLE attendance_records ADD COLUMN shift_id INTEGER"
                )
            else:
                print(f"  [.] shift_id 已存在")

            # 为已有打卡记录回填 shift_id（按 user_id + record_date 找到生效的 user_shift）
            print(f"  [回填] 为历史打卡记录回填 user_shift_id / shift_id")
            cursor.execute("""
                SELECT ar.id, ar.user_id, ar.record_date
                FROM attendance_records ar
                WHERE ar.user_shift_id IS NULL OR ar.shift_id IS NULL
            """)
            rows = cursor.fetchall()
            filled = 0
            for ar_id, user_id, record_date in rows:
                if not record_date:
                    continue
                date_str = record_date[:10]
                cursor.execute("""
                    SELECT id, shift_id FROM user_shifts
                    WHERE user_id = ?
                      AND date(effective_date) <= date(?)
                      AND (expire_date IS NULL OR date(expire_date) >= date(?))
                    ORDER BY date(effective_date) DESC
                    LIMIT 1
                """, (user_id, date_str, date_str))
                us = cursor.fetchone()
                if us:
                    cursor.execute("""
                        UPDATE attendance_records
                        SET user_shift_id = ?, shift_id = ?
                        WHERE id = ?
                    """, (us[0], us[1], ar_id))
                    filled += 1
            print(f"  [回填] 完成 {filled} / {len(rows)} 条")

            conn.commit()
            print(f"  [完成] {db_path}")
        except Exception as e:
            conn.rollback()
            print(f"  [错误] {e}")
            import traceback
            traceback.print_exc()
        finally:
            conn.close()


if __name__ == '__main__':
    print(f"开始执行迁移: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    migrate()
    print("\n迁移完成")
