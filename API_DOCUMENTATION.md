# API 文档

本文档详细说明TOPO系统的RESTful API接口。

## 基础信息

### 基础URL
```
http://localhost:5000/api
```

> 实际部署的 API 路径前缀为 `/api`（不再使用 `/v1`），所有模块在 `backend/api/` 下以 Flask 蓝图形式注册。

### 认证方式
所有API请求（除登录注册外）都需要在Header中包含JWT Token：
```
Authorization: Bearer <your_jwt_token>
```

### 响应格式
所有API响应都使用JSON格式：
```json
{
    "success": true,
    "message": "操作成功",
    "data": {}
}
```

### 错误处理
错误响应格式：
```json
{
    "success": false,
    "error": "错误描述",
    "code": "错误代码"
}
```

### 通用接口
- `GET /health` - 服务存活检查（无 `/api` 前缀）
- `GET /api/health` - 健康检查

## 认证相关API

### 用户登录

**Endpoint**: `POST /api/auth/login`

**请求参数**:
```json
{
    "username": "admin",
    "password": "admin123"
}
```

**响应示例**:
```json
{
    "success": true,
    "message": "登录成功",
    "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "user": {
            "id": 1,
            "username": "admin",
            "email": "admin@example.com",
            "role": "admin"
        }
    }
}
```

### 用户注册

**Endpoint**: `POST /api/auth/register`

**请求参数**:
```json
{
    "username": "newuser",
    "password": "password123",
    "email": "newuser@example.com",
    "role": "developer"
}
```

**响应示例**:
```json
{
    "success": true,
    "message": "用户注册成功",
    "data": {
        "id": 5,
        "username": "newuser",
        "email": "newuser@example.com",
        "role": "developer"
    }
}
```

### 获取当前用户信息

**Endpoint**: `GET /api/auth/me`

**响应示例**:
```json
{
    "success": true,
    "data": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "role": "admin",
        "is_super_admin": true
    }
}
```

### 更新当前用户信息

**Endpoint**: `PUT /api/auth/me`

## 用户管理API

> 所有用户管理接口前缀为 `/api/users`。

### 用户列表

**Endpoint**: `GET /api/users`

**查询参数**:
- `page` / `per_page` - 分页
- `role` - 角色筛选
- `department` - 部门筛选
- `search` - 用户名/姓名搜索

### 创建用户

**Endpoint**: `POST /api/users`

### 用户详情 / 更新 / 删除

- `GET    /api/users/{id}` - 详情
- `PUT    /api/users/{id}` - 更新
- `DELETE /api/users/{id}` - 删除
- `PUT    /api/users/{id}/status` - 启用/停用
- `POST   /api/users/{id}/reset-password` - 重置密码
- `POST   /api/users/{id}/activity` - 记录活动

### 用户主页聚合数据

**Endpoint**: `GET /api/users/{id}/home`

### 搜索用户

**Endpoint**: `GET /api/users/search?q=keyword`

### 获取审批人列表

**Endpoint**: `GET /api/users/approvers`

### 批量操作

- `POST /api/users/batch-delete` - 批量删除
- `POST /api/users/batch-update-role` - 批量修改角色

### 导入/导出

- `GET  /api/users/export/{format}` - 导出（CSV/Excel）
- `POST /api/users/import` - 导入用户

### 部门管理

- `GET    /api/users/departments` - 部门列表
- `POST   /api/users/departments` - 新建部门
- `PUT    /api/users/departments/{name}` - 更新部门
- `DELETE /api/users/departments/{name}` - 删除部门
- `GET    /api/users/department/{name}/members` - 部门成员
- `POST   /api/users/departments/{name}/members/batch-add` - 批量添加
- `POST   /api/users/departments/{name}/members/batch-remove` - 批量移除

### 职位管理

- `GET    /api/users/positions` - 职位列表
- `POST   /api/users/positions` - 新建职位
- `PUT    /api/users/positions/{name}` - 更新
- `DELETE /api/users/positions/{name}` - 删除
- `GET    /api/users/position/{name}/members` - 职位成员

### 我的部门

**Endpoint**: `GET /api/users/my-department`

### 模块权限管理（v1.6 新增）

- `GET  /api/users/module-permissions/catalog` - 模块权限目录（项目、Bug、考勤等）
- `GET  /api/users/module-permissions/users` - 用户的模块权限
- `GET  /api/users/{id}/module-permissions` - 指定用户的模块权限
- `PUT  /api/users/{id}/module-permissions` - 设置用户的模块权限
- `POST /api/users/{id}/module-permissions/reset` - 重置为默认

