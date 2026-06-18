# Bug管理系统数据库架构设计

## 1. 数据库概述

根据系统设计文档，设计符合需求的数据库架构，包含用户权限、项目管理、缺陷报告、任务管理等核心功能模块的数据模型。

## 2. 核心数据模型

### 2.1 用户表（users）

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'developer' NOT NULL,  -- admin, project_manager, developer, tester, guest
    avatar VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    employee_id VARCHAR(20),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    position VARCHAR(100),
    department VARCHAR(100),
    company_phone VARCHAR(20),
    mobile_phone VARCHAR(20),
    birthday DATE,
    gender VARCHAR(10),
    work_language VARCHAR(20)
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_is_active ON users(is_active);
```

### 2.2 项目表（projects）

```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id INTEGER NOT NULL,  -- 创建者ID
    status VARCHAR(20) DEFAULT '新建' NOT NULL,  -- 新建, 进行中, 已完成, 已关闭
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    start_date DATE,
    end_date DATE,
    progress INTEGER DEFAULT 0,  -- 项目进度（0-100）
    FOREIGN KEY (owner_id) REFERENCES users(id)
);

CREATE INDEX idx_projects_owner_id ON projects(owner_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_created_at ON projects(created_at);
```

### 2.3 项目成员表（project_members）

```sql
CREATE TABLE project_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role VARCHAR(20) DEFAULT 'member' NOT NULL,  -- member, admin, manager
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE (project_id, user_id)  -- 确保用户在项目中唯一
);

CREATE INDEX idx_project_members_project_id ON project_members(project_id);
CREATE INDEX idx_project_members_user_id ON project_members(user_id);
```

### 2.4 缺陷表（bugs）

```sql
CREATE TABLE bugs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) DEFAULT '新建' NOT NULL,  -- 新建, 已指派, 处理中, 已解决, 已验证, 已关闭, 已拒绝, 已重新打开
    priority VARCHAR(20) DEFAULT 'medium' NOT NULL,  -- low, medium, high, urgent
    severity VARCHAR(20) DEFAULT 'medium' NOT NULL,  -- low, medium, high, critical
    category VARCHAR(50),
    reporter_id INTEGER NOT NULL,  -- 报告者
    assignee_id INTEGER,  -- 处理者
    project_id INTEGER NOT NULL,
    resolver_id INTEGER,  -- 解决者
    verifier_id INTEGER,  -- 验证者
    version VARCHAR(50),
    tags TEXT,  -- JSON数组存储
    issue_type VARCHAR(50),  -- 问题类型
    reproduce_frequency VARCHAR(50),  -- 重现频率
    found_build VARCHAR(100),  -- 发现构建
    test_version VARCHAR(100),  -- 测试版本
    module VARCHAR(100),  -- 模块
    custom_category1 VARCHAR(100),  -- 自定义分类1
    customer_mr_number VARCHAR(100),  -- 客户MR编号
    agent VARCHAR(100),  -- 代理商
    plan_resolve_version VARCHAR(100),  -- 计划解决版本
    resolve_build VARCHAR(100),  -- 解决构建
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    due_date DATETIME,  -- 期限
    closed_at DATETIME,  -- 关闭时间
    assigned_at DATETIME,  -- 指派时间
    resolved_at DATETIME,  -- 解决时间
    FOREIGN KEY (reporter_id) REFERENCES users(id),
    FOREIGN KEY (assignee_id) REFERENCES users(id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (resolver_id) REFERENCES users(id),
    FOREIGN KEY (verifier_id) REFERENCES users(id)
);

