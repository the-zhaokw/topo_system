# TOPO System - 开发环境搭建与调试指南

> 本文档合并自原 `VS_CODE_SETUP.md`（本地 VS Code 调试）与 `VSCODE_SERVER_SETUP.md`（远程 VS Code Server）。

---

## 一、本地开发环境（Windows + VS Code）

### 快速开始

#### 1. 打开项目
1. 启动 VS Code
2. 文件 → 打开文件夹
3. 选择 `D:\topo_system` 文件夹

#### 2. 安装推荐扩展
VS Code 会提示安装推荐的扩展，点击"全部安装"：
- Python (Microsoft)
- Pylance (Microsoft)
- Vue - Official (Vue.js)
- Prettier - Code formatter
- Debugpy (Microsoft)

或手动安装扩展 ID:
- ms-python.python
- ms-python.vscode-pylance
- Vue.volar
- esbenp.prettier-vscode

---

### 调试配置

#### 方式一：使用任务 (推荐)

**Ctrl+Shift+P** → **Tasks: Run Task**

| 任务 | 说明 |
|------|------|
| `Start Backend` | 启动 Flask 后端 (端口 5000) |
| `Start Frontend` | 启动 Vue 前端 (端口 3000) |
| `Install Backend Dependencies` | 安装 Python 依赖 |
| `Install Frontend Dependencies` | 安装 Node 依赖 |
| `Restart Backend` | 重启后端服务 |

#### 方式二：使用调试器

**F5** 或 **运行和调试** 面板

| 配置 | 说明 |
|------|------|
| `Python: Flask Backend` | 调试模式启动后端 |
| `Vue: Frontend Dev Server` | 启动前端并连接 Chrome 调试 |
| `Full Stack (Backend + Frontend)` | 同时启动前后端 |

#### 方式三：终端手动启动

**终端 1 - 后端**:
```bash
cd D:\topo_system\backend
python run_app.py
```

**终端 2 - 前端**:
```bash
cd D:\topo_system\vue-frontend
npm run dev
```

---

### 断点调试

#### Python 后端调试
1. 在 Python 代码中点击行号左侧添加断点
2. 选择 `Python: Flask Backend` 配置
3. 按 **F5** 启动调试
4. 访问 http://localhost:5000 触发断点

#### Vue 前端调试
1. 在 Vue 组件中点击行号左侧添加断点
2. 选择 `Vue: Frontend Dev Server` 配置
3. 按 **F5** 启动调试
4. 在浏览器中操作触发断点

---

### 常用调试场景

#### 1. 调试 API 接口
```python
# backend/api/bugs.py
@bugs_bp.route('/<int:bug_id>', methods=['GET'])
@jwt_required()
def get_bug(bug_id):
    # 在此处设置断点
    bug = Bug.query.get_or_404(bug_id)
    return jsonify(bug.to_dict())
```

#### 2. 调试 Vue 组件
```vue
<!-- vue-frontend/src/views/BugList.vue -->
<script setup>
const fetchBugs = async () => {
  // 在此处设置断点
  const response = await fetch('/api/bugs')
  bugs.value = await response.json()
}
</script>
```

#### 3. 查看日志
- 后端日志：`backend/logs/enhanced_app.log`
- 业务日志：`backend/logs/business/`
- 错误日志：`backend/logs/errors/`
- 审计日志：`backend/logs/audit/`
- 性能日志：`backend/logs/performance/`

---

### 快捷键

