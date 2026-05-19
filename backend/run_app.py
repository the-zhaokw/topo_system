#!/usr/bin/env python3
"""
独立的Flask应用启动脚本
避免SQLAlchemy初始化问题
"""
import sqlite3
import os
import logging

logging.getLogger('werkzeug').setLevel(logging.ERROR)

from enhanced_app import app, db, init_db, register_api_blueprints, init_extensions
from restful_api import api_bp

def ensure_columns():
    """确保数据库有新增的列 - 完善的迁移脚本，检查所有模型字段"""
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'topo_system.db')
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}，跳过列检查")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取现有表和列信息
    def get_existing_columns(table_name):
        """获取表中已存在的列名"""
        try:
            cursor.execute(f"PRAGMA table_info({table_name})")
            return {row[1] for row in cursor.fetchall()}
        except sqlite3.OperationalError:
            return set()
    
    # 定义所有表的列
    # users 表列定义
    users_columns = {
        'email_notification_enabled': 'INTEGER DEFAULT 1',
        'email_on_bug_assigned': 'INTEGER DEFAULT 1',
        'email_on_bug_closed': 'INTEGER DEFAULT 1',
        'salt': 'VARCHAR(32)',
        'role': 'VARCHAR(50) DEFAULT "user"',
        'is_admin': 'INTEGER DEFAULT 0',
        'is_active': 'INTEGER DEFAULT 1',
        'first_name': 'VARCHAR(50)',
        'last_name': 'VARCHAR(50)',
        'department': 'VARCHAR(100)',
        'position': 'VARCHAR(100)',
        'phone': 'VARCHAR(20)',
        'employee_id': 'VARCHAR(50)',
        'company_phone': 'VARCHAR(20)',
        'mobile_phone': 'VARCHAR(20)',
        'birthday': 'DATETIME',
        'gender': 'VARCHAR(20)',
        'work_language': 'VARCHAR(50)',
        'avatar': 'VARCHAR(255)',
        'last_login': 'DATETIME',
        'last_activity': 'DATETIME',
        'custom_permissions': 'TEXT DEFAULT \'{}\'',
        'is_super_admin': 'INTEGER DEFAULT 0'
    }
    
    # bugs 表列定义
    bugs_columns = {
        'resolved_by': 'INTEGER',
        'verifier_id': 'INTEGER',
        'verified_by': 'INTEGER',
        'verified_at': 'DATETIME',
        'version': 'VARCHAR(50)',
        'tags': 'TEXT',
        'issue_type': 'VARCHAR(50)',
        'reproduce_frequency': 'VARCHAR(50)',
        'found_build': 'VARCHAR(50)',
        'test_version': 'VARCHAR(50)',
        'module': 'VARCHAR(100)',
        'reproduce_steps': 'TEXT',
        'steps_to_reproduce': 'TEXT',
        'expected_result': 'TEXT',
        'actual_result': 'TEXT',
        'attachment_path': 'VARCHAR(255)',
        'resolution': 'TEXT',
        'resolution_version': 'VARCHAR(50)',
        'reopened_count': 'INTEGER DEFAULT 0',
        'related_bug_id': 'INTEGER',
        'parent_bug_id': 'INTEGER',
        'estimated_hours': 'FLOAT',
        'actual_hours': 'FLOAT',
        'test_case_id': 'VARCHAR(50)',
        'bug_type': 'VARCHAR(50)',
        'root_cause': 'VARCHAR(50)',
        'customer_mr_number': 'VARCHAR(100)',
        'plan_resolve_version': 'VARCHAR(50)',
        'resolve_build': 'VARCHAR(50)',
        'deadline': 'DATETIME',
        'closed_at': 'DATETIME',
        'resolved_at': 'DATETIME'
    }
    
    # tasks 表列定义
    tasks_columns = {
        'title': 'VARCHAR(255) NOT NULL',
        'description': 'TEXT NOT NULL',
        'status': 'VARCHAR(20) DEFAULT "todo"',
        'priority': 'VARCHAR(20) DEFAULT "medium"',
        'project_id': 'INTEGER NOT NULL',
        'assigned_to': 'INTEGER',
        'created_by': 'INTEGER NOT NULL',
        'due_date': 'DATETIME',
        'start_date': 'DATETIME',
        'estimated_hours': 'FLOAT',
        'actual_hours': 'FLOAT',
        'progress': 'INTEGER DEFAULT 0',
        'parent_task_id': 'INTEGER',
        'related_bug_id': 'INTEGER',
        'milestone': 'VARCHAR(100)',
        'tags': 'TEXT',
        'participants': 'TEXT',
        'notes': 'TEXT',
        'depends_on': 'TEXT',
        'created_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
        'updated_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
        'completed_at': 'DATETIME'
    }
    
    # projects 表列定义
    projects_columns = {
        'name': 'VARCHAR(200) NOT NULL',
        'code': 'VARCHAR(100) UNIQUE NOT NULL',
        'description': 'TEXT',
        'status': 'VARCHAR(50) DEFAULT "active"',
        'start_date': 'DATETIME',
        'end_date': 'DATETIME',
        'created_by': 'INTEGER',
        'created_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
        'updated_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
        'owner_id': 'INTEGER',
        'manager_id': 'INTEGER',
        'progress': 'INTEGER DEFAULT 0',
        'current_stage': 'VARCHAR(100)',
        'quality': 'VARCHAR(50)',
        'risk': 'VARCHAR(50)',
        'resources': 'TEXT',
        'cost': 'FLOAT DEFAULT 0.0',
        'priority': 'VARCHAR(50)',
        'technology_stack': 'TEXT',
        'budget': 'FLOAT DEFAULT 0.0',
        'actual_cost': 'FLOAT DEFAULT 0.0',
        'project_type': 'VARCHAR(50)',
        'client_name': 'VARCHAR(200)',
        'client_contact': 'VARCHAR(200)',
        'contract_value': 'FLOAT DEFAULT 0.0',
        'estimated_hours': 'INTEGER DEFAULT 0',
        'actual_hours': 'INTEGER DEFAULT 0',
        'team_size': 'INTEGER DEFAULT 0',
        'tags': 'TEXT',
        'milestones': 'TEXT',
        'versions': 'TEXT'
    }
    
    # project_members 表列定义
    project_members_columns = {
        'project_id': 'INTEGER NOT NULL',
        'user_id': 'INTEGER NOT NULL',
        'role': 'VARCHAR(50) DEFAULT "member"'
    }

    # 注意: joined_at 列需要在表创建时单独处理，SQLite不支持 ALTER TABLE ADD COLUMN with DEFAULT CURRENT_TIMESTAMP
    
    # comments 表列定义
    comments_columns = {
        'content': 'TEXT NOT NULL',
        'created_by': 'INTEGER NOT NULL',
        'created_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
        'updated_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
        'commentable_type': 'VARCHAR(50) NOT NULL',
        'commentable_id': 'INTEGER NOT NULL'
    }
    
    # attachments 表列定义
    attachments_columns = {
        'filename': 'VARCHAR(255) NOT NULL',
        'file_path': 'VARCHAR(500) NOT NULL',
        'file_size': 'INTEGER',
        'mime_type': 'VARCHAR(100)',
        'created_by': 'INTEGER NOT NULL',
        'created_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
        'attachable_type': 'VARCHAR(50) NOT NULL',
        'attachable_id': 'INTEGER NOT NULL'
    }
    
    # notifications 表列定义
    # 注意: SQLite不支持 ALTER TABLE ADD COLUMN 添加 NOT NULL 列(无默认值)
    # 因此使用允许NULL的定义，迁移后再处理约束
    notifications_columns = {
        'user_id': 'INTEGER NOT NULL',
        'type': 'VARCHAR(50)',
        'title': 'VARCHAR(255) NOT NULL',
        'content': 'TEXT NOT NULL',
        'related_bug_id': 'INTEGER',
        'related_comment_id': 'INTEGER',
        'link': 'VARCHAR(500)',
        'is_read': 'INTEGER DEFAULT 0',
        'created_at': 'DATETIME',
        'read_at': 'DATETIME'
    }
    
    # audit_logs 表列定义
    audit_logs_columns = {
        'user_id': 'INTEGER',
        'action': 'VARCHAR(100) NOT NULL',
        'resource_type': 'VARCHAR(50) NOT NULL',
        'resource_id': 'INTEGER',
        'details': 'TEXT',
        'ip_address': 'VARCHAR(50)',
        'user_agent': 'TEXT',
        'created_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP'
    }

    # test_suites 表列定义
    test_suites_columns = {
        'project_id': 'INTEGER NOT NULL',
        'parent_id': 'INTEGER',
        'name': 'VARCHAR(200) NOT NULL',
        'description': 'TEXT',
        'type': 'VARCHAR(50) DEFAULT "functional"',
        'status': 'VARCHAR(20) DEFAULT "designing"',
        'priority': 'INTEGER DEFAULT 2',
        'owner_id': 'INTEGER',
        'expected_duration': 'INTEGER DEFAULT 0',
        'version': 'INTEGER DEFAULT 1',
        'created_by': 'INTEGER NOT NULL',
        'created_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
        'updated_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP'
    }

    # test_cases 表列定义
    test_cases_columns = {
        'suite_id': 'INTEGER NOT NULL',
        'identifier': 'VARCHAR(50) NOT NULL',
        'title': 'VARCHAR(500) NOT NULL',
        'description': 'TEXT',
        'priority': 'INTEGER DEFAULT 2',
        'type': 'VARCHAR(50) DEFAULT "functional"',
        'status': 'VARCHAR(20) DEFAULT "designing"',
        'precondition': 'TEXT',
        'test_data': 'TEXT',
        'environment': 'TEXT',
        'is_automated': 'INTEGER DEFAULT 0',
        'automation_script': 'VARCHAR(500)',
        'tags': 'TEXT',
        'estimated_duration': 'INTEGER DEFAULT 0',
        'designer_id': 'INTEGER',
        'reviewer_id': 'INTEGER',
        'approved_by': 'INTEGER',
        'version': 'INTEGER DEFAULT 1',
        'created_by': 'INTEGER NOT NULL',
        'created_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
        'updated_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP'
    }

    # test_steps 表列定义
    test_steps_columns = {
        'case_id': 'INTEGER NOT NULL',
        'step_number': 'INTEGER NOT NULL',
        'action': 'TEXT NOT NULL',
        'expected_result': 'TEXT',
        'attachments': 'TEXT',
        'created_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
        'updated_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP'
    }

    # test_executions 表列定义
    test_executions_columns = {
        'project_id': 'INTEGER NOT NULL',
        'suite_id': 'INTEGER',
        'name': 'VARCHAR(200) NOT NULL',
        'status': 'VARCHAR(20) DEFAULT "in_progress"',
        'executor_id': 'INTEGER NOT NULL',
        'started_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
        'completed_at': 'DATETIME',
        'environment': 'VARCHAR(100)',
        'test_version': 'VARCHAR(100)',
        'build_number': 'VARCHAR(100)',
        'notes': 'TEXT',
        'created_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
        'updated_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP'
    }

    # test_results 表列定义
    test_results_columns = {
        'execution_id': 'INTEGER NOT NULL',
        'case_id': 'INTEGER NOT NULL',
        'result': 'VARCHAR(20) NOT NULL',
        'actual_result': 'TEXT',
        'defect_id': 'INTEGER',
        'executor_id': 'INTEGER NOT NULL',
        'executed_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
        'duration': 'INTEGER DEFAULT 0',
        'screenshots': 'TEXT',
        'notes': 'TEXT',
        'created_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
        'updated_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP'
    }

    # test_case_requirement_links 表列定义
    test_case_requirement_links_columns = {
        'test_case_id': 'INTEGER NOT NULL',
        'requirement_id': 'INTEGER NOT NULL',
        'link_type': 'VARCHAR(50) DEFAULT "tests"',
        'created_by': 'INTEGER',
        'created_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP'
    }

    # project_logs 表列定义
    project_logs_columns = {
        'project_id': 'INTEGER NOT NULL',
        'title': 'VARCHAR(255) NOT NULL',
        'content': 'TEXT NOT NULL',
        'log_type': 'VARCHAR(50) DEFAULT "general"',
        'status': 'VARCHAR(50) DEFAULT "draft"',
        'created_by': 'INTEGER NOT NULL',
        'created_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
        'updated_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
        'logged_at': 'DATETIME',
        'start_date': 'DATE',
        'end_date': 'DATE'
    }

    # 定义所有表及其列
    all_tables = {
        'users': users_columns,
        'bugs': bugs_columns,
        'tasks': tasks_columns,
        'projects': projects_columns,
        'project_members': project_members_columns,
        'comments': comments_columns,
        'attachments': attachments_columns,
        'notifications': notifications_columns,
        'audit_logs': audit_logs_columns,
        'test_suites': test_suites_columns,
        'test_cases': test_cases_columns,
        'test_steps': test_steps_columns,
        'test_executions': test_executions_columns,
        'test_results': test_results_columns,
        'test_case_requirement_links': test_case_requirement_links_columns,
        'project_logs': project_logs_columns
    }
    
    # 添加缺失的列
    for table_name, columns in all_tables.items():
        existing_cols = get_existing_columns(table_name)
        
        if not existing_cols:
            continue
        
        for col_name, col_type in columns.items():
            if col_name not in existing_cols:
                try:
                    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")
                    print(f"已添加列: {table_name}.{col_name}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e).lower():
                        pass  # 列已存在，忽略
                    else:
                        print(f"添加列 {table_name}.{col_name} 时出错: {e}")
    
    conn.commit()
    conn.close()
    print("数据库列检查完成")

if __name__ == '__main__':
    ensure_columns()

    # 注册API蓝图 - 必须在 init_extensions 之前调用
    # 这样所有模型会在 db.init_app() 之前被导入，避免重复注册
    register_api_blueprints()

    # 初始化扩展（现在可以安全地初始化 db）
    init_extensions(app)

    # 初始化数据库
    with app.app_context():
        init_db()
    
    # 初始化 WebSocket
    try:
        from websocket_notifications import init_socketio
        socketio = init_socketio(app)
        print("WebSocket 服务已启动")
        print(" * Running on http://127.0.0.1:5000")
        print(" * Running on http://172.18.36.249:5000")
        socketio.run(app, debug=False, host='0.0.0.0', port=5000, use_reloader=False)
    except ImportError as e:
        print(f"WebSocket 模块未安装 ({e})，使用标准 Flask 服务器")
        print(" * Running on http://127.0.0.1:5000")
        print(" * Running on http://172.18.36.249:5000")
        app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
