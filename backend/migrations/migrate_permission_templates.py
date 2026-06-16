"""创建 permission_templates 表（权限模板）— 使用纯 SQL 避免 SQLAlchemy registry 冲突"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhanced_app import app, db, init_extensions
from sqlalchemy import text

init_extensions(app)


def column_exists(conn, table, column):
    res = conn.execute(text(f"PRAGMA table_info({table})"))
    return any(row[1] == column for row in res)


def table_exists(conn, table):
    res = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name=:n"), {"n": table})
    return res.fetchone() is not None


def migrate():
    with app.app_context():
        try:
            print("开始迁移：创建 permission_templates 表...")

            if not table_exists(db.session, 'permission_templates'):
                db.session.execute(text("""
                    CREATE TABLE permission_templates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name VARCHAR(100) NOT NULL UNIQUE,
                        description TEXT DEFAULT '',
                        category VARCHAR(50) DEFAULT 'custom',
                        icon VARCHAR(50) DEFAULT 'Document',
                        modules TEXT DEFAULT '[]',
                        allowed_permissions TEXT DEFAULT '[]',
                        denied_permissions TEXT DEFAULT '[]',
                        is_builtin BOOLEAN DEFAULT 0,
                        is_active BOOLEAN DEFAULT 1,
                        sort_order INTEGER DEFAULT 0,
                        created_by INTEGER,
                        created_at DATETIME,
                        updated_at DATETIME
                    )
                """))
                db.session.commit()
                print("  - 成功创建 permission_templates 表")
            else:
                print("  - permission_templates 表已存在，跳过")

            # 检查是否已有内置模板
            count = db.session.execute(text("SELECT COUNT(*) FROM permission_templates WHERE is_builtin=1")).scalar()
            if count == 0:
                print("  - 初始化内置模板...")
                from datetime import datetime
                now = datetime.utcnow().isoformat()

                from models.permissions import (
                    PermissionCodes,
                    get_default_accessible_modules,
                    get_all_permission_codes
                )
                defaults = get_default_accessible_modules()
                all_codes = list(get_all_permission_codes())

                builtin = [
                    {
                        'name': '新人默认模板',
                        'description': '面向新入职员工：拥有个人工作台、待办、计划、知识库等基础模块',
                        'icon': 'Avatar',
                        'category': 'role',
                        'sort_order': 10,
                        'modules': defaults,
                        'allowed': [],
                        'denied': [],
                    },
                    {
                        'name': '开发工程师模板',
                        'description': '面向研发：可见项目、缺陷、需求、测试、知识库等开发相关模块',
                        'icon': 'Cpu',
                        'category': 'role',
                        'sort_order': 20,
                        'modules': defaults + [
                            PermissionCodes.MODULE_PROJECT,
                            PermissionCodes.MODULE_BUG,
                            PermissionCodes.MODULE_REQUIREMENT,
                            PermissionCodes.MODULE_TEST,
                            PermissionCodes.MODULE_RISK,
                        ],
                        'allowed': [
                            PermissionCodes.PROJECT_VIEW,
                            PermissionCodes.BUG_VIEW, PermissionCodes.BUG_CREATE, PermissionCodes.BUG_EDIT,
                            PermissionCodes.BUG_COMMENT, PermissionCodes.BUG_DOWNLOAD_ATTACHMENT,
                            PermissionCodes.TASK_VIEW, PermissionCodes.TASK_CREATE, PermissionCodes.TASK_EDIT,
                            PermissionCodes.REQUIREMENT_VIEW,
                            PermissionCodes.TEST_VIEW,
                        ],
                        'denied': [
                            PermissionCodes.PROJECT_DELETE, PermissionCodes.BUG_DELETE,
                        ],
                    },
                    {
                        'name': '测试工程师模板',
                        'description': '面向测试：可见缺陷、需求、测试、考勤等模块，拥有完整测试管理权限',
                        'icon': 'MagicStick',
                        'category': 'role',
                        'sort_order': 30,
                        'modules': defaults + [
                            PermissionCodes.MODULE_BUG,
                            PermissionCodes.MODULE_REQUIREMENT,
                            PermissionCodes.MODULE_TEST,
                        ],
                        'allowed': [
                            PermissionCodes.BUG_VIEW, PermissionCodes.BUG_CREATE, PermissionCodes.BUG_EDIT,
                            PermissionCodes.BUG_ASSIGN, PermissionCodes.BUG_RESOLVE, PermissionCodes.BUG_CLOSE,
                            PermissionCodes.BUG_COMMENT, PermissionCodes.BUG_UPLOAD_ATTACHMENT,
                            PermissionCodes.BUG_DOWNLOAD_ATTACHMENT, PermissionCodes.BUG_EXPORT,
                            PermissionCodes.BUG_IMPORT, PermissionCodes.BUG_VIEW_STATISTICS,
                            PermissionCodes.REQUIREMENT_VIEW,
                            PermissionCodes.TEST_VIEW, PermissionCodes.TEST_SUITE_CREATE, PermissionCodes.TEST_SUITE_EDIT,
                            PermissionCodes.TEST_CASE_CREATE, PermissionCodes.TEST_CASE_EDIT,
                            PermissionCodes.TEST_CASE_REVIEW, PermissionCodes.TEST_EXECUTION_CREATE,
                            PermissionCodes.TEST_EXECUTION_EDIT, PermissionCodes.TEST_RESULT_SUBMIT,
                            PermissionCodes.TEST_VIEW_REPORT,
                        ],
                        'denied': [
                            PermissionCodes.BUG_DELETE,
                        ],
                    },
                    {
                        'name': '项目经理模板',
                        'description': '面向项目负责人：可见并管理项目、缺陷、需求、风险等',
                        'icon': 'Folder',
                        'category': 'role',
                        'sort_order': 40,
                        'modules': defaults + [
                            PermissionCodes.MODULE_PROJECT,
                            PermissionCodes.MODULE_BUG,
                            PermissionCodes.MODULE_REQUIREMENT,
                            PermissionCodes.MODULE_TEST,
                            PermissionCodes.MODULE_RISK,
                            PermissionCodes.MODULE_CONTRACT,
                        ],
                        'allowed': all_codes,
                        'denied': [],
                    },
                    {
                        'name': '考勤管理员模板',
                        'description': '面向 HR / 考勤专员：考勤全套管理权限',
                        'icon': 'Clock',
                        'category': 'role',
                        'sort_order': 50,
                        'modules': defaults + [PermissionCodes.MODULE_ATTENDANCE],
                        'allowed': [
                            PermissionCodes.ATTENDANCE_VIEW, PermissionCodes.ATTENDANCE_MANAGE,
                            PermissionCodes.SHIFT_MANAGE, PermissionCodes.USER_SHIFT_ASSIGN,
                            PermissionCodes.LEAVE_APPROVE, PermissionCodes.OVERTIME_APPROVE,
                            PermissionCodes.EXCEPTION_APPROVE, PermissionCodes.ATTENDANCE_REPORT,
                            PermissionCodes.ATTENDANCE_EXPORT,
                        ],
                        'denied': [],
                    },
                ]

                for t in builtin:
                    db.session.execute(text("""
                        INSERT INTO permission_templates
                        (name, description, category, icon, modules, allowed_permissions, denied_permissions,
                         is_builtin, is_active, sort_order, created_by, created_at, updated_at)
                        VALUES (:name, :desc, :cat, :icon, :mods, :allow, :deny, 1, 1, :sort, NULL, :now, :now)
                    """), {
                        'name': t['name'],
                        'desc': t['description'],
                        'cat': t['category'],
                        'icon': t['icon'],
                        'mods': json.dumps(list(dict.fromkeys(t['modules'])), ensure_ascii=False),
                        'allow': json.dumps(list(dict.fromkeys(t['allowed'])), ensure_ascii=False),
                        'deny': json.dumps(list(dict.fromkeys(t['denied'])), ensure_ascii=False),
                        'sort': t['sort_order'],
                        'now': now
                    })
                db.session.commit()
                print(f"  - 已创建 {len(builtin)} 个内置模板")
            else:
                print(f"  - 已有 {count} 个内置模板，跳过初始化")

            print("\n✅ 迁移完成！")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ 迁移失败: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == '__main__':
    migrate()
