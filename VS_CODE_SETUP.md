# TOPO System - VS Code 调试指南

## 快速开始

### 1. 打开项目
1. 启动 VS Code
2. 文件 → 打开文件夹
3. 选择 `D:\topo_system` 文件夹

### 2. 安装推荐扩展
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

## 调试配置

### 方式一：使用任务 (推荐)

**Ctrl+Shift+P** → **Tasks: Run Task**

| 任务 | 说明 |
|------|------|
| `Start Backend` | 启动 Flask 后端 (端口 5000) |
| `Start Frontend` | 启动 Vue 前端 (端口 3000) |
| `Install Backend Dependencies` | 安装 Python 依赖 |
| `Install Frontend Dependencies` | 安装 Node 依赖 |
| `Restart Backend` | 重启后端服务 |

### 方式二：使用调试器

**F5** 或 **运行和调试** 面板

| 配置 | 说明 |
|------|------|
| `Python: Flask Backend` | 调试模式启动后端 |
| `Vue: Frontend Dev Server` | 启动前端并连接 Chrome 调试 |
| `Full Stack (Backend + Frontend)` | 同时启动前后端 |

### 方式三：终端手动启动

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

## 断点调试

### Python 后端调试
1. 在 Python 代码中点击行号左侧添加断点
2. 选择 `Python: Flask Backend` 配置
3. 按 **F5** 启动调试
4. 访问 http://localhost:5000 触发断点

### Vue 前端调试
1. 在 Vue 组件中点击行号左侧添加断点
2. 选择 `Vue: Frontend Dev Server` 配置
3. 按 **F5** 启动调试
4. 在浏览器中操作触发断点

---

## 项目结构