**请求参数**:
```json
{
    "permissions": {
        "module:project": true,
        "module:bug": true,
        "module:attendance": false
    }
}
```

### 权限模板管理（v1.6 新增）

- `GET    /api/users/permission-templates` - 模板列表
- `GET    /api/users/permission-templates/{id}` - 模板详情
- `POST   /api/users/permission-templates` - 新建模板
- `PUT    /api/users/permission-templates/{id}` - 更新模板
- `DELETE /api/users/permission-templates/{id}` - 删除模板
- `POST   /api/users/permission-templates/{id}/apply` - 应用到一批用户

### 用户权限码

- `GET  /api/users/permissions` - 系统权限码列表
- `GET  /api/users/{id}/permissions` - 用户的权限码
- `PUT  /api/users/{id}/permissions` - 更新用户权限码

## 项目管理API

> 实际路径前缀为 `/api/projects`。

### 获取项目列表

**Endpoint**: `GET /api/projects`

**查询参数**:
- `page` (可选): 页码，默认1
- `per_page` (可选): 每页数量，默认10
- `status` (可选): 项目状态筛选
- `search` (可选): 项目名称搜索

**响应示例**:
```json
{
    "success": true,
    "message": "获取项目列表成功",
    "data": {
        "projects": [
            {
                "id": 1,
                "name": "示例项目",
                "description": "系统功能演示和培训用项目",
                "status": "active",
                "manager": {
                    "id": 2,
                    "username": "project_manager"
                },
                "members": [
                    {"id": 3, "username": "developer1", "role": "developer"},
                    {"id": 4, "username": "tester1", "role": "tester"}
                ],
                "created_at": "2025-11-26T10:00:00Z",
                "updated_at": "2025-11-26T10:00:00Z"
            }
        ],
        "total": 10,
        "page": 1,
        "per_page": 10,
        "pages": 1
    }
}
```

### 获取单个项目

**Endpoint**: `GET /api/projects/{id}`

**响应示例**:
```json
{
    "success": true,
    "message": "获取项目详情成功",
    "data": {
        "id": 1,
        "name": "示例项目",
        "description": "系统功能演示和培训用项目",
        "status": "active",
        "manager": {
            "id": 2,
            "username": "project_manager",
            "email": "manager@example.com"
        },
        "members": [
            {
                "id": 3,
                "username": "developer1",
                "email": "dev1@example.com",
                "role": "developer"
            }
        ],
        "bug_count": 15,
        "open_bugs": 5,
        "created_at": "2025-11-26T10:00:00Z",
        "updated_at": "2025-11-26T10:00:00Z"
    }
}
```

### 创建项目

**Endpoint**: `POST /api/projects`

**请求参数**:
```json
{
    "name": "新项目",
    "description": "项目描述",
    "status": "active",
    "manager_id": 2,
    "member_ids": [3, 4]
}
```

**响应示例**:
```json
{
    "success": true,
    "message": "项目创建成功",
    "data": {
        "id": 11,
        "name": "新项目",
        "description": "项目描述",
        "status": "active",
        "created_at": "2025-11-26T10:00:00Z"
    }
}
```

### 更新项目

**Endpoint**: `PUT /projects/{id}`

**请求参数**:
```json
{
    "name": "更新后的项目名",
    "description": "更新后的描述",
    "status": "inactive",
    "manager_id": 3,
    "member_ids": [4, 5]
}
```

**响应示例**:
```json
{
    "success": true,
    "message": "项目更新成功",
    "data": {
        "id": 1,
        "name": "更新后的项目名",
        "description": "更新后的描述",
        "status": "inactive",
        "updated_at": "2025-11-26T11:00:00Z"
    }
}
```

### 删除项目

**Endpoint**: `DELETE /api/projects/{id}`

**响应示例**:
```json
{
    "success": true,
    "message": "项目删除成功",
    "data": null
}
```

## Bug管理API

### 获取Bug列表

**Endpoint**: `GET /bugs`

**查询参数**:
- `page` (可选): 页码，默认1
- `per_page` (可选): 每页数量，默认10
- `status` (可选): Bug状态筛选
- `severity` (可选): 严重程度筛选
- `priority` (可选): 优先级筛选
- `project_id` (可选): 项目ID筛选
- `assignee_id` (可选): 分配人ID筛选
- `search` (可选): Bug标题搜索

