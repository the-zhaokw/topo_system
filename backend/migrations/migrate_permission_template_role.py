"""给 permission_templates 表增加 role 列，并回填内置模板的 role 与考勤权限

适用于已初始化过内置模板、但尚未包含 role 字段的既有数据库。
幂等：可重复执行，不会重复加列、不会破坏手动配置。
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhanced_app import app, db, init_extensions
from sqlalchemy import text

init_extensions(app)


def column_exists(conn, table, column):
    res = conn.execute(text(f"PRAGMA table_info({table})"))
    return any(row[1] == column for row in res)


# 内置模板 -> role 映射
TEMPLATE_ROLE_MAP = {
    '新人默认模板': 'user',
    '开发工程师模板': 'software_engineer',
    '测试工程师模板': 'test_engineer',
    '项目经理模板': 'project_manager',
    '考勤管理员模板': 'hr',
}

# 测试工程师模板补充考勤权限后的完整 allowed 列表
TEST_ENGINEER_ALLOWED = [
    'bug:view', 'bug:create', 'bug:edit', 'bug:assign', 'bug:resolve', 'bug:close',
    'bug:comment', 'bug:upload_attachment', 'bug:download_attachment', 'bug:export',
    'bug:import', 'bug:view_statistics',
    'requirement:view',
    'test:view', 'test:suite_create', 'test:suite_edit', 'test:case_create',
    'test:case_edit', 'test:case_review', 'test:execution_create',
    'test:execution_edit', 'test:result_submit', 'test:view_report',
    'attendance:view', 'attendance:clock_in', 'attendance:clock_out',
    'attendance:leave_apply', 'attendance:overtime_apply', 'attendance:exception_handle',
]

# 开发工程师模板补充考勤权限后的完整 allowed 列表
SOFTWARE_ENGINEER_ALLOWED = [
    'project:view',
    'bug:view', 'bug:create', 'bug:edit', 'bug:comment', 'bug:download_attachment',
    'task:view', 'task:create', 'task:edit',
    'requirement:view', 'test:view',
    'attendance:view', 'attendance:clock_in', 'attendance:clock_out',
    'attendance:leave_apply', 'attendance:overtime_apply', 'attendance:exception_handle',
]


def migrate():
    with app.app_context():
        try:
            print("开始迁移：permission_templates 增加 role 列...")

            # 1. 加 role 列（如不存在）
            if not column_exists(db.session, 'permission_templates', 'role'):
                db.session.execute(text("ALTER TABLE permission_templates ADD COLUMN role VARCHAR(50)"))
                db.session.commit()
                print("  - 已添加 role 列")
            else:
                print("  - role 列已存在，跳过")

            # 2. 回填各内置模板的 role
            for name, role in TEMPLATE_ROLE_MAP.items():
                db.session.execute(
                    text("UPDATE permission_templates SET role=:r WHERE name=:n AND is_builtin=1"),
                    {'r': role, 'n': name}
                )
            db.session.commit()
            print(f"  - 已回填 {len(TEMPLATE_ROLE_MAP)} 个内置模板的 role")

            # 3. 更新测试工程师模板的 allowed_permissions（补充考勤权限）
            test_json = json.dumps(TEST_ENGINEER_ALLOWED, ensure_ascii=False)
            db.session.execute(
                text("UPDATE permission_templates SET allowed_permissions=:a WHERE name='测试工程师模板' AND is_builtin=1"),
                {'a': test_json}
            )
            print("  - 已更新测试工程师模板的 allowed_permissions（补充考勤权限）")

            # 4. 更新开发工程师模板的 allowed_permissions（补充考勤权限）
            dev_json = json.dumps(SOFTWARE_ENGINEER_ALLOWED, ensure_ascii=False)
            db.session.execute(
                text("UPDATE permission_templates SET allowed_permissions=:a WHERE name='开发工程师模板' AND is_builtin=1"),
                {'a': dev_json}
            )
            print("  - 已更新开发工程师模板的 allowed_permissions（补充考勤权限）")

            db.session.commit()
            print("\n✅ 迁移完成！")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ 迁移失败: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == '__main__':
    migrate()