```
topo_system/
├── backend/              # Flask 后端
│   ├── api/             # API 路由 (33个模块)
│   │   ├── activities.py      # 活动记录
│   │   ├── attendance.py      # 考勤管理
│   │   ├── audit.py           # 审计日志
│   │   ├── auth.py            # 认证
│   │   ├── avatar.py          # 头像管理
│   │   ├── bug_statistics.py  # Bug统计
│   │   ├── bugs.py            # Bug管理
│   │   ├── contracts.py       # 合同管理
│   │   ├── contracts_enhanced.py # 增强合同
│   │   ├── contracts_statistics_enhanced.py # 合同统计
│   │   ├── data_import_export.py # 数据导入导出
│   │   ├── delivery_tracking.py # 配送跟踪
│   │   ├── docs.py            # 文档
│   │   ├── export.py          # 导出
│   │   ├── health.py          # 健康检查
│   │   ├── knowledge.py       # 知识库
│   │   ├── materials.py       # 物料管理
│   │   ├── monitoring.py      # 系统监控
│   │   ├── notifications.py   # 通知管理
│   │   ├── performance.py     # 性能监控
│   │   ├── personal_plan.py   # 个人计划
│   │   ├── projects.py        # 项目管理
│   │   ├── project_logs.py    # 项目日志
│   │   ├── requirements.py    # 需求管理
│   │   ├── risks.py           # 风险管理
│   │   ├── search.py          # 搜索
│   │   ├── statistics.py      # 统计
│   │   ├── system.py          # 系统管理
│   │   ├── tasks.py           # 任务管理
│   │   ├── test_management.py # 测试管理
│   │   ├── todos.py           # 待办事项
│   │   ├── users.py           # 用户管理
│   │   ├── work_logs.py       # 工作日志
│   │   └── system_config.json # 系统配置
│   ├── models/          # 数据模型
│   │   ├── materials.py       # 物料模型
│   │   └── permissions.py     # 权限模型
│   ├── services/       # 业务服务
│   │   ├── email_service.py   # 邮件服务
│   │   ├── contract_enhanced_service.py # 合同服务
│   │   └── delivery_tracking_service.py # 配送服务
│   ├── uploads/         # 上传文件
│   ├── backups/         # 数据库备份
│   ├── logs/            # 日志文件
│   │   ├── audit/      # 审计日志
│   │   ├── business/   # 业务日志
│   │   ├── errors/     # 错误日志
│   │   ├── performance/ # 性能日志
│   │   └── requests/   # 请求日志
│   ├── instance/        # SQLite 数据库
│   ├── migrations/      # 数据库迁移
│   ├── requirements.txt  # Python 依赖
│   ├── run_app.py       # 启动脚本
│   ├── enhanced_app.py  # Flask 应用
│   └── logging_config.py # 日志配置
│
├── vue-frontend/        # Vue 3 前端
│   ├── src/
│   │   ├── views/       # 页面组件 (61个页面)
│   │   │   ├── ActivityList.vue        # 活动列表
│   │   │   ├── AttendanceDetail.vue    # 考勤详情
│   │   │   ├── AttendanceList.vue      # 考勤列表
│   │   │   ├── AttendanceReport.vue    # 考勤报表
│   │   │   ├── BugDetail.vue           # Bug详情
│   │   │   ├── BugForm.vue             # Bug表单
│   │   │   ├── BugList.vue             # Bug列表
│   │   │   ├── BugStatistics.vue       # Bug统计
│   │   │   ├── ContractDetail.vue      # 合同详情
│   │   │   ├── ContractList.vue        # 合同列表
│   │   │   ├── ContractStatistics.vue  # 合同统计
│   │   │   ├── CustomReport.vue        # 自定义报表
│   │   │   ├── Dashboard.vue           # 仪表板
│   │   │   ├── InventoryList.vue        # 库存列表
│   │   │   ├── KnowledgeBase.vue        # 知识库
│   │   │   ├── KnowledgeEnhanced.vue    # 知识增强
│   │   │   ├── KnowledgeListFinal.vue   # 知识列表
│   │   │   ├── KnowledgeShare.vue       # 知识分享
│   │   │   ├── LeaveApplication.vue    # 请假申请
│   │   │   ├── LeaveApproval.vue       # 请假审批
│   │   │   ├── LocationList.vue        # 库位列表
│   │   │   ├── Login.vue                # 登录
│   │   │   ├── MaterialCategoryList.vue # 物料分类
│   │   │   ├── MaterialList.vue         # 物料列表
│   │   │   ├── MaterialRelationshipList.vue # 物料关系
│   │   │   ├── MaterialReport.vue       # 物料报表
│   │   │   ├── MonitoringList.vue      # 监控列表
│   │   │   ├── MyDepartment.vue         # 我的部门
│   │   │   ├── MyTodos.vue              # 我的待办
│   │   │   ├── NotificationList.vue     # 通知列表
│   │   │   ├── OvertimeApplication.vue  # 加班申请
│   │   │   ├── OvertimeApproval.vue     # 加班审批
│   │   │   ├── ProjectBugList.vue       # 项目Bug
│   │   │   ├── ProjectDetail.vue        # 项目详情
│   │   │   ├── ProjectForm.vue          # 项目表单
│   │   │   ├── ProjectList.vue          # 项目列表
│   │   │   ├── ProjectLogList.vue       # 项目日志
│   │   │   ├── ProjectStatistics.vue     # 项目统计
│   │   │   ├── RequirementDashboard.vue # 需求仪表板
│   │   │   ├── RequirementDocumentDetail.vue # 需求详情
│   │   │   ├── RequirementDocumentList.vue # 需求列表
│   │   │   ├── RequirementTraceMatrix.vue # 需求追溯
│   │   │   ├── SerialNumberList.vue     # 序列号
│   │   │   ├── ShiftManagement.vue      # 班次管理
│   │   │   ├── SystemSettings.vue       # 系统设置
│   │   │   ├── TaskDetail.vue           # 任务详情
│   │   │   ├── TaskList.vue             # 任务列表
│   │   │   ├── TestCaseDetail.vue       # 测试用例
│   │   │   ├── TestCaseList.vue         # 测试用例
│   │   │   ├── TestDashboard.vue        # 测试仪表板
│   │   │   ├── TestExecutionList.vue    # 测试执行
│   │   │   ├── TestReport.vue           # 测试报告
│   │   │   ├── TestSuiteDetail.vue     # 测试集
│   │   │   ├── TestSuiteList.vue        # 测试集
│   │   │   ├── UserDetail.vue           # 用户详情
│   │   │   ├── UserList.vue             # 用户列表
│   │   │   ├── UserProfile.vue          # 用户资料
│   │   │   ├── WarehouseList.vue        # 仓库列表
│   │   │   ├── WorkLogList.vue          # 工作日志
│   │   │   ├── WorkLogs.vue             # 工作日志
│   │   │   └── WorkStatisticsDetail.vue # 工作统计
│   │   ├── components/  # 通用组件
│   │   │   ├── business/ # 业务组件
│   │   │   │   ├── CoverageChart.vue
│   │   │   │   ├── ExecutionItemCard.vue
│   │   │   │   ├── ExecutionProgress.vue
│   │   │   │   ├── TestCaseTable.vue
│   │   │   │   └── TestSuiteTree.vue
│   │   │   └── common/  # 通用组件
│   │   │       ├── AttachmentList.vue
│   │   │       ├── PermissionWrapper.vue
│   │   │       ├── RequirementSelector.vue
│   │   │       ├── RichTextEditor.vue
│   │   │       ├── StepEditor.vue
│   │   │       ├── TestCaseResultBadge.vue
│   │   │       └── UserSelector.vue
│   │   ├── composables/  # 组合式函数
│   │   ├── router/      # 路由配置
│   │   ├── services/    # API 调用
│   │   │   ├── api.js
│   │   │   ├── bugStatisticsService.js
│   │   │   ├── materials.js
│   │   │   ├── systemTimeService.js
│   │   │   └── websocket.js
│   │   ├── stores/      # Pinia 状态管理
│   │   │   ├── bug.js
│   │   │   └── user.js
│   │   ├── utils/       # 工具函数
│   │   │   ├── dateUtils.js
│   │   │   └── position.js
│   │   └── assets/      # 静态资源
│   ├── package.json     # Node 依赖
│   └── vite.config.js   # Vite 配置
│
├── .vscode/             # VS Code 配置
│   ├── settings.json    # 工作区设置
│   ├── launch.json      # 调试配置
│   └── tasks.json       # 任务配置
│
└── README.md            # 项目文档
```