CREATE INDEX idx_bugs_project_id ON bugs(project_id);
CREATE INDEX idx_bugs_status ON bugs(status);
CREATE INDEX idx_bugs_priority ON bugs(priority);
CREATE INDEX idx_bugs_severity ON bugs(severity);
CREATE INDEX idx_bugs_reporter_id ON bugs(reporter_id);
CREATE INDEX idx_bugs_assignee_id ON bugs(assignee_id);
CREATE INDEX idx_bugs_created_at ON bugs(created_at);
```

### 2.5 任务表（tasks）

```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    project_id INTEGER NOT NULL,
    owner_id INTEGER NOT NULL,  -- 创建者
    assignee_id INTEGER,  -- 负责人
    status VARCHAR(20) DEFAULT '新建' NOT NULL,  -- 新建, 进行中, 已完成, 已关闭
    priority VARCHAR(20) DEFAULT 'medium' NOT NULL,  -- low, medium, high, urgent
    progress INTEGER DEFAULT 0,  -- 进度（0-100）
    estimated_hours FLOAT,  -- 估计工时
    actual_hours FLOAT,  -- 实际工时
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    start_date DATE,
    due_date DATE,
    completed_at DATETIME,  -- 实际完成时间
    related_bug_id INTEGER,  -- 关联的缺陷ID
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (owner_id) REFERENCES users(id),
    FOREIGN KEY (assignee_id) REFERENCES users(id),
    FOREIGN KEY (related_bug_id) REFERENCES bugs(id)
);

CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_assignee_id ON tasks(assignee_id);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
CREATE INDEX idx_tasks_related_bug_id ON tasks(related_bug_id);
```

### 2.6 任务参与人表（task_participants）

```sql
CREATE TABLE task_participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE (task_id, user_id)
);