**响应示例**:
```json
{
    "success": true,
    "message": "获取Bug列表成功",
    "data": {
        "bugs": [
            {
                "id": 1,
                "title": "用户登录失败",
                "description": "输入正确密码后提示登录失败",
                "severity": "high",
                "priority": "high",
                "status": "open",
                "project": {
                    "id": 1,
                    "name": "示例项目"
                },
                "assignee": {
                    "id": 3,
                    "username": "developer1"
                },
                "reporter": {
                    "id": 4,
                    "username": "tester1"
                },
                "created_at": "2025-11-26T10:00:00Z",
                "updated_at": "2025-11-26T10:00:00Z"
            }
        ],
        "total": 50,
        "page": 1,
        "per_page": 10,
        "pages": 5
    }
}
```

### 获取单个Bug

**Endpoint**: `GET /bugs/{id}`

**响应示例**:
```json
{
    "success": true,
    "message": "获取Bug详情成功",
    "data": {
        "id": 1,
        "title": "用户登录失败",
        "description": "输入正确密码后提示登录失败",
        "severity": "high",
        "priority": "high",
        "status": "open",
        "steps_to_reproduce": "1. 打开登录页面\n2. 输入用户名和密码\n3. 点击登录按钮",
        "expected_result": "成功登录系统",
        "actual_result": "提示登录失败",
        "attachments": [
            {
                "id": 1,
                "filename": "login_error.png",
                "url": "/uploads/bugs/1/login_error.png"
            }
        ],
        "comments": [
            {
                "id": 1,
                "content": "这个问题需要尽快修复",
                "author": {
                    "id": 2,
                    "username": "project_manager"
                },
                "created_at": "2025-11-26T10:30:00Z"
            }
        ],
        "project": {
            "id": 1,
            "name": "示例项目"
        },
        "assignee": {
            "id": 3,
            "username": "developer1",
            "email": "dev1@example.com"
        },
        "reporter": {
            "id": 4,
            "username": "tester1",
            "email": "tester1@example.com"
        },
        "created_at": "2025-11-26T10:00:00Z",
        "updated_at": "2025-11-26T10:30:00Z"
    }
}
```

### 创建Bug

**Endpoint**: `POST /bugs`

**请求参数**:
```json
{
    "title": "新Bug标题",
    "description": "Bug详细描述",
    "severity": "medium",
    "priority": "high",
    "status": "open",
    "project_id": 1,
    "assignee_id": 3,
    "steps_to_reproduce": "重现步骤",
    "expected_result": "期望结果",
    "actual_result": "实际结果"
}
```

**响应示例**:
```json
{
    "success": true,
    "message": "Bug创建成功",
    "data": {
        "id": 51,
        "title": "新Bug标题",
        "description": "Bug详细描述",
        "severity": "medium",
        "priority": "high",
        "status": "open",
        "created_at": "2025-11-26T12:00:00Z"
    }
}
```

### 更新Bug

**Endpoint**: `PUT /bugs/{id}`

**请求参数**:
```json
{
    "title": "更新后的Bug标题",
    "description": "更新后的描述",
    "severity": "high",
    "priority": "medium",
    "status": "in_progress",
    "assignee_id": 4
}
```

**响应示例**:
```json
{
    "success": true,
    "message": "Bug更新成功",
    "data": {
        "id": 1,
        "title": "更新后的Bug标题",
        "description": "更新后的描述",
        "severity": "high",
        "priority": "medium",
        "status": "in_progress",
        "updated_at": "2025-11-26T12:30:00Z"
    }
}
```

### 删除Bug

**Endpoint**: `DELETE /bugs/{id}`

**响应示例**:
```json
{
    "success": true,
    "message": "Bug删除成功",
    "data": null
}
```

## 用户管理API

### 获取用户列表

**Endpoint**: `GET /users`

**查询参数**:
- `page` (可选): 页码，默认1
- `per_page` (可选): 每页数量，默认10
- `role` (可选): 角色筛选
- `search` (可选): 用户名搜索

**响应示例**:
```json
{
    "success": true,
    "message": "获取用户列表成功",
    "data": {
        "users": [
            {
                "id": 1,
                "username": "admin",
                "email": "admin@example.com",
                "role": "admin",
                "created_at": "2025-11-26T09:00:00Z"
            }
        ],
        "total": 5,
        "page": 1,
        "per_page": 10,
        "pages": 1
    }
}
```

