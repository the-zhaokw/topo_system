-- ============================================================
-- TOPO 系统时区修正脚本
-- 将所有 DATETIME 字段从 UTC(+0)修正为北京时间(+8)
--
-- 使用方法:
--   1. 先备份数据库:
--      copy "d:\topo_system\backend\instance\topo_system.db" "d:\topo_system\backend\instance\topo_system_backup_before_tz_fix.db"
--   2. 执行本脚本:
--      sqlite3 "d:\topo_system\backend\instance\topo_system.db" < "d:\topo_system\backend\fix_utc_to_beijing.sql"
--
-- 说明:
--   - 仅修正 DATETIME 类型字段(含日期+时间)
--   - 不修正 VARCHAR 类型的纯时间字段(如 shift_schedules.start_time)
--   - 不修正 DATE 类型字段(纯日期,UTC 与北京日期基本一致)
--   - 使用 datetime(field, '+8 hours') 进行修正
--   - 仅更新非 NULL 的记录
-- ============================================================

BEGIN TRANSACTION;

-- ---------- activities ----------
UPDATE activities SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;

-- ---------- attachments ----------
UPDATE attachments SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;

-- ---------- attendance_exceptions ----------
UPDATE attendance_exceptions SET approved_at = datetime(approved_at, '+8 hours') WHERE approved_at IS NOT NULL;
UPDATE attendance_exceptions SET created_at  = datetime(created_at,  '+8 hours') WHERE created_at  IS NOT NULL;
UPDATE attendance_exceptions SET record_date = datetime(record_date, '+8 hours') WHERE record_date IS NOT NULL;
UPDATE attendance_exceptions SET updated_at  = datetime(updated_at,  '+8 hours') WHERE updated_at  IS NOT NULL;

-- ---------- attendance_records ----------
UPDATE attendance_records SET clock_in_time  = datetime(clock_in_time,  '+8 hours') WHERE clock_in_time  IS NOT NULL;
UPDATE attendance_records SET clock_out_time = datetime(clock_out_time, '+8 hours') WHERE clock_out_time IS NOT NULL;
UPDATE attendance_records SET created_at     = datetime(created_at,     '+8 hours') WHERE created_at     IS NOT NULL;
UPDATE attendance_records SET record_date     = datetime(record_date,    '+8 hours') WHERE record_date    IS NOT NULL;
UPDATE attendance_records SET updated_at     = datetime(updated_at,     '+8 hours') WHERE updated_at     IS NOT NULL;

-- ---------- audit_logs ----------
UPDATE audit_logs SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;

-- ---------- bug_comments ----------
UPDATE bug_comments SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE bug_comments SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- bugs ----------
UPDATE bugs SET closed_at   = datetime(closed_at,   '+8 hours') WHERE closed_at   IS NOT NULL;
UPDATE bugs SET created_at  = datetime(created_at,  '+8 hours') WHERE created_at  IS NOT NULL;
UPDATE bugs SET deadline    = datetime(deadline,    '+8 hours') WHERE deadline    IS NOT NULL;
UPDATE bugs SET resolved_at = datetime(resolved_at, '+8 hours') WHERE resolved_at IS NOT NULL;
UPDATE bugs SET updated_at  = datetime(updated_at,  '+8 hours') WHERE updated_at  IS NOT NULL;
UPDATE bugs SET verified_at = datetime(verified_at, '+8 hours') WHERE verified_at IS NOT NULL;

-- ---------- comments ----------
UPDATE comments SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE comments SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- contract_approvals ----------
UPDATE contract_approvals SET approval_date = datetime(approval_date, '+8 hours') WHERE approval_date IS NOT NULL;
UPDATE contract_approvals SET created_at    = datetime(created_at,     '+8 hours') WHERE created_at    IS NOT NULL;

-- ---------- contract_attachments ----------
UPDATE contract_attachments SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;

-- ---------- contract_changes ----------
UPDATE contract_changes SET approval_date = datetime(approval_date, '+8 hours') WHERE approval_date IS NOT NULL;
UPDATE contract_changes SET created_at    = datetime(created_at,    '+8 hours') WHERE created_at    IS NOT NULL;

-- ---------- contract_clauses ----------
UPDATE contract_clauses SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;

-- ---------- contract_deliveries ----------
UPDATE contract_deliveries SET actual_date  = datetime(actual_date,  '+8 hours') WHERE actual_date  IS NOT NULL;
UPDATE contract_deliveries SET created_at   = datetime(created_at,   '+8 hours') WHERE created_at   IS NOT NULL;
UPDATE contract_deliveries SET planned_date = datetime(planned_date, '+8 hours') WHERE planned_date IS NOT NULL;
UPDATE contract_deliveries SET updated_at   = datetime(updated_at,   '+8 hours') WHERE updated_at   IS NOT NULL;

