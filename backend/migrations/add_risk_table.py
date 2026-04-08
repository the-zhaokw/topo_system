"""
数据库迁移：为项目添加风险和问题管理表
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhanced_app import db
from datetime import datetime

def upgrade():
    """创建风险表"""
    from sqlalchemy import text

    with db.engine.begin() as conn:
        try:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='risks'"))
            if result.fetchone():
                print("表 risks 已存在，跳过创建")
                return

            create_table_sql = """
            CREATE TABLE risks (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                risk_type VARCHAR(20) DEFAULT 'risk',
                title VARCHAR(255) NOT NULL,
                description TEXT,
                status VARCHAR(50) DEFAULT 'identified',
                priority VARCHAR(50) DEFAULT 'medium',
                level VARCHAR(50) DEFAULT 'medium',
                category VARCHAR(50),
                identified_by INTEGER,
                assigned_to INTEGER,
                probability FLOAT DEFAULT 0.0,
                impact FLOAT DEFAULT 0.0,
                exposure FLOAT DEFAULT 0.0,
                mitigation_strategy TEXT,
                contingency_plan TEXT,
                resolution TEXT,
                identified_date DATE,
                due_date DATE,
                resolved_date DATE,
                closed_date DATE,
                trigger_condition TEXT,
                indicator VARCHAR(255),
                related_risk_id INTEGER,
                related_bug_id INTEGER,
                related_task_id INTEGER,
                created_by INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id),
                FOREIGN KEY (identified_by) REFERENCES users (id),
                FOREIGN KEY (assigned_to) REFERENCES users (id),
                FOREIGN KEY (created_by) REFERENCES users (id),
                FOREIGN KEY (related_risk_id) REFERENCES risks (id),
                FOREIGN KEY (related_bug_id) REFERENCES bugs (id),
                FOREIGN KEY (related_task_id) REFERENCES tasks (id)
            )
            """
            conn.execute(text(create_table_sql))
            print("表 risks 创建成功")
        except Exception as e:
            print(f"创建表 risks 失败: {e}")
            raise

def downgrade():
    """删除风险表"""
    from sqlalchemy import text

    with db.engine.begin() as conn:
        try:
            conn.execute(text("DROP TABLE IF EXISTS risks"))
            print("表 risks 已删除")
        except Exception as e:
            print(f"删除表 risks 失败: {e}")
            raise

if __name__ == '__main__':
    upgrade()