### 获取单个用户

**Endpoint**: `GET /api/users/{id}`

**响应示例**:
```json
{
    "success": true,
    "message": "获取用户详情成功",
    "data": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "role": "admin",
        "projects": [
            {
                "id": 1,
                "name": "示例项目",
                "role": "manager"
            }
        ],
        "created_at": "2025-11-26T09:00:00Z"
    }
}
```

### 更新用户信息

**Endpoint**: `PUT /users/{id}`

**请求参数**:
```json
{
    "email": "newemail@example.com",
    "role": "developer"
}
```

**响应示例**:
```json
{
    "success": true,
    "message": "用户信息更新成功",
    "data": {
        "id": 1,
        "username": "admin",
        "email": "newemail@example.com",
        "role": "developer",
        "updated_at": "2025-11-26T13:00:00Z"
    }
}
```

## 统计信息API

### 获取项目统计

**Endpoint**: `GET /stats/projects`

**响应示例**:
```json
{
    "success": true,
    "message": "获取项目统计成功",
    "data": {
        "total_projects": 10,
        "active_projects": 7,
        "inactive_projects": 2,
        "completed_projects": 1,
        "projects_by_status": [
            {"status": "active", "count": 7},
            {"status": "inactive", "count": 2},
            {"status": "completed", "count": 1}
        ]
    }
}
```

### 获取Bug统计

**Endpoint**: `GET /stats/bugs`

**响应示例**:
```json
{
    "success": true,
    "message": "获取Bug统计成功",
    "data": {
        "total_bugs": 50,
        "open_bugs": 15,
        "in_progress_bugs": 10,
        "resolved_bugs": 20,
        "closed_bugs": 5,
        "bugs_by_severity": [
            {"severity": "low", "count": 10},
            {"severity": "medium", "count": 25},
            {"severity": "high", "count": 12},
            {"severity": "critical", "count": 3}
        ],
        "bugs_by_priority": [
            {"priority": "low", "count": 15},
            {"priority": "medium", "count": 20},
            {"priority": "high", "count": 15}
        ]
    }
}
```

## 导入导出API

### 导出项目数据

**Endpoint**: `GET /export/projects`

**查询参数**:
- `format` (可选): 导出格式，支持 `csv` 或 `excel`，默认 `csv`

**响应示例**:
返回文件下载流

### 导出Bug数据

**Endpoint**: `GET /export/bugs`

**查询参数**:
- `format` (可选): 导出格式，支持 `csv` 或 `excel`，默认 `csv`
- `project_id` (可选): 按项目导出
- `status` (可选): 按状态导出

**响应示例**:
返回文件下载流

### 导入项目数据

**Endpoint**: `POST /api/data/import/projects`

**请求参数**:
- `file` (必需): 上传的文件（CSV或Excel格式）

**响应示例**:
```json
{
    "success": true,
    "message": "项目数据导入成功",
    "data": {
        "imported_count": 5,
        "failed_count": 0,
        "failed_items": []
    }
}
```

## 文件上传API

### 上传附件

**Endpoint**: `POST /upload/attachment`

**请求参数**:
- `file` (必需): 上传的文件
- `bug_id` (可选): 关联的Bug ID

**响应示例**:
```json
{
    "success": true,
    "message": "文件上传成功",
    "data": {
        "filename": "screenshot.png",
        "url": "/uploads/bugs/1/screenshot.png",
        "size": 102400,
        "mime_type": "image/png"
    }
}
```

## 个人计划API

### 获取任务列表

**Endpoint**: `GET /personal-plan/tasks`

**查询参数**:
- `status` (可选): 任务状态筛选 (inbox/active/done)
- `quadrant` (可选): 四象限编号 (1/2/3/4)
- `tag` (可选): 标签筛选
- `date_from` (可选): 开始日期
- `date_to` (可选): 结束日期
- `is_habit` (可选): 是否为习惯

**响应示例**:
```json
{
    "success": true,
    "data": {
        "tasks": [
            {
                "id": 1,
                "title": "完成任务标题",
                "status": "todo",
                "priority": "high",
                "quadrant": 2,
                "scheduled_date": "2026-04-10",
                "scheduled_time": "14:00",
                "estimated_minutes": 30,
                "tags": "work,important",
                "is_habit": false
            }
        ],
        "total": 10
    }
}
```

### 创建任务