-- ---------- contract_payments ----------
UPDATE contract_payments SET actual_date  = datetime(actual_date,  '+8 hours') WHERE actual_date  IS NOT NULL;
UPDATE contract_payments SET created_at   = datetime(created_at,   '+8 hours') WHERE created_at   IS NOT NULL;
UPDATE contract_payments SET planned_date = datetime(planned_date, '+8 hours') WHERE planned_date IS NOT NULL;

-- ---------- contract_risks ----------
UPDATE contract_risks SET created_at      = datetime(created_at,      '+8 hours') WHERE created_at      IS NOT NULL;
UPDATE contract_risks SET identified_date = datetime(identified_date, '+8 hours') WHERE identified_date IS NOT NULL;
UPDATE contract_risks SET resolved_date   = datetime(resolved_date,   '+8 hours') WHERE resolved_date   IS NOT NULL;

-- ---------- contracts ----------
UPDATE contracts SET created_at      = datetime(created_at,      '+8 hours') WHERE created_at      IS NOT NULL;
UPDATE contracts SET effective_date   = datetime(effective_date,  '+8 hours') WHERE effective_date   IS NOT NULL;
UPDATE contracts SET expiration_date  = datetime(expiration_date, '+8 hours') WHERE expiration_date  IS NOT NULL;
UPDATE contracts SET signing_date     = datetime(signing_date,    '+8 hours') WHERE signing_date     IS NOT NULL;
UPDATE contracts SET updated_at       = datetime(updated_at,       '+8 hours') WHERE updated_at       IS NOT NULL;

-- ---------- departments ----------
UPDATE departments SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE departments SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- focus_sessions ----------
UPDATE focus_sessions SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE focus_sessions SET ended_at   = datetime(ended_at,   '+8 hours') WHERE ended_at   IS NOT NULL;
UPDATE focus_sessions SET started_at  = datetime(started_at,  '+8 hours') WHERE started_at  IS NOT NULL;

-- ---------- habit_records (completed_date 是 DATE 类型,跳过) ----------
UPDATE habit_records SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;

-- ---------- inventories ----------
UPDATE inventories SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE inventories SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- inventory_check_details ----------
UPDATE inventory_check_details SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE inventory_check_details SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- inventory_checks ----------
UPDATE inventory_checks SET check_date = datetime(check_date, '+8 hours') WHERE check_date IS NOT NULL;
UPDATE inventory_checks SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE inventory_checks SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- inventory_transactions ----------
UPDATE inventory_transactions SET created_at        = datetime(created_at,        '+8 hours') WHERE created_at        IS NOT NULL;
UPDATE inventory_transactions SET transaction_date  = datetime(transaction_date,  '+8 hours') WHERE transaction_date  IS NOT NULL;
UPDATE inventory_transactions SET updated_at        = datetime(updated_at,         '+8 hours') WHERE updated_at        IS NOT NULL;

-- ---------- knowledge_articles ----------
UPDATE knowledge_articles SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE knowledge_articles SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- knowledge_attachments ----------
UPDATE knowledge_attachments SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;

-- ---------- knowledge_categories ----------
UPDATE knowledge_categories SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE knowledge_categories SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- knowledge_comments ----------
UPDATE knowledge_comments SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE knowledge_comments SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- knowledge_favorites ----------
UPDATE knowledge_favorites SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;

-- ---------- knowledge_links ----------
UPDATE knowledge_links SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;

-- ---------- knowledge_read_records ----------
UPDATE knowledge_read_records SET read_at = datetime(read_at, '+8 hours') WHERE read_at IS NOT NULL;

-- ---------- knowledge_shares ----------
UPDATE knowledge_shares SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE knowledge_shares SET expire_at = datetime(expire_at, '+8 hours') WHERE expire_at IS NOT NULL;

-- ---------- knowledge_tags ----------
UPDATE knowledge_tags SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;

-- ---------- knowledge_versions ----------
UPDATE knowledge_versions SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;

-- ---------- leave_applications ----------
UPDATE leave_applications SET approved_at = datetime(approved_at, '+8 hours') WHERE approved_at IS NOT NULL;
UPDATE leave_applications SET created_at  = datetime(created_at,  '+8 hours') WHERE created_at  IS NOT NULL;
UPDATE leave_applications SET end_date    = datetime(end_date,    '+8 hours') WHERE end_date    IS NOT NULL;
UPDATE leave_applications SET start_date  = datetime(start_date,  '+8 hours') WHERE start_date  IS NOT NULL;
UPDATE leave_applications SET updated_at  = datetime(updated_at,  '+8 hours') WHERE updated_at  IS NOT NULL;

