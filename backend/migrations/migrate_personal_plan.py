"""
迁移脚本：为个人工作计划创建新的数据库表
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhanced_app import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        conn = db.engine.connect()

        tables_to_create = [
            """
            CREATE TABLE IF NOT EXISTS personal_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title VARCHAR(500) NOT NULL,
                description TEXT,
                status VARCHAR(20) DEFAULT 'inbox' NOT NULL,
                priority VARCHAR(20) DEFAULT 'medium',
                quadrant INTEGER,
                scheduled_date VARCHAR(20),
                scheduled_time VARCHAR(10),
                estimated_minutes INTEGER,
                actual_minutes INTEGER,
                tags VARCHAR(500),
                is_habit BOOLEAN DEFAULT 0,
                habit_frequency VARCHAR(20),
                source VARCHAR(20) DEFAULT 'manual',
                started_at DATETIME,
                completed_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS focus_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task_id INTEGER,
                focus_type VARCHAR(20) DEFAULT 'pomodoro',
                planned_duration INTEGER DEFAULT 25,
                actual_duration INTEGER,
                started_at DATETIME NOT NULL,
                ended_at DATETIME,
                completed BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (task_id) REFERENCES personal_tasks (id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS habit_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task_id INTEGER,
                completed_date DATE NOT NULL,
                duration_minutes INTEGER,
                note VARCHAR(200),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (task_id) REFERENCES personal_tasks (id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS personal_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                default_view VARCHAR(20) DEFAULT 'list',
                pomodoro_duration INTEGER DEFAULT 25,
                break_duration INTEGER DEFAULT 5,
                long_break_duration INTEGER DEFAULT 15,
                work_streak_alert INTEGER DEFAULT 60,
                custom_tags VARCHAR(500),
                tag_colors TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        ]

        for i, sql in enumerate(tables_to_create):
            try:
                conn.execute(text(sql))
                print(f"Table {i+1} created successfully")
            except Exception as e:
                print(f"Table {i+1} may already exist or error: {e}")

        conn.commit()
        conn.close()
        print("Migration completed!")

if __name__ == '__main__':
    migrate()