| 快捷键 | 功能 |
|--------|------|
| **F5** | 启动调试 |
| **F9** | 切换断点 |
| **F10** | 单步跳过 |
| **F11** | 单步进入 |
| **Shift+F11** | 单步跳出 |
| **Ctrl+Shift+P** | 命令面板 |
| **Ctrl+`** | 打开终端 |
| **Ctrl+Shift+D** | 打开调试面板 |

---

### 访问地址

| 服务 | 地址 | 账号 |
|------|------|------|
| 前端 | http://localhost:3000 | admin / admin123 |
| 后端 API | http://localhost:5000/api | - |

---

### 系统功能模块

#### 后端 API 模块 (33个)
1. activities.py - 活动记录
2. attendance.py - 考勤管理
3. audit.py - 审计日志
4. auth.py - 认证
5. avatar.py - 头像管理
6. bug_statistics.py - Bug统计
7. bugs.py - Bug管理
8. contracts.py - 合同管理
9. contracts_enhanced.py - 增强合同
10. contracts_statistics_enhanced.py - 合同统计
11. data_import_export.py - 数据导入导出
12. delivery_tracking.py - 配送跟踪
13. docs.py - API文档
14. export.py - 通用导出
15. health.py - 健康检查
16. knowledge.py - 知识库（v1.6 增强）
17. materials.py - 物料管理
18. monitoring.py - 系统监控
19. notifications.py - 通知管理
20. performance.py - 性能监控
21. personal_plan.py - 个人计划（v1.6 新增）
22. projects.py - 项目管理
23. project_logs.py - 项目日志
24. requirements.py - 需求管理
25. risks.py - 风险管理（v1.6 新增）
26. search.py - 搜索
27. statistics.py - 统计
28. system.py - 系统管理
29. test_management.py - 测试管理
30. todos.py - 待办事项
31. users.py - 用户管理（含模块权限、权限模板）
32. work_logs.py - 工作日志
33. __init__.py - 模块初始化

#### 前端页面 (65个)
- 仪表板：Dashboard
- 项目管理：ProjectList, ProjectDetail, ProjectForm, ProjectStatistics, ProjectBugList, ProjectLogList
- Bug管理：BugList, BugDetail, BugForm, BugStatistics
- 物料管理：MaterialList, MaterialCategoryList, WarehouseList, LocationList, InventoryList, SerialNumberList, MaterialRelationshipList, MaterialReport
- 合同管理：ContractList, ContractDetail, ContractStatistics
- 考勤管理：AttendanceList, AttendanceDetail, AttendanceReport, MyAttendance, ShiftManagement, LeaveApplication, LeaveApproval, OvertimeApplication, OvertimeApproval
- 需求管理：RequirementDocumentList, RequirementDocumentDetail, RequirementDashboard, RequirementTraceMatrix
- 测试管理：TestSuiteList, TestSuiteDetail, TestCaseList, TestCaseDetail, TestExecutionList, TestDashboard, TestReport
- 用户管理：UserList, UserDetail, UserProfile, MyDepartment
- 权限管理：ModulePermissions（v1.6 新增）, PermissionTemplates（v1.6 新增）
- 知识库：KnowledgeBase, KnowledgeEnhanced, KnowledgeArticleDetail, KnowledgeShare
- 个人工作台：MyTodos, WorkLogs, WorkLogList, WorkStatisticsDetail, PersonalPlan（v1.6 新增）
- 风险管理：RiskList（v1.6 新增）
- 系统功能：NotificationList, MonitoringList, ActivityList, SystemSettings, CustomReport, Login

---

### 常见问题

#### Q: 端口被占用怎么办？
**A**:
- 后端：修改 `run_app.py` 中的端口号
- 前端：修改 `vite.config.js` 中的 `server.port`

#### Q: Python 依赖安装失败？
**A**:
```bash
cd backend
pip3 install -r requirements.txt --upgrade
```

#### Q: Node 依赖安装失败？
**A**:
```bash
cd vue-frontend
npm install --legacy-peer-deps
```

#### Q: 如何查看更详细的日志？
**A**:
- 修改 `backend/logging_config.py` 中的日志级别为 DEBUG
- 重启后端服务

#### Q: 前端页面空白怎么办？
**A**:
- 检查浏览器控制台错误
- 确认后端 API 是否正常运行
- 清除浏览器缓存

---

**文档创建时间**: 2026-03-16
**最后更新**: 2026-06
**VS Code 版本**: 1.111.0+
**系统版本**: TOPO System v1.6.0

---

## 二、远程开发环境（VS Code Server）

### 概述

VS Code Server 允许在远程服务器上运行 VS Code，通过浏览器访问，实现远程开发和调试。

---

### 访问方式

#### 方式一：浏览器直接访问（推荐）

**地址**: `http://your-server-ip:8080`