-- ---------- locations ----------
UPDATE locations SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE locations SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- material_categories ----------
UPDATE material_categories SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE material_categories SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- material_relationships ----------
UPDATE material_relationships SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE material_relationships SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- materials ----------
UPDATE materials SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE materials SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- notifications ----------
UPDATE notifications SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE notifications SET read_at   = datetime(read_at,   '+8 hours') WHERE read_at   IS NOT NULL;

-- ---------- overtime_applications (start_time/end_time 是 VARCHAR 纯时间,跳过) ----------
UPDATE overtime_applications SET approved_at = datetime(approved_at, '+8 hours') WHERE approved_at IS NOT NULL;
UPDATE overtime_applications SET created_at  = datetime(created_at,  '+8 hours') WHERE created_at  IS NOT NULL;
UPDATE overtime_applications SET date        = datetime(date,        '+8 hours') WHERE date        IS NOT NULL;
UPDATE overtime_applications SET updated_at  = datetime(updated_at,  '+8 hours') WHERE updated_at  IS NOT NULL;

-- ---------- permission_templates ----------
UPDATE permission_templates SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE permission_templates SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- personal_settings ----------
UPDATE personal_settings SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE personal_settings SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- personal_tasks (due_date/scheduled_date/scheduled_time 是 VARCHAR,跳过) ----------
UPDATE personal_tasks SET completed_at = datetime(completed_at, '+8 hours') WHERE completed_at IS NOT NULL;
UPDATE personal_tasks SET created_at  = datetime(created_at,  '+8 hours') WHERE created_at  IS NOT NULL;
UPDATE personal_tasks SET started_at   = datetime(started_at,   '+8 hours') WHERE started_at   IS NOT NULL;
UPDATE personal_tasks SET updated_at  = datetime(updated_at,  '+8 hours') WHERE updated_at  IS NOT NULL;

-- ---------- plan_templates ----------
UPDATE plan_templates SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE plan_templates SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- positions ----------
UPDATE positions SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE positions SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- project_logs (start_date/end_date 是 DATE,跳过) ----------
UPDATE project_logs SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE project_logs SET logged_at  = datetime(logged_at,  '+8 hours') WHERE logged_at  IS NOT NULL;
UPDATE project_logs SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- project_members ----------
UPDATE project_members SET join_date = datetime(join_date, '+8 hours') WHERE join_date IS NOT NULL;

-- ---------- projects ----------
UPDATE projects SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE projects SET end_date   = datetime(end_date,   '+8 hours') WHERE end_date   IS NOT NULL;
UPDATE projects SET start_date = datetime(start_date, '+8 hours') WHERE start_date IS NOT NULL;
UPDATE projects SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- rd_kanban_attachments ----------
UPDATE rd_kanban_attachments SET uploaded_at = datetime(uploaded_at, '+8 hours') WHERE uploaded_at IS NOT NULL;

-- ---------- rd_kanban_comments ----------
UPDATE rd_kanban_comments SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE rd_kanban_comments SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- rd_kanban_items ----------
UPDATE rd_kanban_items SET created_at   = datetime(created_at,   '+8 hours') WHERE created_at   IS NOT NULL;
UPDATE rd_kanban_items SET due_at       = datetime(due_at,       '+8 hours') WHERE due_at       IS NOT NULL;
UPDATE rd_kanban_items SET resolved_at  = datetime(resolved_at,  '+8 hours') WHERE resolved_at  IS NOT NULL;
UPDATE rd_kanban_items SET updated_at   = datetime(updated_at,   '+8 hours') WHERE updated_at   IS NOT NULL;

-- ---------- requirement_comments ----------
UPDATE requirement_comments SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;

-- ---------- requirement_documents ----------
UPDATE requirement_documents SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE requirement_documents SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- requirement_items ----------
UPDATE requirement_items SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE requirement_items SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- requirement_links ----------
UPDATE requirement_links SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;

-- ---------- requirement_versions ----------
UPDATE requirement_versions SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;