**Endpoint**: `POST /personal-plan/tasks`

**请求参数**:
```json
{
    "content": "任务内容",
    "description": "任务描述",
    "priority": "high",
    "scheduled_date": "2026-04-10",
    "scheduled_time": "14:00",
    "estimated_minutes": 30,
    "tags": "work",
    "is_habit": false
}
```

### 获取四象限任务

**Endpoint**: `GET /api/personal-plan/tasks/quadrant`

**响应示例**:
```json
{
    "success": true,
    "data": {
        "1": [{"id": 1, "title": "紧急且重要", "priority": "urgent"}],
        "2": [{"id": 2, "title": "重要不紧急", "priority": "high"}],
        "3": [{"id": 3, "title": "紧急不重要", "priority": "medium"}],
        "4": [{"id": 4, "title": "不紧急不重要", "priority": "low"}]
    }
}
```

### 获取日历事件

**Endpoint**: `GET /personal-plan/calendar/events`

**查询参数**:
- `date_from` (可选): 开始日期
- `date_to` (可选): 结束日期

### 开始专注

**Endpoint**: `POST /personal-plan/focus/start`

**请求参数**:
```json
{
    "task_id": 1,
    "focus_type": "pomodoro",
    "duration": 25
}
```

### 获取专注统计

**Endpoint**: `GET /personal-plan/focus/stats`

**响应示例**:
```json
{
    "success": true,
    "data": {
        "total_minutes": 350,
        "completed_sessions": 14,
        "pomodoro_count": 10,
        "total_sessions": 15
    }
}
```

### 获取习惯列表

**Endpoint**: `GET /personal-plan/habits`

**响应示例**:
```json
{
    "success": true,
    "data": [
        {
            "task": {"id": 1, "title": "每日阅读", "is_habit": true},
            "streak": 7,
            "total_completions": 30
        }
    ]
}
```

## 风险管理API

### 获取风险列表

**Endpoint**: `GET /risks`

**查询参数**:
- `project_id` (可选): 项目ID筛选
- `risk_type` (可选): 风险类型 (risk/issue)
- `status` (可选): 状态筛选
- `level` (可选): 等级筛选
- `priority` (可选): 优先级筛选
- `page` (可选): 页码，默认1

**响应示例**:
```json
{
    "success": true,
    "data": {
        "risks": [
            {
                "id": 1,
                "title": "技术风险",
                "risk_type": "risk",
                "status": "identified",
                "level": "high",
                "priority": "high",
                "probability": 0.7,
                "impact": 0.8,
                "exposure": 0.56
            }
        ],
        "total": 10,
        "page": 1,
        "pages": 1
    }
}
```

### 创建风险/问题

**Endpoint**: `POST /api/risks`

**请求参数**:
```json
{
    "project_id": 1,
    "title": "风险标题",
    "description": "风险描述",
    "risk_type": "risk",
    "status": "identified",
    "priority": "high",
    "level": "high",
    "category": "technical",
    "probability": 0.7,
    "impact": 0.8,
    "mitigation_strategy": "缓解策略",
    "contingency_plan": "应急预案"
}
```

### 获取风险矩阵

**Endpoint**: `GET /risks/matrix`

**响应示例**:
```json
{
    "success": true,
    "data": {
        "critical_high": [],
        "critical_medium": [],
        "high_high": [{"id": 1, "title": "高风险项", "exposure": 0.9}],
        "high_medium": [],
        "medium_high": [],
        "medium_medium": [],
        "low_low": []
    }
}
```

### 获取风险统计

**Endpoint**: `GET /api/risks/statistics`

**响应示例**:
```json
{
    "success": true,
    "data": {
        "total": 15,
        "open": 10,
        "resolved": 5,
        "high_risk": 3,
        "by_status": {"identified": 5, "analyzing": 3, "mitigating": 2},
        "by_level": {"high": 3, "medium": 8, "low": 4}
    }
}
```

## 知识库 API（v1.6 增强）

> 实际路径前缀为 `/api/knowledge`。

### 分类管理

- `GET    /api/knowledge/categories` - 分类列表
- `GET    /api/knowledge/categories/tree` - 树形结构
- `POST   /api/knowledge/categories` - 新建分类
- `GET    /api/knowledge/categories/{id}` - 分类详情
- `PUT    /api/knowledge/categories/{id}` - 更新分类
- `POST   /api/knowledge/categories/{id}/archive` - 归档分类
- `DELETE /api/knowledge/categories/{id}` - 删除分类
- `GET    /api/knowledge/categories/{id}/articles` - 分类下文章

