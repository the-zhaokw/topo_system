#!/usr/bin/env python3
"""
数据库迁移脚本
为知识库模块添加新字段
"""

import sqlite3
import os

def migrate():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'topo_system.db')

    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA table_info(knowledge_categories)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'is_archived' not in columns:
            cursor.execute("ALTER TABLE knowledge_categories ADD COLUMN is_archived INTEGER DEFAULT 0")
            print("已添加 knowledge_categories.is_archived 字段")
        else:
            print("knowledge_categories.is_archived 字段已存在")

        cursor.execute("PRAGMA table_info(knowledge_articles)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'cover_image' not in columns:
            cursor.execute("ALTER TABLE knowledge_articles ADD COLUMN cover_image VARCHAR(500)")
            print("已添加 knowledge_articles.cover_image 字段")
        else:
            print("knowledge_articles.cover_image 字段已存在")

        if 'status' not in columns:
            cursor.execute("ALTER TABLE knowledge_articles ADD COLUMN status VARCHAR(20) DEFAULT 'draft'")
            print("已添加 knowledge_articles.status 字段")
        else:
            print("knowledge_articles.status 字段已存在")

        conn.commit()
        print("数据库迁移完成！")

    except Exception as e:
        print(f"迁移错误: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