-- ---------- review_records ----------
UPDATE review_records SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE review_records SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- risks (closed_date/due_date/identified_date/resolved_date 是 DATE,跳过) ----------
UPDATE risks SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE risks SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- serial_numbers ----------
UPDATE serial_numbers SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE serial_numbers SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- shift_schedules (start_time/end_time 是 VARCHAR 纯时间,跳过) ----------
UPDATE shift_schedules SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE shift_schedules SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- tasks ----------
UPDATE tasks SET completed_at = datetime(completed_at, '+8 hours') WHERE completed_at IS NOT NULL;
UPDATE tasks SET created_at   = datetime(created_at,   '+8 hours') WHERE created_at   IS NOT NULL;
UPDATE tasks SET due_date     = datetime(due_date,     '+8 hours') WHERE due_date     IS NOT NULL;
UPDATE tasks SET start_date   = datetime(start_date,   '+8 hours') WHERE start_date   IS NOT NULL;
UPDATE tasks SET updated_at   = datetime(updated_at,   '+8 hours') WHERE updated_at   IS NOT NULL;

-- ---------- test_case_requirement_links ----------
UPDATE test_case_requirement_links SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;

-- ---------- test_cases ----------
UPDATE test_cases SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE test_cases SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- test_executions ----------
UPDATE test_executions SET completed_at = datetime(completed_at, '+8 hours') WHERE completed_at IS NOT NULL;
UPDATE test_executions SET created_at   = datetime(created_at,   '+8 hours') WHERE created_at   IS NOT NULL;
UPDATE test_executions SET started_at   = datetime(started_at,   '+8 hours') WHERE started_at   IS NOT NULL;
UPDATE test_executions SET updated_at   = datetime(updated_at,   '+8 hours') WHERE updated_at   IS NOT NULL;

-- ---------- test_results ----------
UPDATE test_results SET created_at   = datetime(created_at,   '+8 hours') WHERE created_at   IS NOT NULL;
UPDATE test_results SET executed_at  = datetime(executed_at,  '+8 hours') WHERE executed_at  IS NOT NULL;
UPDATE test_results SET updated_at   = datetime(updated_at,   '+8 hours') WHERE updated_at   IS NOT NULL;

-- ---------- test_steps ----------
UPDATE test_steps SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE test_steps SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- test_suites ----------
UPDATE test_suites SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE test_suites SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- user_shifts ----------
UPDATE user_shifts SET created_at      = datetime(created_at,      '+8 hours') WHERE created_at      IS NOT NULL;
UPDATE user_shifts SET effective_date  = datetime(effective_date,  '+8 hours') WHERE effective_date  IS NOT NULL;
UPDATE user_shifts SET expire_date     = datetime(expire_date,     '+8 hours') WHERE expire_date     IS NOT NULL;
UPDATE user_shifts SET updated_at      = datetime(updated_at,      '+8 hours') WHERE updated_at      IS NOT NULL;

-- ---------- users ----------
UPDATE users SET birthday      = datetime(birthday,      '+8 hours') WHERE birthday      IS NOT NULL;
UPDATE users SET created_at    = datetime(created_at,    '+8 hours') WHERE created_at    IS NOT NULL;
UPDATE users SET last_activity = datetime(last_activity, '+8 hours') WHERE last_activity IS NOT NULL;
UPDATE users SET last_login    = datetime(last_login,   '+8 hours') WHERE last_login    IS NOT NULL;
UPDATE users SET updated_at    = datetime(updated_at,    '+8 hours') WHERE updated_at    IS NOT NULL;

-- ---------- warehouses ----------
UPDATE warehouses SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE warehouses SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- work_calendar ----------
UPDATE work_calendar SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE work_calendar SET date       = datetime(date,       '+8 hours') WHERE date       IS NOT NULL;
UPDATE work_calendar SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

-- ---------- work_logs ----------
UPDATE work_logs SET created_at = datetime(created_at, '+8 hours') WHERE created_at IS NOT NULL;
UPDATE work_logs SET log_date   = datetime(log_date,   '+8 hours') WHERE log_date   IS NOT NULL;
UPDATE work_logs SET updated_at = datetime(updated_at, '+8 hours') WHERE updated_at IS NOT NULL;

COMMIT;

-- ============================================================
-- 验证修正结果(可选,执行后查看输出)
-- ============================================================
-- 检查打卡时间是否已转为北京时间:
--   sqlite3 "d:\topo_system\backend\instance\topo_system.db" "SELECT clock_in_time FROM attendance_records WHERE clock_in_time IS NOT NULL LIMIT 5;"
-- 检查用户最后登录时间:
--   sqlite3 "d:\topo_system\backend\instance\topo_system.db" "SELECT username, last_login FROM users WHERE last_login IS NOT NULL LIMIT 5;"
-- 检查 Bug 创建时间:
--   sqlite3 "d:\topo_system\backend\instance\topo_system.db" "SELECT id, created_at FROM bugs LIMIT 5;"