### 文章管理

- `GET    /api/knowledge/articles` - 文章列表
- `GET    /api/knowledge/articles/my` - 我的文章
- `POST   /api/knowledge/articles` - 新建文章
- `GET    /api/knowledge/articles/{id}` - 文章详情
- `PUT    /api/knowledge/articles/{id}` - 更新文章
- `PUT    /api/knowledge/articles/{id}/status` - 变更状态
- `POST   /api/knowledge/articles/{id}/pin` - 置顶
- `DELETE /api/knowledge/articles/{id}` - 删除文章

### 互动

- `GET/POST /api/knowledge/articles/{id}/comments` - 评论列表/新增
- `DELETE /api/knowledge/articles/{id}/comments/{commentId}` - 删除评论
- `POST   /api/knowledge/articles/{id}/like` - 点赞
- `POST/DELETE /api/knowledge/articles/{id}/favorite` - 收藏/取消
- `GET    /api/knowledge/articles/{id}/related` - 关联文章

### 附件

- `POST   /api/knowledge/articles/{id}/attachments` - 上传附件
- `GET    /api/knowledge/articles/{id}/attachments/{attId}` - 下载附件
- `DELETE /api/knowledge/articles/{id}/attachments/{attId}` - 删除附件

### 批量操作

- `POST /api/knowledge/articles/batch/move` - 批量移动
- `POST /api/knowledge/articles/batch/status` - 批量状态变更
- `POST /api/knowledge/articles/batch/delete` - 批量删除

### 导出 & 分享

- `GET  /api/knowledge/articles/{id}/export/{type}` - 导出（md/pdf/word）
- `POST /api/knowledge/articles/{id}/shares` - 创建分享 Token
- `GET  /api/knowledge/articles/{id}/shares` - 分享列表
- `GET  /api/knowledge/enhanced/share/{token}` - 通过 Token 访问
- `GET  /api/knowledge/enhanced/share/{token}/download` - 下载分享文件
- `DELETE /api/knowledge/shares/{id}` - 取消分享

### 搜索 / 标签 / 统计

- `GET /api/knowledge/search?q=...` - 全文搜索
- `GET /api/knowledge/tags` - 标签云
- `GET /api/knowledge/statistics` - 知识库统计
- `GET /api/knowledge/stats` - 扩展统计

## 考勤管理 API（v1.6 增强）

> 实际路径前缀为 `/api/attendance`。

- `GET /api/attendance/work-calendar` - 工作日历
- `GET /api/attendance/records` - 考勤记录
- `GET /api/attendance/records/today` - 今日记录
- `GET /api/attendance/records/export` - 记录导出
- `POST /api/attendance/clock-in` - 上班打卡
- `POST /api/attendance/clock-out` - 下班打卡
- `GET /api/attendance/my-summary` - 我的考勤汇总
- `GET /api/attendance/exceptions` - 考勤异常
- `GET /api/attendance/statistics` - 考勤统计
- `GET/POST /api/attendance/leave-applications` - 请假申请
- `GET/POST /api/attendance/overtime-applications` - 加班申请
- `POST /api/attendance/overtime-applications/{id}/approve` - 加班审批
- `GET/POST/PUT/DELETE /api/attendance/shifts[...]` - 班次管理
- `GET/POST/DELETE /api/attendance/user-shifts[...]` - 用户班次
- `GET /api/attendance/reports/overview` - 概览报表
- `GET /api/attendance/reports/detail` - 明细报表
- `GET /api/attendance/reports/export` - 报表导出

## 需求管理 API（v1.6 增强）

> 实际路径前缀为 `/api/requirements`。

- 需求文档 CRUD：`/projects/{pid}/requirement-documents`
- 需求条目 CRUD：`/requirement-items`
- 状态变更、评论、关联、复制、移动、历史
- 版本管理：版本列表、创建版本、版本对比、版本回滚
- 追溯矩阵、覆盖率统计、影响分析
- 评审：文档评审、条目评审
- 我的需求待办：`/my/requirement-todos`
- 导出

## 测试管理 API（v1.6 增强）

> 实际路径前缀为 `/api/test-management`。

- 测试集 CRUD（树形、批量、版本历史）
- 测试用例 CRUD（步骤、评审、复制、批量、历史）
- 测试执行 CRUD
- 用例执行结果
- 需求-用例关联
- 统计：项目统计、报表
- 仪表板
- 用例导入/导出