---

## 常用调试场景

### 1. 调试 API 接口
```python
# backend/api/bugs.py
@bugs_bp.route('/<int:bug_id>', methods=['GET'])
@jwt_required()
def get_bug(bug_id):
    # 在此处设置断点
    bug = Bug.query.get_or_404(bug_id)
    return jsonify(bug.to_dict())
```

### 2. 调试 Vue 组件
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

### 3. 查看日志
- 后端日志：`backend/logs/enhanced_app.log`
- 业务日志：`backend/logs/business/`
- 错误日志：`backend/logs/errors/`
- 审计日志：`backend/logs/audit/`
- 性能日志：`backend/logs/performance/`

---

## 快捷键

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

## 访问地址

| 服务 | 地址 | 账号 |
|------|------|------|
| 前端 | http://localhost:3000 | admin / admin123 |
| 后端 API | http://localhost:5000/api | - |

---

## 系统功能模块

### 后端 API 模块 (28个)
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
13. docs.py - 文档
14. export.py - 导出
15. health.py - 健康检查
16. knowledge.py - 知识库
17. materials.py - 物料管理
18. monitoring.py - 系统监控
19. notifications.py - 通知管理
20. performance.py - 性能监控
21. projects.py - 项目管理
22. project_logs.py - 项目日志
23. requirements.py - 需求管理
24. search.py - 搜索
25. statistics.py - 统计
26. system.py - 系统管理
27. tasks.py - 任务管理
28. test_management.py - 测试管理
29. todos.py - 待办事项
30. users.py - 用户管理
31. work_logs.py - 工作日志
32. personal_plan.py - 个人计划
33. risks.py - 风险管理

### 前端页面 (63个)
- 仪表板：Dashboard
- 项目管理：ProjectList, ProjectDetail, ProjectForm, ProjectStatistics, ProjectBugList, ProjectLogList
- Bug管理：BugList, BugDetail, BugForm, BugStatistics
- 任务管理：TaskList, TaskDetail
- 物料管理：MaterialList, MaterialCategoryList, WarehouseList, LocationList, InventoryList, SerialNumberList, MaterialRelationshipList, MaterialReport
- 合同管理：ContractList, ContractDetail, ContractStatistics
- 考勤管理：AttendanceList, AttendanceDetail, AttendanceReport, ShiftManagement, LeaveApplication, LeaveApproval, OvertimeApplication, OvertimeApproval
- 需求管理：RequirementDocumentList, RequirementDocumentDetail, RequirementDashboard, RequirementTraceMatrix
- 测试管理：TestSuiteList, TestSuiteDetail, TestCaseList, TestCaseDetail, TestExecutionList, TestDashboard, TestReport
- 用户管理：UserList, UserDetail, UserProfile, MyDepartment
- 知识库：KnowledgeBase, KnowledgeListFinal, KnowledgeEnhanced, KnowledgeShare
- 个人工作台：MyTodos, WorkLogs, WorkLogList, WorkStatisticsDetail, PersonalPlan
- 风险管理：RiskList
- 系统功能：NotificationList, MonitoringList, ActivityList, SystemSettings, CustomReport, Login

---

## 常见问题

### Q: 端口被占用怎么办？
**A**:
- 后端：修改 `run_app.py` 中的端口号
- 前端：修改 `vite.config.js` 中的 `server.port`

### Q: Python 依赖安装失败？
**A**:
```bash
cd backend
pip3 install -r requirements.txt --upgrade
```

### Q: Node 依赖安装失败？
**A**:
```bash
cd vue-frontend
npm install --legacy-peer-deps
```

### Q: 如何查看更详细的日志？
**A**:
- 修改 `backend/logging_config.py` 中的日志级别为 DEBUG
- 重启后端服务

### Q: 前端页面空白怎么办？
**A**:
- 检查浏览器控制台错误
- 确认后端 API 是否正常运行
- 清除浏览器缓存

---

**文档创建时间**: 2026-03-16
**最后更新**: 2026-04
**VS Code 版本**: 1.111.0+
**系统版本**: TOPO System v1.4.0
