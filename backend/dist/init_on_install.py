#!/usr/bin/env python3
"""
TOPO System 安装后初始化脚本
首次运行安装的程序时自动调用
"""
import os
import sys
import sqlite3
from datetime import datetime

def get_app_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def init_database():
    app_path = get_app_path()
    instance_path = os.path.join(app_path, 'instance')
    db_path = os.path.join(instance_path, 'topo_system.db')

    os.makedirs(instance_path, exist_ok=True)

    if os.path.exists(db_path):
        print(f"[INFO] 数据库已存在: {db_path}")
        return

    print(f"[INFO] 初始化数据库: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(80) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        email VARCHAR(120) UNIQUE NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        email_notification_enabled INTEGER DEFAULT 1,
        email_on_bug_assigned INTEGER DEFAULT 1,
        email_on_bug_closed INTEGER DEFAULT 1,
        salt VARCHAR(32),
        role VARCHAR(50) DEFAULT "user",
        is_admin INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        department VARCHAR(100),
        position VARCHAR(100),
        phone VARCHAR(20),
        employee_id VARCHAR(50),
        company_phone VARCHAR(20),
        mobile_phone VARCHAR(20),
        birthday DATETIME,
        gender VARCHAR(20),
        work_language VARCHAR(50),
        avatar VARCHAR(255),
        last_login DATETIME,
        custom_permissions TEXT DEFAULT '{}',
        is_super_admin INTEGER DEFAULT 0
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(200) NOT NULL,
        code VARCHAR(100) UNIQUE NOT NULL,
        description TEXT,
        status VARCHAR(50) DEFAULT "active",
        start_date DATETIME,
        end_date DATETIME,
        created_by INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        owner_id INTEGER,
        manager_id INTEGER,
        progress INTEGER DEFAULT 0,
        current_stage VARCHAR(100),
        quality VARCHAR(50),
        risk VARCHAR(50),
        resources TEXT,
        cost FLOAT DEFAULT 0.0,
        priority VARCHAR(50),
        technology_stack TEXT,
        budget FLOAT DEFAULT 0.0,
        actual_cost FLOAT DEFAULT 0.0,
        project_type VARCHAR(50),
        client_name VARCHAR(200),
        client_contact VARCHAR(200),
        contract_value FLOAT DEFAULT 0.0,
        estimated_hours INTEGER DEFAULT 0,
        actual_hours INTEGER DEFAULT 0,
        team_size INTEGER DEFAULT 0,
        tags TEXT,
        milestones TEXT,
        versions TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bugs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(500) NOT NULL,
        description TEXT,
        status VARCHAR(50) DEFAULT "open",
        priority VARCHAR(50) DEFAULT "medium",
        severity VARCHAR(50) DEFAULT "medium",
        project_id INTEGER,
        reported_by INTEGER,
        assigned_to INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        resolved_by INTEGER,
        verifier_id INTEGER,
        verified_by INTEGER,
        verified_at DATETIME,
        version VARCHAR(50),
        tags TEXT,
        issue_type VARCHAR(50),
        reproduce_frequency VARCHAR(50),
        found_build VARCHAR(50),
        test_version VARCHAR(50),
        module VARCHAR(100),
        reproduce_steps TEXT,
        steps_to_reproduce TEXT,
        expected_result TEXT,
        actual_result TEXT,
        attachment_path VARCHAR(255),
        resolution TEXT,
        resolution_version VARCHAR(50),
        reopened_count INTEGER DEFAULT 0,
        related_bug_id INTEGER,
        parent_bug_id INTEGER,
        estimated_hours FLOAT,
        actual_hours FLOAT,
        test_case_id VARCHAR(50),
        bug_type VARCHAR(50),
        root_cause VARCHAR(50),
        customer_mr_number VARCHAR(100),
        plan_resolve_version VARCHAR(50),
        resolve_build VARCHAR(50),
        deadline DATETIME,
        closed_at DATETIME,
        resolved_at DATETIME
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(255) NOT NULL,
        description TEXT NOT NULL,
        status VARCHAR(20) DEFAULT "todo",
        priority VARCHAR(20) DEFAULT "medium",
        project_id INTEGER NOT NULL,
        assigned_to INTEGER,
        created_by INTEGER NOT NULL,
        due_date DATETIME,
        start_date DATETIME,
        estimated_hours FLOAT,
        actual_hours FLOAT,
        progress INTEGER DEFAULT 0,
        parent_task_id INTEGER,
        related_bug_id INTEGER,
        milestone VARCHAR(100),
        tags TEXT,
        participants TEXT,
        notes TEXT,
        depends_on TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        completed_at DATETIME
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS project_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        role VARCHAR(50) DEFAULT "member",
        joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(project_id, user_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        type VARCHAR(50),
        title VARCHAR(255) NOT NULL,
        content TEXT NOT NULL,
        related_bug_id INTEGER,
        related_comment_id INTEGER,
        link VARCHAR(500),
        is_read INTEGER DEFAULT 0,
        created_at DATETIME,
        read_at DATETIME
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action VARCHAR(100) NOT NULL,
        resource_type VARCHAR(50) NOT NULL,
        resource_id INTEGER,
        details TEXT,
        ip_address VARCHAR(50),
        user_agent TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]

    if user_count == 0:
        print("[INFO] 创建默认管理员账户...")
        import hashlib
        import secrets
        salt = secrets.token_hex(16)
        password = 'admin123'
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()

        cursor.execute('''
            INSERT INTO users (username, password_hash, email, salt, role, is_admin, is_super_admin, first_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('admin', password_hash, 'admin@topo.local', salt, 'admin', 1, 1, '系统'))

        conn.commit()
        print("[INFO] 默认管理员账户已创建")
        print("       用户名: admin")
        print("       密码: admin123")

    conn.close()
    print("[INFO] 数据库初始化完成")

def create_directories():
    app_path = get_app_path()
    dirs = ['instance', 'uploads', 'logs', 'backups']
    for d in dirs:
        path = os.path.join(app_path, d)
        os.makedirs(path, exist_ok=True)
    print("[INFO] 目录结构已创建")

def main():
    print("=" * 50)
    print("   TOPO System 初始化")
    print("=" * 50)
    print()

    try:
        create_directories()
        init_database()

        print()
        print("=" * 50)
        print("   初始化完成！")
        print("=" * 50)
        print()
        print("默认管理员账户:")
        print("  用户名: admin")
        print("  密码: admin123")
        print()
        print("首次使用请修改默认密码！")
        print()

        return 0
    except Exception as e:
        print(f"[错误] 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