## 合同管理 API

> 实际路径前缀为 `/api/contracts`。

- 合同 CRUD：`/api/contracts`
- 增强详情：`/api/contracts/enhanced/{id}`
- 合同审批：`/api/contracts/enhanced/{id}/approve`
- 增强统计：`/api/contracts/statistics/enhanced`
- 配送跟踪：`/api/contracts/delivery`

## 物料管理 API

> 实际路径前缀为 `/api/materials`。

- 物料主数据：CRUD
- 分类、仓库、库位、序列号、关系
- 库存操作：入库、出库、调拨、盘点
- 库存预警与报表
- 批量导入/导出

## 待办事项 API

> 实际路径前缀为 `/api/todos`。

- 任务/待办 CRUD、状态流转

## 工作日志 API

> 实际路径前缀为 `/api/work-logs`。

- 工作日志 CRUD、统计

## 项目日志 API

> 实际路径前缀为 `/api/project-logs`。

- 项目日志 CRUD

## 通知 API

> 实际路径前缀为 `/api/notifications`。

- 通知列表、未读/已读、全部已读

## 审计日志 API

> 实际路径前缀为 `/api/audit`、`/api/activities`。

- 审计日志列表、活动记录

## 系统监控 API

- `GET /api/monitoring` - 监控数据
- `GET /api/performance` - 性能指标
- `GET /api/health` - 健康检查
- `GET /health` - 存活检查

## 系统配置 API

> 实际路径前缀为 `/api/system`。

- `GET  /api/system/backup` - 备份列表
- `POST /api/system/backup` - 创建备份
- `GET  /api/system/config` - 系统配置
- `PUT  /api/system/config` - 更新系统配置

## 全局搜索 API

- `GET /api/search?q=keyword` - 全局搜索（项目、Bug、需求、用户、知识等）

## 数据导入导出 API

- `POST /api/data/import` - 批量导入
- `GET  /api/data/export` - 批量导出

## 错误代码说明

| 错误代码 | 描述 | 解决方案 |
|---------|------|----------|
| `AUTH_001` | 未提供认证Token | 检查请求头是否包含Authorization |
| `AUTH_002` | Token已过期 | 重新登录获取新Token |
| `AUTH_003` | Token无效 | 检查Token格式是否正确 |
| `PERM_001` | 权限不足 | 检查用户角色是否有操作权限 |
| `PERM_002` | 模块权限未授予 | 检查用户模块权限是否包含目标模块 |
| `DATA_001` | 数据不存在 | 检查请求的ID是否存在 |
| `DATA_002` | 数据验证失败 | 检查请求参数是否符合要求 |
| `FILE_001` | 文件大小超限 | 检查文件是否超过16MB限制 |
| `FILE_002` | 文件类型不支持 | 检查文件格式是否被允许 |
| `STATUS_001` | 状态流转不合法 | 检查工作流配置（Bug、合同、需求等） |

## 使用示例

### Python 示例

```python
import requests

# 登录获取Token
login_data = {
    "username": "admin",
    "password": "admin123"
}

response = requests.post("http://localhost:5000/api/auth/login", json=login_data)
token = response.json()["data"]["access_token"]

# 设置请求头
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 获取项目列表
response = requests.get("http://localhost:5000/api/projects", headers=headers)
projects = response.json()["data"]["projects"]

# 创建新Bug
bug_data = {
    "title": "API测试Bug",
    "description": "通过API创建的测试Bug",
    "severity": "medium",
    "priority": "high",
    "project_id": 1,
    "assignee_id": 3
}

response = requests.post("http://localhost:5000/api/bugs", json=bug_data, headers=headers)
print(response.json())
```

### JavaScript 示例

```javascript
// 登录获取Token
const login = async () => {
    const response = await fetch('http://localhost:5000/api/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: 'admin',
            password: 'admin123'
        })
    });

    const data = await response.json();
    return data.data.access_token;
};

// 获取项目列表
const getProjects = async (token) => {
    const response = await fetch('http://localhost:5000/api/projects', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    const data = await response.json();
    return data.data.projects;
};

// 使用示例
login().then(token => {
    getProjects(token).then(projects => {
        console.log(projects);
    });
});
```

---

**API版本**: v1.6.0
**最后更新**: 2026-06
**基础URL**: http://localhost:5000/api