CREATE INDEX idx_task_participants_task_id ON task_participants(task_id);
CREATE INDEX idx_task_participants_user_id ON task_participants(user_id);
```

### 2.7 评论表（comments）

```sql
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bug_id INTEGER,
    task_id INTEGER,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bug_id) REFERENCES bugs(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_comments_bug_id ON comments(bug_id);
CREATE INDEX idx_comments_task_id ON comments(task_id);
CREATE INDEX idx_comments_user_id ON comments(user_id);
CREATE INDEX idx_comments_created_at ON comments(created_at);
```

### 2.8 活动日志表（activities）

```sql
CREATE TABLE activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bug_id INTEGER,
    task_id INTEGER,
    project_id INTEGER,
    user_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,  -- 操作类型
    old_value TEXT,  -- 旧值
    new_value TEXT,  -- 新值
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bug_id) REFERENCES bugs(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_activities_bug_id ON activities(bug_id);
CREATE INDEX idx_activities_task_id ON activities(task_id);
CREATE INDEX idx_activities_project_id ON activities(project_id);
CREATE INDEX idx_activities_user_id ON activities(user_id);
CREATE INDEX idx_activities_created_at ON activities(created_at);
```

### 2.9 审计日志表（audit_logs）

```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,  -- 操作类型
    resource_type VARCHAR(50) NOT NULL,  -- 资源类型
    resource_id INTEGER,
    details TEXT NOT NULL,  -- 详细操作信息
    ip_address VARCHAR(45),  -- IP地址
    user_agent TEXT,  -- 用户代理
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_resource_type ON audit_logs(resource_type);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
```

### 2.10 通知表（notifications）

```sql
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type VARCHAR(20) NOT NULL,  -- email, webhook, in_app
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    related_bug_id INTEGER,
    related_task_id INTEGER,
    related_project_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (related_bug_id) REFERENCES bugs(id),
    FOREIGN KEY (related_task_id) REFERENCES tasks(id),
    FOREIGN KEY (related_project_id) REFERENCES projects(id)
);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);
```

### 2.11 附件表（attachments）

```sql
CREATE TABLE attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bug_id INTEGER,
    task_id INTEGER,
    user_id INTEGER NOT NULL,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR(100),
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bug_id) REFERENCES bugs(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_attachments_bug_id ON attachments(bug_id);
CREATE INDEX idx_attachments_task_id ON attachments(task_id);
CREATE INDEX idx_attachments_user_id ON attachments(user_id);
```

## 3. 数据关系图

```
users 1:n projects
users 1:n project_members
projects 1:n project_members
projects 1:n bugs
projects 1:n tasks
users 1:n bugs (reporter, assignee, resolver, verifier)
users 1:n tasks (owner, assignee)
bugs 1:n comments
tasks 1:n comments
bugs 1:n activities
tasks 1:n activities
projects 1:n activities
users 1:n activities
users 1:n audit_logs
users 1:n notifications
bugs 1:n notifications
tasks 1:n notifications
projects 1:n notifications
bugs 1:n attachments
tasks 1:n attachments
users 1:n attachments
tasks 1:n task_participants
users 1:n task_participants
bugs 1:1 tasks (related_bug_id)
```

## 4. 数据库优化建议

1. **索引优化**：为频繁查询的字段创建索引，如状态、优先级、项目ID、用户ID等
2. **数据分区**：对于大型系统，可以考虑按时间范围对活动日志、审计日志等表进行分区
3. **缓存策略**：实现应用层缓存，减少数据库查询压力
4. **定期维护**：定期清理过期数据，优化表空间
5. **读写分离**：对于高并发系统，考虑实现读写分离架构

## 5. 数据安全考虑

1. **密码安全**：用户密码必须使用强哈希算法存储
2. **权限控制**：在应用层实现严格的权限控制
3. **数据备份**：定期进行数据备份，确保数据可恢复
4. **防止SQL注入**：使用参数化查询，避免SQL注入攻击
5. **数据脱敏**：对敏感信息进行脱敏处理

## 6. 扩展性设计

1. **模块化设计**：各功能模块数据模型相对独立
2. **自定义字段**：预留自定义字段，支持系统扩展
3. **标签系统**：使用标签系统增强数据分类能力
4. **版本管理**：支持数据变更的版本记录

## 7. 知识库模块（v1.6 增强）

### 7.1 知识分类表（knowledge_categories）

```sql
CREATE TABLE knowledge_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    parent_id INTEGER,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    article_count INTEGER DEFAULT 0,
    created_by INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES knowledge_categories(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE INDEX idx_knowledge_categories_parent_id ON knowledge_categories(parent_id);
```

### 7.2 知识文章表（knowledge_articles）

```sql
CREATE TABLE knowledge_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,           -- Markdown 内容
    summary TEXT,
    category_id INTEGER,
    author_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',  -- draft, published, archived, deprecated
    is_pinned BOOLEAN DEFAULT FALSE,    -- 置顶
    is_public BOOLEAN DEFAULT FALSE,    -- 是否对全员可见
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    favorite_count INTEGER DEFAULT 0,
    tags TEXT,                          -- JSON 数组
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    published_at DATETIME,
    FOREIGN KEY (category_id) REFERENCES knowledge_categories(id),
    FOREIGN KEY (author_id) REFERENCES users(id)
);

CREATE INDEX idx_knowledge_articles_category_id ON knowledge_articles(category_id);
CREATE INDEX idx_knowledge_articles_status ON knowledge_articles(status);
CREATE INDEX idx_knowledge_articles_pinned ON knowledge_articles(is_pinned);
```

### 7.3 知识收藏表（knowledge_favorites）

```sql
CREATE TABLE knowledge_favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    article_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (article_id) REFERENCES knowledge_articles(id) ON DELETE CASCADE,
    UNIQUE (user_id, article_id)
);
```

### 7.4 知识分享表（knowledge_shares）

```sql
CREATE TABLE knowledge_shares (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    share_token VARCHAR(64) UNIQUE NOT NULL,
    password_hash VARCHAR(255),           -- 可选密码保护
    expire_at DATETIME,                   -- NULL 表示永不过期
    access_count INTEGER DEFAULT 0,
    created_by INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES knowledge_articles(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE INDEX idx_knowledge_shares_token ON knowledge_shares(share_token);
```

## 8. 个人计划模块（v1.6 新增）

### 8.1 个人计划任务表（personal_plan_tasks）

```sql
CREATE TABLE personal_plan_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    quadrant INTEGER,                    -- 1-4 四象限
    priority VARCHAR(20) DEFAULT 'medium',  -- low, medium, high, urgent
    is_habit BOOLEAN DEFAULT FALSE,      -- 是否习惯
    habit_frequency VARCHAR(20),         -- daily, weekly
    due_date DATETIME,
    estimated_minutes INTEGER,           -- 预计耗时（分钟）
    actual_minutes INTEGER,              -- 实际专注时长
    status VARCHAR(20) DEFAULT 'pending',  -- pending, in_progress, done, cancelled
    source VARCHAR(50),                  -- inbox, manual, habit
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_personal_plan_tasks_user_id ON personal_plan_tasks(user_id);
CREATE INDEX idx_personal_plan_tasks_due_date ON personal_plan_tasks(due_date);
```

### 8.2 专注记录表（focus_sessions）

```sql
CREATE TABLE focus_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    task_id INTEGER,
    started_at DATETIME NOT NULL,
    ended_at DATETIME,
    duration_seconds INTEGER,
    is_pomodoro BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (task_id) REFERENCES personal_plan_tasks(id) ON DELETE SET NULL
);
```

### 8.3 习惯打卡表（habit_logs）

```sql
CREATE TABLE habit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    log_date DATE NOT NULL,
    note TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES personal_plan_tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE (task_id, log_date)
);
```

## 9. 风险与问题管理（v1.6 新增）

### 9.1 风险表（risks）

```sql
CREATE TABLE risks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    type VARCHAR(20) DEFAULT 'risk',    -- risk（风险）, issue（问题）
    status VARCHAR(20) DEFAULT 'identified',  -- identified, analyzing, mitigating, resolved, closed
    level VARCHAR(20) DEFAULT 'medium', -- low, medium, high, critical
    priority VARCHAR(20) DEFAULT 'medium',
    probability FLOAT,                   -- 0-1
    impact FLOAT,                        -- 0-1
    exposure FLOAT,                      -- 自动计算 = probability * impact
    mitigation_strategy TEXT,
    contingency_plan TEXT,
    owner_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (owner_id) REFERENCES users(id)
);

