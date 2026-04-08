"""
个人工作计划系统 - 数据库迁移脚本
添加子任务、依赖关系、进度、提醒等新功能字段
"""
import sqlite3
import os
import json
from datetime import datetime

def migrate_database():
    """执行数据库迁移"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'topo_system.db')

    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 获取 personal_tasks 表的现有列
        cursor.execute("PRAGMA table_info(personal_tasks)")
        existing_columns = {row[1] for row in cursor.fetchall()}

        # 需要添加的新列定义
        new_columns = [
            ('parent_id', 'INTEGER REFERENCES personal_tasks(id)'),
            ('progress', 'INTEGER DEFAULT 0'),
            ('due_date', 'VARCHAR(20)'),
            ('dependencies', 'TEXT'),
            ('is_pinned', 'BOOLEAN DEFAULT 0'),
            ('order_index', 'INTEGER DEFAULT 0'),
            ('reminder_config', 'TEXT'),
            ('completed', 'BOOLEAN DEFAULT 0')
        ]

        # 添加新列（如果不存在）
        for column_name, column_type in new_columns:
            if column_name not in existing_columns:
                print(f"添加列: {column_name}")
                cursor.execute(f"""
                    ALTER TABLE personal_tasks
                    ADD COLUMN {column_name} {column_type}
                """)
            else:
                print(f"列已存在，跳过: {column_name}")

        # 创建 plan_templates 表（如果不存在）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plan_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                name VARCHAR(200) NOT NULL,
                description TEXT,
                template_type VARCHAR(20) DEFAULT 'daily',
                tasks_template TEXT NOT NULL,
                is_default BOOLEAN DEFAULT 0,
                created_at DATETIME,
                updated_at DATETIME
            )
        """)
        print("✓ plan_templates 表已就绪")

        # 创建 review_records 表（如果不存在）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS review_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                title VARCHAR(200),
                date_range_start VARCHAR(20) NOT NULL,
                date_range_end VARCHAR(20) NOT NULL,
                review_type VARCHAR(20) DEFAULT 'weekly',
                total_planned INTEGER DEFAULT 0,
                total_completed INTEGER DEFAULT 0,
                total_planned_hours REAL DEFAULT 0.0,
                total_actual_hours REAL DEFAULT 0.0,
                overdue_count INTEGER DEFAULT 0,
                avg_overdue_days REAL DEFAULT 0.0,
                summary_text TEXT,
                key_achievements TEXT,
                challenges TEXT,
                lessons_learned TEXT,
                next_week_plan TEXT,
                created_at DATETIME,
                updated_at DATETIME
            )
        """)
        print("✓ review_records 表已就绪")

        # 更新现有数据：将 status='inbox' 改为 'todo'（如果需要）
        cursor.execute("""
            UPDATE personal_tasks
            SET status = 'todo'
            WHERE status = 'inbox'
        """)
        print(f"✓ 已更新 {cursor.rowcount} 条任务状态 (inbox -> todo)")

        # 初始化 completed 字段基于 status
        cursor.execute("""
            UPDATE personal_tasks
            SET completed = CASE WHEN status = 'done' THEN 1 ELSE 0 END
            WHERE completed IS NULL
        """)
        print(f"✓ 已初始化 {cursor.rowcount} 条任务的完成状态")

        conn.commit()
        print("\n✅ 数据库迁移成功完成！")
        print(f"\n新增功能:")
        print("  • 子任务支持 (parent_id)")
        print("  • 进度跟踪 (progress)")
        print("  • 截止日期 (due_date)")
        print("  • 任务依赖 (dependencies)")
        print("  • 置顶功能 (is_pinned)")
        print("  • 排序索引 (order_index)")
        print("  • 提醒配置 (reminder_config)")
        print("  • 完成状态 (completed)")
        print("  • 计划模板管理 (plan_templates)")
        print("  • 复盘记录存储 (review_records)")

    except Exception as e:
        print(f"❌ 迁移失败: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