> **注意**: 需要在服务器防火墙和安全组中开放 **8080** 端口

#### 方式二：SSH 隧道访问（更安全，无需开放端口）

**本地终端执行**:
```bash
ssh -L 8080:localhost:8080 admin@your-server-ip
```

然后访问：`http://localhost:8080`

---

### 快速开始

#### 1. 启动 VS Code Server

```bash
# 启动服务
code-server --port 8080 --bind-addr 0.0.0.0 /path/to/topo_system
```

#### 2. 打开项目

在 VS Code Server 浏览器界面中：
- File → Open Folder
- 选择 `/home/admin/topo_system` 或你部署的项目路径

#### 3. 启动后端

打开终端：
```bash
cd /path/to/topo_system/backend
python run_app.py
```

#### 4. 启动前端

打开另一个终端：
```bash
cd /path/to/topo_system/vue-frontend
npm run dev
```

#### 5. 访问应用

- **前端**: http://localhost:3000（如果是本地访问）或 http://your-server-ip:3000
- **后端 API**: http://localhost:5000/api

---

### 配置说明

#### 启动参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--port` | 端口号 | `--port 8080` |
| `--bind-addr` | 绑定地址 | `--bind-addr 0.0.0.0` |
| `--auth` | 认证方式 | `--auth password` 或 `--auth none` |
| `--password` | 访问密码 | `--password your-password` |

#### 完整配置示例

```bash
# 创建配置目录
mkdir -p ~/.config/code-server

# 创建配置文件
cat > ~/.config/code-server/config.yaml << EOF
bind-addr: 0.0.0.0:8080
auth: password
password: your-strong-password
cert: false
EOF

# 启动服务
code-server
```

---

### 服务管理

#### 手动启动

```bash
# 前台运行
code-server --port 8080 --bind-addr 0.0.0.0 /path/to/topo_system

# 后台运行
nohup code-server --port 8080 --bind-addr 0.0.0.0 /path/to/topo_system > ~/code-server.log 2>&1 &
```

#### 使用 systemd 服务（推荐）

创建服务文件 `/etc/systemd/system/code-server.service`:

```ini
[Unit]
Description=VS Code Server
After=network.target

[Service]
Type=simple
User=admin
WorkingDirectory=/home/admin
ExecStart=/usr/bin/code-server --port 8080 --bind-addr 0.0.0.0 --config /home/admin/.config/code-server/config.yaml
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable code-server
sudo systemctl start code-server

# 查看状态
sudo systemctl status code-server
```

---

### 推荐扩展

在 VS Code Server 中安装以下扩展：

#### Python 开发
- **Python** (ms-python.python)
- **Pylance** (ms-python.vscode-pylance)
- **Python Debugger** (ms-python.debugpy)

#### Vue 开发
- **Vue - Official** (Vue.volar)
- **Volar** (Vue.volar)

#### 通用工具
- **Prettier - Code formatter** (esbenp.prettier-vscode)
- **GitLens** (eamodio.gitlens)
- **Remote - SSH** (ms-vscode-remote.remote-ssh) - 本地 VS Code 使用

#### 安装命令

```bash
# 在 code-server 终端中安装
code-server --install-extension ms-python.python
code-server --install-extension ms-python.vscode-pylance
code-server --install-extension Vue.volar
code-server --install-extension esbenp.prettier-vscode
```

---

### TOPO System 开发调试

#### 打开项目

在 VS Code Server 中：
- File → Open Folder
- 选择 `/home/admin/topo_system` 或你的项目路径

#### 启动后端