CREATE INDEX idx_risks_project_id ON risks(project_id);
CREATE INDEX idx_risks_status ON risks(status);
CREATE INDEX idx_risks_level ON risks(level);
```

### 9.2 风险关联表（risk_links）

```sql
CREATE TABLE risk_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    risk_id INTEGER NOT NULL,
    link_type VARCHAR(20) NOT NULL,    -- bug, task, risk
    link_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (risk_id) REFERENCES risks(id) ON DELETE CASCADE
);
```

## 10. 模块权限与权限模板（v1.6 新增）

### 10.1 用户模块权限表（user_module_permissions）

```sql
CREATE TABLE user_module_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    module_key VARCHAR(50) NOT NULL,  -- module:project, module:bug ...
    is_enabled BOOLEAN DEFAULT TRUE,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (user_id, module_key)
);

CREATE INDEX idx_user_module_permissions_user_id ON user_module_permissions(user_id);
```

### 10.2 权限模板表（permission_templates）

```sql
CREATE TABLE permission_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    permissions TEXT NOT NULL,         -- JSON：{ "module:project": true, ... }
    created_by INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

## 11. 合同增强（v1.6）

### 11.1 合同站点表（contract_sites）

```sql
CREATE TABLE contract_sites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL,
    site_name VARCHAR(200) NOT NULL,
    address TEXT,
    delivery_status VARCHAR(20) DEFAULT 'pending',  -- pending, partial, delivered
    delivery_date DATE,
    contact_person VARCHAR(50),
    contact_phone VARCHAR(20),
    notes TEXT,
    FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE
);
```

### 11.2 合同BOM表（contract_boms）

```sql
CREATE TABLE contract_boms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL,
    material_name VARCHAR(200) NOT NULL,
    model VARCHAR(100),
    quantity INTEGER NOT NULL,
    unit_price FLOAT,
    total_price FLOAT,
    remarks TEXT,
    FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE
);
```

### 11.3 合同付款条款（contract_payment_terms）

```sql
CREATE TABLE contract_payment_terms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL,
    stage_name VARCHAR(100) NOT NULL,
    percentage FLOAT NOT NULL,
    amount FLOAT,
    milestone TEXT,
    expected_date DATE,
    actual_date DATE,
    status VARCHAR(20) DEFAULT 'pending',
    FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE
);
```

### 11.4 知识产权条款（contract_ip_terms）

```sql
CREATE TABLE contract_ip_terms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL,
    background_ip TEXT,                 -- 背景IP说明
    foreground_ip TEXT,                 -- 前景IP说明
    license_terms TEXT,                 -- 许可条款
    FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE
);
```

## 12. 需求管理（v1.6 增强）

### 12.1 需求版本表（requirement_versions）

```sql
CREATE TABLE requirement_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requirement_id INTEGER NOT NULL,
    version_number INTEGER NOT NULL,
    content_snapshot TEXT,              -- JSON 快照
    change_summary TEXT,
    created_by INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (requirement_id) REFERENCES requirements(id) ON DELETE CASCADE
);
```

---

**版本**: v1.6.0
**最后更新**: 2026-06