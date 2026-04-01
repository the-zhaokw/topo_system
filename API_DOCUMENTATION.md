# API 文档

本文档详细说明TOPO系统的RESTful API接口。

## 基础信息

### 基础URL
```
http://localhost:5000/api/v1
```

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

## 认证相关API

### 用户登录

**Endpoint**: `POST /auth/login`

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

**Endpoint**: `POST /auth/register`

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

## 项目管理API

### 获取项目列表

**Endpoint**: `GET /projects`

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

**Endpoint**: `GET /projects/{id}`

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

**Endpoint**: `POST /projects`

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

**Endpoint**: `DELETE /projects/{id}`

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

**Endpoint**: `GET /users/{id}`

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

**Endpoint**: `POST /import/projects`

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

## 错误代码说明

| 错误代码 | 描述 | 解决方案 |
|---------|------|----------|
| `AUTH_001` | 未提供认证Token | 检查请求头是否包含Authorization |
| `AUTH_002` | Token已过期 | 重新登录获取新Token |
| `AUTH_003` | Token无效 | 检查Token格式是否正确 |
| `PERM_001` | 权限不足 | 检查用户角色是否有操作权限 |
| `DATA_001` | 数据不存在 | 检查请求的ID是否存在 |
| `DATA_002` | 数据验证失败 | 检查请求参数是否符合要求 |
| `FILE_001` | 文件大小超限 | 检查文件是否超过16MB限制 |
| `FILE_002` | 文件类型不支持 | 检查文件格式是否被允许 |

## 使用示例

### Python 示例

```python
import requests

# 登录获取Token
login_data = {
    "username": "admin",
    "password": "admin123"
}

response = requests.post("http://localhost:5000/api/v1/auth/login", json=login_data)
token = response.json()["data"]["access_token"]

# 设置请求头
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 获取项目列表
response = requests.get("http://localhost:5000/api/v1/projects", headers=headers)
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

response = requests.post("http://localhost:5000/api/v1/bugs", json=bug_data, headers=headers)
print(response.json())
```

### JavaScript 示例

```javascript
// 登录获取Token
const login = async () => {
    const response = await fetch('http://localhost:5000/api/v1/auth/login', {
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
    const response = await fetch('http://localhost:5000/api/v1/projects', {
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

**API版本**: v1.0  
**最后更新**: 2025年11月  
**基础URL**: http://localhost:5000/api/v1