打开终端：
```bash
cd /home/admin/topo_system/backend
python run_app.py
```

#### 启动前端

打开另一个终端：
```bash
cd /home/admin/topo_system/vue-frontend
npm run dev
```

#### 访问应用

- **前端**: 点击弹出的 http://localhost:3000 链接，或使用服务器IP访问
- **后端 API**: http://localhost:5000/api

#### 调试

1. **Python 后端调试**
   - 在代码中设置断点
   - 使用 VS Code 调试面板启动 "Python: Flask Backend"

2. **Vue 前端调试**
   - 在 Vue 组件中设置断点
   - 使用浏览器开发者工具查看

---

### 端口开放（服务器防火墙）

#### Linux 防火墙

```bash
# Ubuntu/Debian
sudo ufw allow 8080/tcp
sudo ufw allow 3000/tcp
sudo ufw allow 5000/tcp
sudo ufw status

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

#### 云服务器安全组

如果使用阿里云、腾讯云等：
- 登录云服务器控制台
- 配置安全组规则，开放 8080、3000、5000 端口

---

### 服务状态

| 项目 | 说明 |
|------|------|
| code-server | 运行在服务器上 |
| 端口 | 8080（默认） |
| 认证 | 可配置密码或无认证 |
| 工作目录 | /path/to/topo_system |

---

### 常用操作

#### 查看日志

```bash
# 查看 code-server 日志
tail -f ~/code-server.log

# 或使用 journalctl
sudo journalctl -u code-server -f
```

#### 停止服务

```bash
# 如果是前台运行
Ctrl+C

# 如果是后台运行
pkill code-server

# 如果使用 systemd
sudo systemctl stop code-server
```

#### 重启服务

```bash
# 如果使用 systemd
sudo systemctl restart code-server

# 如果是手动运行
pkill code-server
code-server --port 8080 --bind-addr 0.0.0.0 /path/to/topo_system &
```

#### 查看进程

```bash
ps aux | grep code-server
```

#### 查看端口占用

```bash
netstat -tlnp | grep 8080
```

---

### 故障排查

#### 问题 1: 无法访问 8080 端口

**解决**:
```bash
# 检查防火墙
sudo ufw status
sudo ufw allow 8080/tcp

# 检查安全组
# 登录云控制台，配置安全组规则

# 检查服务是否运行
ps aux | grep code-server
```

#### 问题 2: code-server 启动失败

**解决**:
```bash
# 查看日志
journalctl -u code-server -f

# 检查端口占用
lsof -i :8080

# 重新启动
sudo systemctl restart code-server
```

#### 问题 3: Python 环境找不到

**解决**:
```bash
# 检查 Python 路径
which python3

# 设置 Python 路径
# VS Code → Settings → Python: Default Interpreter Path
# 输入：/usr/bin/python3
```

#### 问题 4: 页面加载缓慢或白屏

**解决**:
```bash
# 清除浏览器缓存
# 或使用无痕模式访问

# 检查网络连接
ping your-server-ip
```

---

### 配置信息

| 配置项 | 说明 |
|--------|------|
| 安装路径 | `/usr/bin/code-server` |
| 配置文件 | `~/.config/code-server/config.yaml` |
| 数据目录 | `~/.local/share/code-server` |
| 默认端口 | 8080 |
| 工作目录 | 启动时指定 |

---

### 安全建议

1. **启用密码认证**：生产环境务必设置密码
2. **使用 HTTPS**：通过 Nginx 反向代理配置 SSL
3. **限制访问 IP**：使用防火墙规则限制可访问的 IP
4. **定期更新**：保持 code-server 版本更新

#### Nginx 反向代理配置 HTTPS

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection upgrade;
        proxy_set_header Accept-Encoding gzip;
    }
}
```

---

**安装时间**: 2026-03-16
**最后更新**: 2026-06
**系统版本**: TOPO System v1.6.0

---

## 附：项目结构

项目结构请见仓库根目录 README.md 的『项目结构』章节。
