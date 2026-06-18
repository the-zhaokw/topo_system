# TOPO系统

一个功能完整的TOPO系统（组织架构管理与工作协同平台），基于Flask后端和Vue.js前端，集成了项目管理、Bug跟踪、物料管理、考勤管理、任务管理、合同管理、配送跟踪、需求管理、测试管理、用户权限管理、知识库、个人工作计划、风险管理、模块权限控制等综合功能。

## 系统功能

### 核心功能模块

#### 1. 项目管理
- 项目创建、编辑、删除
- 项目成员管理（项目经理、开发人员、测试人员）
- 项目状态管理（planning、in_progress、completed、cancelled）
- 项目权限控制（基于角色的访问控制）
- 批量导入导出功能（CSV、Excel格式）
- 项目进度跟踪和成本管理
- 项目类型和客户信息管理
- 项目日志跟踪
- 项目Bug列表查看
- 项目下需求、测试、风险子模块
- 项目自定义报表

#### 2. Bug跟踪管理
- Bug创建、编辑、删除
- Bug状态机管理（new、assigned、in_progress、fixed、resolved、verified、closed、reopened、rejected）
- Bug优先级和严重程度管理
- Bug分配和跟踪
- Bug评论和活动记录
- 附件上传功能
- 工作流建议和验证
- Bug关联任务和测试用例
- Bug统计和趋势分析

#### 3. 物料管理系统
- 物料分类管理（多级分类结构）
- 物料主数据管理
- 仓库和库位管理
- 库存管理（入库、出库、调拨、盘点）
- 序列号管理
- 库存预警和报表
- 物料关系管理

#### 4. 合同管理系统
- 合同创建、编辑、删除
- 合同状态和风险等级管理
- 合同金额和付款跟踪
- 合同条款和审批流程
- 合同交付和变更管理
- 合同统计分析
- 通信设备企业增强功能（站点信息、BOM清单、知识产权条款等）

#### 5. 配送跟踪系统
- 配送单创建和管理
- 配送状态跟踪
- 配送进度监控

#### 6. 考勤管理系统
- 上下班打卡（支持位置和设备信息）
- 班次管理（白班、夜班、弹性时间）
- 工作日历管理
- 请假申请和审批（多级审批链）
- 加班申请和审批
- 考勤异常处理
- 考勤统计报表

#### 7. 个人计划（任务管理）
- 个人任务快速捕获、智能解析（@标签、!紧急、!高优、时间、时长）
- 收件箱/四象限/日历/时间块/专注/习惯多种视图
- 番茄钟专注模式（默认25分钟，可自定义）
- 习惯追踪（连续打卡、完成率统计）
- 日/周完成率、时间分配、专注时长统计
- 与团队任务解耦，专注个人工作流

#### 8. 需求管理
- 需求文档管理
- 需求条目管理（支持树形结构）
- 需求评审和审批流程
- 需求状态跟踪
- 需求与Bug/任务/测试用例关联
- 需求追溯矩阵
- 需求版本历史（版本对比、回滚）
- 需求仪表板
- 需求覆盖率统计、影响分析
- 需求导出

#### 9. 测试管理
- 测试集管理（树形结构）
- 测试用例管理
- 测试步骤管理
- 测试执行记录
- 测试结果跟踪
- 测试用例与需求关联
- 测试报表生成
- 测试仪表板

#### 10. 用户权限管理
- 用户注册和登录
- 基于角色的权限控制（admin、manager、project_manager、software_engineer、test_engineer、user、hr、department_manager）
- JWT Token认证
- 头像管理
- 用户个人资料管理
- 用户列表和详情管理
- 部门管理、职位管理、批量成员操作
- 用户批量导入/导出、重置密码、停用/启用
- **模块权限控制**：每个用户可独立配置可访问的大功能模块
- **权限模板**：将一组模块权限保存为模板，批量应用到用户
- 用户活动状态、活动记录

#### 11. 统计和报告
- 项目统计信息
- Bug统计和趋势分析
- 考勤统计报表
- 物料库存统计
- 合同统计分析
- 数据可视化图表
- 批量数据导出（CSV、Excel）
- 自定义报表
- 智能报表中心

#### 12. 通知系统
- Bug分配通知
- 状态变更通知
- @提及通知
- 邮件通知
- 审批通知
- WebSocket实时通知

#### 13. 知识库系统
- 知识文章管理（创建、编辑、删除、点赞、收藏、置顶、归档）
- 分类管理（多级分类树形结构，支持归档）
- 标签管理（热门标签云）
- 全文搜索功能
- Markdown内容支持
- 附件上传下载管理
- 文章评论、关联文章
- 文章状态流转、版本历史
- 批量操作（移动/状态/删除）
- 文章统计（浏览量、点赞数）
- 知识分享链接（带Token的公开分享）
- 导出（Markdown/PDF/Word）
- 热门文章排行、最近更新追踪

#### 14. 系统监控
- 性能指标监控
- 数据库健康检查
- API响应时间统计
- 系统资源使用率
- 健康检查接口（`/api/health`、`/health`）

#### 15. 审计日志
- 操作审计记录
- 登录日志追踪
- 业务操作日志（业务/审计/错误/性能/请求日志分类存储）
- 日志查询和导出
- 活动记录追踪
- 日志轮转与归档

#### 16. 个人工作台
- 我的待办事项
- 工作日志记录
- 活动记录跟踪
- 个人统计概览
- 工作统计详情
- 个人工作计划（收件箱、四象限、日历、专注、习惯追踪）
- 番茄钟专注模式
- 习惯追踪、连续打卡统计

#### 17. 风险管理
- 风险/问题创建、编辑、删除
- 风险状态管理（identified、analyzing、mitigating、resolved、closed等）
- 风险等级和优先级管理（low、medium、high、critical）
- 风险类别管理
- 风险敞口计算（probability × impact）
- 风险矩阵可视化
- 风险统计和分布分析
- 关联Bug
- 全文搜索、按负责人/类别筛选

#### 18. 数据导入导出
- 批量数据导入（项目、用户、Bug、物料等）
- 批量数据导出（CSV/Excel）
- 数据格式转换
- 模板下载

#### 19. 模块权限控制
- 大功能模块编码（项目、Bug、考勤、物料、合同、用户、设置、监控、活动、知识、待办、计划、部门等）
- 用户级别的模块访问控制（白名单/黑名单）
- 权限模板管理（创建/编辑/删除/应用）
- 管理员可批量重置用户模块权限

#### 20. 通知中心
- Bug分配、状态变更、@提及通知
- 审批通知（请假、加班）
- 邮件通知
- WebSocket 实时通知
- 通知已读/未读状态管理

#### 21. 移动端 & 小程序
- Vue 前端响应式适配（手机/平板/桌面）
- 微信小程序（项目、Bug、考勤、合同、库存、物料、风险、个人计划、通知等）
- 离线缓存、PWA 风格主屏

## 技术栈

### 后端技术栈
- **核心框架**: Flask 2.3.3 - Python Web框架
- **数据库**: SQLite - 轻量级关系型数据库
- **ORM**: SQLAlchemy 2.0.23 - 数据库对象关系映射
- **认证授权**:
  - Flask-JWT-Extended 4.5.3 - JWT Token认证
  - 自定义权限系统 - 基于角色的细粒度权限控制
- **API开发**: Flask 蓝图（Blueprint） - 35+ 模块化 API
- **实时通信**: Flask-SocketIO + WebSocket
- **文件处理**:
  - Werkzeug - 文件上传管理
  - Pillow 10.0.1 - 图像处理
- **数据导出**: openpyxl 3.1.2 - Excel文件处理
- **其他依赖**:
  - Flask-CORS 4.0.0 - 跨域资源共享
  - Flask-Mail / smtplib - 邮件发送
  - python-dotenv 1.0.0 - 环境变量管理
  - zoneinfo - 中国时区 (UTC+8) 支持

### 前端技术栈
- **核心框架**: Vue.js 3 - 现代化前端框架
- **路由管理**: Vue Router - 单页面应用路由
- **状态管理**: Pinia - Vue 3状态管理库
- **UI组件库**: Element Plus - 企业级UI组件库
- **构建工具**: Vite - 现代化前端构建工具
- **HTTP客户端**: Axios - Promise-based HTTP客户端
- **图表库**: ECharts - 数据可视化图表
- **日期处理**: date-fns - 日期处理工具

### 系统架构特色
- **模块化设计**: 采用蓝图(Blueprint)架构，功能模块独立
- **状态机管理**: 内置Bug状态机，支持工作流验证
- **日志系统**: 完整的操作审计记录，多级别日志
- **数据验证**: 前后端双重数据验证机制
- **错误处理**: 统一的错误处理和异常捕获
- **安全机制**: JWT认证、权限控制、SQL注入防护
- **WebSocket支持**: 实时通知和协作功能

## 快速开始

### 环境要求
- **Python**: 3.8+ (推荐3.9+)
- **Node.js**: 14+ (推荐16+)
- **npm**: 6+ (推荐8+)
- **操作系统**: Windows/Linux/macOS

### 后端部署

1. **创建虚拟环境（推荐）**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

2. **安装Python依赖**
```bash
cd backend
pip install -r requirements.txt
```

3. **初始化数据库**
```bash
python init_enhanced_db.py
```

4. **启动后端服务**
```bash
python run_app.py
```

后端服务将在 http://localhost:5000 启动

### 前端部署

1. **安装Node.js依赖**
```bash
cd vue-frontend
npm install
```

2. **配置环境变量**
编辑 `.env.development` 文件，确保API地址正确：
```
VITE_API_BASE_URL=http://localhost:5000/api
```

3. **启动开发服务器**
```bash
npm run dev
```

前端服务将在 http://localhost:3000 启动（如果端口被占用，会自动使用其他端口）

4. **构建生产版本**
```bash
npm run build
```

构建后的文件将生成在 `dist/` 目录中

### 完整启动流程

1. **启动后端服务**（终端1）
```bash
cd backend
python run_app.py
```

2. **启动前端服务**（终端2）
```bash
cd vue-frontend
npm run dev
```

3. **访问系统**
- 前端地址: http://localhost:3000
- 后端API: http://localhost:5000/api
- API文档: http://localhost:5000/api/docs (如果启用了Swagger)

## 系统配置

### 后端配置

在 `backend/.env` 文件中配置环境变量：

```bash
# 数据库配置
DATABASE_URL=sqlite:///topo_system.db

# JWT配置
JWT_SECRET_KEY=your-secret-key-here  # 生产环境请使用强随机密钥
JWT_ACCESS_TOKEN_EXPIRES=86400       # Token有效期（秒），默认24小时

# 邮件配置（可选，用于通知和密码重置）
# 网易邮箱推荐配置
MAIL_SERVER=smtp.vip.163.com
MAIL_PORT=465
MAIL_USE_SSL=true
MAIL_USE_TLS=false
MAIL_USERNAME=your-email@163.com
MAIL_PASSWORD=your-authorization-code
MAIL_DEFAULT_SENDER=your-email@163.com

# 文件上传配置
UPLOAD_FOLDER=uploads                # 上传文件存储目录
MAX_CONTENT_LENGTH=16777216          # 最大文件大小（16MB）
ALLOWED_EXTENSIONS=txt,pdf,png,jpg,jpeg,gif,doc,docx,xls,xlsx

# 系统配置
SYSTEM_NAME=Topo组织管理系统
ADMIN_EMAIL=admin@example.com
BACKUP_ENABLED=True                  # 是否启用自动备份
BACKUP_INTERVAL=24                   # 备份间隔（小时）

# 调试和日志
DEBUG=True
LOG_LEVEL=INFO                       # 日志级别：DEBUG/INFO/WARNING/ERROR
LOG_FILE=logs/app.log                # 日志文件路径

# CORS配置
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 前端配置

在 `vue-frontend/.env.development` 文件中配置开发环境变量：

```bash
# API基础地址
VITE_API_BASE_URL=http://localhost:5000/api

# 应用配置
VITE_APP_NAME=Topo组织管理系统
VITE_APP_VERSION=1.0.0

# 功能开关
VITE_ENABLE_DEBUG=true               # 启用调试模式
VITE_ENABLE_MOCK=false               # 是否启用Mock数据

# 主题配置
VITE_THEME_PRIMARY=#409EFF          # 主色调
VITE_THEME_SUCCESS=#67C23A          # 成功色
VITE_THEME_WARNING=#E6A23C          # 警告色
VITE_THEME_DANGER=#F56C6C           # 危险色

# 页面配置
VITE_PAGE_SIZE=20                   # 默认分页大小
VITE_UPLOAD_MAX_SIZE=16             # 上传文件最大大小（MB）
```

生产环境配置在 `vue-frontend/.env.production` 文件中，需要设置正确的API地址和关闭调试模式。

### 重要安全配置

1. **JWT密钥**：生产环境必须使用强随机密钥
2. **数据库路径**：确保数据库文件有适当权限
3. **上传目录**：配置正确的文件权限和访问控制
4. **邮件服务**：使用安全的SMTP配置

### 默认用户账户
- **管理员**: username: `admin`, password: `admin123`
- **项目经理**: username: `project_manager`, password: `project123`
- **开发人员**: username: `developer1`, password: `dev123`
- **测试人员**: username: `tester1`, password: `test123`

### 数据库配置
- 开发环境数据库: `instance/topo_system.db`
- 数据库备份目录: `backend/backups/`
- 文件上传目录: `backend/uploads/`

## API接口

### 主要API接口分类

#### 1. 认证管理 API（`/api/auth`）
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `GET  /api/auth/me` - 获取当前登录用户信息
- `PUT  /api/auth/me` - 更新当前登录用户信息

#### 2. 用户管理 API（`/api/users`）
- `GET  /api/users` - 获取用户列表（支持角色/部门/搜索筛选）
- `POST /api/users` - 创建用户
- `GET  /api/users/search` - 搜索用户
- `GET  /api/users/approvers` - 获取审批人列表
- `GET  /api/users/{id}` - 获取用户详情
- `GET  /api/users/{id}/home` - 获取用户主页聚合数据
- `PUT  /api/users/{id}/status` - 更新用户状态（启用/停用）
- `POST /api/users/{id}/activity` - 记录用户活动
- `PUT  /api/users/{id}` - 更新用户信息
- `DELETE /api/users/{id}` - 删除用户
- `POST /api/users/{id}/reset-password` - 重置密码
- `POST /api/users/batch-delete` - 批量删除
- `GET  /api/users/export/{format}` - 导出用户（CSV/Excel）
- `POST /api/users/import` - 导入用户
- `GET  /api/users/departments` - 获取部门列表
- `GET/POST/PUT/DELETE /api/users/departments[...]` - 部门管理
- `GET  /api/users/positions` - 获取职位列表
- `GET/POST/PUT/DELETE /api/users/positions[...]` - 职位管理
- `GET  /api/users/permissions` - 获取权限码列表
- `GET/PUT /api/users/{id}/permissions` - 用户权限读写
- `POST /api/users/batch-update-role` - 批量修改角色
- `GET  /api/users/my-department` - 获取我的部门信息
- `GET  /api/users/module-permissions/catalog` - 模块权限目录
- `GET  /api/users/module-permissions/users` - 用户的模块权限
- `GET/PUT /api/users/{id}/module-permissions` - 模块权限读写
- `POST /api/users/{id}/module-permissions/reset` - 重置模块权限
- `GET/POST/PUT/DELETE /api/users/permission-templates[...]` - 权限模板管理
- `POST /api/users/permission-templates/{id}/apply` - 应用权限模板

#### 3. 头像管理 API
- `POST /api/avatar/upload` - 上传头像
- `GET  /api/avatar/<user_id>` - 获取用户头像

#### 4. 项目管理 API（`/api/projects`）
- `GET/POST /api/projects` - 列表/创建项目
- `GET/PUT/DELETE /api/projects/{id}` - 详情/更新/删除
- `GET/POST /api/projects/{id}/members` - 项目成员
- `GET  /api/projects/{id}/logs` - 项目日志
- 项目下子模块：项目Bug、项目日志、项目需求、项目测试、项目风险、项目自定义报表

#### 5. Bug跟踪管理 API（`/api/bugs`）
- `GET/POST /api/bugs` - 列表/创建
- `GET/PUT/DELETE /api/bugs/{id}` - 详情/更新/删除
- `GET/POST /api/bugs/{id}/comments` - Bug评论
- `PUT  /api/bugs/{id}/status` - 更新状态
- `POST /api/bugs/{id}/attachments` - 上传附件
- `GET  /api/bugs/statistics` - 统计
- 详见 `bug_statistics.py`

#### 6. 个人计划 API（`/api/personal-plan`）
- `GET/POST /api/personal-plan/tasks` - 任务列表/创建
- `GET/PUT/DELETE /api/personal-plan/tasks/{id}` - 任务详情/更新/删除
- `GET  /api/personal-plan/tasks/inbox` - 收件箱
- `POST /api/personal-plan/tasks/inbox/process` - 处理收件箱
- `GET  /api/personal-plan/tasks/quadrant` - 四象限任务
- `POST /api/personal-plan/tasks/start` - 开始任务
- `POST /api/personal-plan/tasks/complete` - 完成任务
- `GET  /api/personal-plan/calendar/events` - 日历事件
- `GET  /api/personal-plan/time-blocks` - 时间块
- `POST /api/personal-plan/focus/start` - 开始专注
- `POST /api/personal-plan/focus/end` - 结束专注
- `GET  /api/personal-plan/focus/stats` - 专注统计
- `GET  /api/personal-plan/habits` - 习惯列表
- `POST /api/personal-plan/habits/check-in` - 打卡习惯
- `GET  /api/personal-plan/stats/daily` - 每日统计
- `GET  /api/personal-plan/stats/weekly` - 每周统计

#### 7. 物料管理 API（`/api/materials`）
- 物料主数据、分类、仓库、库位、库存、序列号、关系、报表、导入导出
- 库存操作：入库、出库、调拨、盘点
- 库存预警

#### 8. 合同管理 API（`/api/contracts`）
- 合同 CRUD、状态管理
- 增强版：`/api/contracts/enhanced/{id}`、审批 `/approve`
- 增强统计：`/api/contracts/statistics/enhanced`
- 配送跟踪：`/api/contracts/delivery`
- 通信设备企业增强功能：站点信息、BOM清单、知识产权条款、付款条款

#### 9. 配送跟踪 API
- `GET/POST /api/contracts/delivery` - 配送列表/创建
- `PUT  /api/contracts/delivery/{id}` - 更新配送状态

#### 10. 考勤管理 API（`/api/attendance`）
- `GET  /api/attendance/work-calendar` - 工作日历
- `GET  /api/attendance/records` - 考勤记录
- `POST /api/attendance/clock-in` / `clock-out` - 上下班打卡
- `GET  /api/attendance/records/today` - 今日记录
- `GET/POST /api/attendance/leave-applications` - 请假申请
- `GET/POST /api/attendance/overtime-applications` - 加班申请
- `POST /api/attendance/overtime-applications/{id}/approve` - 加班审批
- `GET/POST/PUT/DELETE /api/attendance/shifts[...]` - 班次管理
- `GET/POST/DELETE /api/attendance/user-shifts[...]` - 用户班次
- `GET  /api/attendance/exceptions` - 考勤异常
- `GET  /api/attendance/statistics` - 考勤统计
- `GET  /api/attendance/reports/overview` - 考勤概览报表
- `GET  /api/attendance/reports/detail` - 考勤明细报表
- `GET  /api/attendance/my-summary` - 我的考勤汇总
- `GET  /api/attendance/records/export` - 记录导出
- `GET  /api/attendance/reports/export` - 报表导出

#### 11. 需求管理 API（`/api/requirements`）
- 需求文档/条目 CRUD、状态变更、评论、关联
- 版本管理：版本列表、创建版本、版本对比、回滚
- 追溯矩阵、覆盖率、影响分析
- 文档/条目评审
- 我的需求待办
- 需求导出

#### 12. 测试管理 API（`/api/test-management`）
- 测试集 CRUD（树形、版本历史、批量）
- 测试用例 CRUD（步骤管理、评审、复制、批量）
- 测试执行 CRUD（项目/Suite维度）
- 测试结果、需求关联、用例执行历史
- 统计、报表、仪表板
- 用例导入/导出

#### 13. 统计报表 API
- `GET /api/statistics/projects` - 项目统计
- `GET /api/statistics/bugs` - Bug统计
- `GET /api/statistics/users` - 用户活跃度统计
- `GET /api/statistics/attendance` - 考勤统计
- `GET /api/statistics/contracts` - 合同统计
- `GET /api/reports` - 智能报表

#### 14. 系统管理 API
- `GET  /api/system/backup` - 备份列表
- `POST /api/system/backup` - 创建备份
- `GET/PUT /api/system/config` - 系统配置读写
- 健康检查 `/api/health` 与 `/health`

#### 15. 通知管理 API（`/api/notifications`）
- 通知列表、未读/已读标记、已读全部

#### 16. 知识库 API（`/api/knowledge`）
- 分类管理：列表、树形、创建/更新/删除/归档
- 文章管理：列表、我的、详情、创建/更新/删除、状态变更、置顶
- 评论、关联文章、附件上传/下载/删除
- 批量操作（移动/状态/删除）
- 点赞、收藏
- 全文搜索、标签
- 统计、最近/热门排行
- 分享 Token 创建/获取/取消/下载

#### 17. 系统监控 API
- `GET /api/monitoring` - 系统监控数据
- `GET /api/performance` - 性能指标
- `GET /api/health` - 健康检查

#### 18. 审计日志 API
- `GET /api/audit` - 获取审计日志
- `GET /api/activities` - 获取活动记录

#### 19. 搜索 API
- `GET /api/search` - 全局搜索

#### 20. 数据导入导出 API
- `POST /api/data/import` - 批量导入
- `GET  /api/data/export` - 批量导出

#### 21. 待办事项 API（`/api/todos`）
- 任务/待办 CRUD、状态流转

#### 22. 工作日志 API（`/api/work-logs`）
- 工作日志 CRUD、统计

#### 23. 项目日志 API（`/api/project-logs`）
- 项目日志 CRUD

#### 24. 风险管理 API（`/api/risks`）
- `GET/POST /api/risks` - 风险/问题列表/创建
- `GET/PUT/DELETE /api/risks/{id}` - 详情/更新/删除
- `GET  /api/risks/statistics` - 风险统计
- `GET  /api/risks/matrix` - 风险矩阵
- 支持 risk_type、status、level、priority、category、assigned_to、search 筛选

## 数据库结构

### 核心数据表结构

#### 1. 用户相关表
- **users**: 用户基本信息（ID、用户名、邮箱、角色、状态、职位、部门、邮箱通知开关等）
- **departments / positions**: 部门表 / 职位表
- **module_permissions**: 用户模块权限（白名单/黑名单）
- **permission_templates**: 权限模板（可应用到用户）

#### 2. 项目管理表
- **projects**: 项目信息（名称、描述、状态、负责人、进度、风险、成本等）
- **project_members**: 项目成员关联表
- **project_logs**: 项目日志表
- **project_custom_reports**: 项目自定义报表

#### 3. Bug跟踪表
- **bugs**: Bug信息（标题、描述、严重程度、优先级、状态、reopen次数、关联任务/测试等）
- **bug_comments**: Bug评论记录
- **bug_attachments**: Bug附件信息
- **bug_activities**: Bug活动记录

#### 4. 个人计划表
- **personal_tasks**: 个人任务（标题、四象限、计划时间、专注时长、是否习惯等）
- **focus_sessions**: 专注记录
- **habit_check_ins**: 习惯打卡记录
- **time_blocks**: 时间块

#### 5. 物料管理表
- **materials**: 物料基本信息
- **material_inventory**: 物料库存
- **material_categories**: 物料分类
- **warehouses**: 仓库
- **locations**: 库位
- **serial_numbers**: 序列号
- **inventory_transactions**: 库存交易
- **material_relationships**: 物料关系

#### 6. 合同管理表
- **contracts**: 合同信息
- **contract_clauses / sites / bom / payments / ip_terms**: 增强版条款/站点/BOM/付款/知识产权
- **contract_approvals**: 合同审批
- **contract_deliveries**: 合同交付
- **contract_changes**: 合同变更
- **contract_risks**: 合同风险

#### 7. 配送跟踪表
- **delivery_tracking**: 配送信息

#### 8. 考勤管理表
- **attendance_records**: 考勤记录
- **leave_applications**: 请假申请
- **overtime_applications**: 加班申请
- **attendance_exceptions**: 考勤异常
- **shifts**: 班次
- **user_shifts**: 用户班次
- **work_calendar**: 工作日历

#### 9. 需求管理表
- **requirement_documents**: 需求文档
- **requirement_items**: 需求条目
- **requirement_comments**: 需求评论
- **requirement_links**: 需求关联
- **requirement_versions**: 需求版本历史

#### 10. 测试管理表
- **test_suites**: 测试集
- **test_cases**: 测试用例
- **test_steps**: 用例步骤
- **test_executions**: 测试执行
- **test_results**: 用例结果
- **test_case_requirement_links**: 用例-需求关联

#### 11. 系统管理表
- **audit_logs**: 审计日志
- **system_settings / system_config.json**: 系统配置
- **backup_records**: 备份记录
- **notifications**: 通知
- **activities**: 活动记录

#### 12. 知识库表
- **knowledge_categories**: 分类（多级、归档）
- **knowledge_articles**: 文章（Markdown、状态、置顶）
- **knowledge_comments**: 评论
- **knowledge_attachments**: 附件
- **knowledge_article_links**: 关联文章
- **knowledge_favorites / likes**: 收藏/点赞
- **knowledge_shares**: 分享 Token

#### 13. 个人工作台表
- **work_logs**: 工作日志
- **todos**: 待办

#### 14. 风险管理表
- **risks**: 风险/问题（等级、优先级、概率/影响、敞口、关联Bug）

## 项目结构

```
topo_system/
├── backend/                    # 后端Flask应用
│   ├── api/                   # API路由目录（35个模块）
│   │   ├── activities.py      # 活动记录API
│   │   ├── attendance.py      # 考勤管理API（24个接口）
│   │   ├── audit.py           # 审计日志API
│   │   ├── auth.py            # 认证API（login/register/me）
│   │   ├── avatar.py          # 头像管理API
│   │   ├── bug_statistics.py  # Bug统计API
│   │   ├── bugs.py            # Bug管理API
│   │   ├── contracts.py       # 合同管理API
│   │   ├── contracts_enhanced.py # 增强合同API
│   │   ├── contracts_statistics_enhanced.py # 合同统计API
│   │   ├── data_import_export.py # 数据导入导出API
│   │   ├── delivery_tracking.py # 配送跟踪API
│   │   ├── docs.py            # 文档API
│   │   ├── export.py          # 导出API
│   │   ├── health.py          # 健康检查API
│   │   ├── knowledge.py       # 知识库API（39个接口）
│   │   ├── knowledge_pdf_fix.py # 知识库PDF补丁
│   │   ├── materials.py       # 物料管理API
│   │   ├── monitoring.py      # 系统监控API
│   │   ├── notifications.py   # 通知管理API
│   │   ├── performance.py     # 性能监控API
│   │   ├── personal_plan.py   # 个人计划API
│   │   ├── project_logs.py    # 项目日志API
│   │   ├── projects.py        # 项目管理API
│   │   ├── requirements.py    # 需求管理API（36个接口）
│   │   ├── risks.py           # 风险管理API
│   │   ├── search.py          # 全局搜索API
│   │   ├── statistics.py      # 统计API
│   │   ├── system.py          # 系统管理API
│   │   ├── test_management.py # 测试管理API（34个接口）
│   │   ├── todos.py           # 待办事项API
│   │   ├── users.py           # 用户管理API（43个接口）
│   │   ├── work_logs.py       # 工作日志API
│   │   └── system_config.json # 系统配置
│   ├── models/                # 数据模型定义
│   │   ├── __init__.py        # 模型导出
│   │   ├── attendance.py      # 考勤模型
│   │   ├── base.py            # 基础模型
│   │   ├── bug.py             # Bug模型
│   │   ├── enums.py           # 枚举定义
│   │   ├── materials.py       # 物料模型
│   │   ├── notification.py    # 通知模型
│   │   ├── permission_template.py # 权限模板模型
│   │   ├── permissions.py     # 权限模型
│   │   ├── project.py         # 项目模型
│   │   └── user.py            # 用户模型
│   ├── services/              # 业务服务
│   │   ├── approval_service.py        # 审批服务
│   │   ├── contract_enhanced_service.py # 合同服务
│   │   ├── delivery_tracking_service.py  # 配送服务
│   │   ├── email_service.py           # 邮件服务
│   │   └── notification_service.py    # 通知服务
│   ├── config/                # 应用配置
│   │   ├── __init__.py
│   │   ├── config.py          # 配置类
│   │   └── extensions.py      # 扩展（db/jwt/cors）
│   ├── migrations/            # 数据库迁移脚本
│   ├── uploads/               # 文件上传目录
│   ├── backups/               # 数据库备份目录
│   ├── logs/                  # 日志文件目录
│   │   ├── audit/            # 审计日志
│   │   ├── business/         # 业务日志
│   │   ├── errors/           # 错误日志
│   │   ├── performance/      # 性能日志
│   │   └── requests/         # 请求日志
│   ├── instance/              # 数据库实例目录
│   ├── utils/                 # 工具函数
│   │   ├── file_utils.py
│   │   ├── permission_unified.py
│   │   ├── permission_utils.py
│   │   └── time_utils.py
│   ├── requirements.txt       # Python依赖
│   ├── run_app.py            # 应用启动脚本
│   ├── enhanced_app.py       # Flask应用（含模型/蓝图注册）
│   ├── restful_api.py        # RESTful API统一入口
│   ├── websocket_server.py   # WebSocket服务
│   ├── websocket_notifications.py # WebSocket通知
│   ├── logging_config.py     # 日志配置
│   └── state_machine.py      # Bug状态机
├── vue-frontend/             # 前端Vue应用
│   ├── src/                  # 源代码
│   │   ├── components/       # 通用组件
│   │   │   ├── business/     # 业务组件（块编辑器、分享管理、版本历史）
│   │   │   └── common/       # 通用组件
│   │   ├── composables/       # 组合式函数（useMobileList、useResponsive）
│   │   ├── directives/       # 自定义指令（permission）
│   │   ├── router/           # 路由配置
│   │   ├── services/         # API服务（api.js、materials.js、websocket.js等）
│   │   ├── stores/           # Pinia 状态管理（bug、user、userStatus）
│   │   ├── utils/            # 工具函数（dateUtils、position）
│   │   ├── styles/           # 全局样式（design-system、aesthetic-theme、mobile）
│   │   └── views/            # 页面组件（60+ 页面）
│   ├── dist/                 # 构建输出目录
│   ├── package.json          # Node.js依赖
│   └── vite.config.js        # Vite配置
├── mini-app/                 # 微信小程序（Taro）
├── chenxiao/                 # 官网（Next.js）
├── instance/                 # 数据库文件目录
├── logs/                     # 顶层日志目录
└── README.md                # 项目说明文档
```

## 更新日志

### v1.6.0 (2026-06)
- 新增**模块权限控制**功能：用户级别可独立配置可访问的大功能模块（项目、Bug、考勤等），支持权限模板
- **知识库升级**：文章状态流转换、置顶、归档、收藏、Markdown/PDF/Word 导出、分享 Token、批量操作
- **需求管理升级**：版本对比与回滚、影响分析、覆盖率统计、需求评审
- **测试管理升级**：版本历史、用例评审/复制/批量、用例导入导出、需求关联
- **合同管理升级**：增强统计、审批工作流、付款与知识产权条款
- **考勤管理升级**：工作日历、班次/用户班次管理、考勤异常、我的汇总、记录/报表导出
- **用户管理升级**：批量导入导出、重置密码、活动状态、部门/职位管理、模块权限 UI
- **个人计划升级**：任务智能解析、四象限、日历、番茄钟、习惯追踪
- **风险管理升级**：风险类别、敞口、风险矩阵、关联 Bug、统计
- **小程序 & 移动端**：Taro 多端小程序发布；Vue 前端移动端深度适配
- **API 数量提升**：35+ API 模块、220+ 端点

### v1.5.0 (2026-04)
- 新增个人工作计划系统（收件箱、四象限视图、日历规划、番茄钟专注模式）
- 新增习惯追踪功能（打卡记录、连续打卡统计）
- 新增风险管理模块（风险/问题管理、风险矩阵、敞口计算）
- 新增个人设置功能
- 增强每日/每周统计功能

### v1.4.0 (2026-04)
- 新增部门管理功能
- 增强用户个人资料管理
- 新增工作统计详情功能
- 增强项目日志功能
- 新增知识库分享功能
- 新增知识增强功能
- 优化系统性能和稳定性
- 修复已知问题

### v1.3.0 (2026-03)
- 新增知识库系统（文章管理、分类管理、标签、搜索、附件）
- 新增系统监控功能
- 新增智能报表中心
- 新增审计日志和活动记录
- 新增数据导入导出功能
- 增强项目日志功能
- 增强搜索功能
- 性能优化和bug修复

### v1.2.0 (2026-03)
- 新增需求管理系统（需求文档、需求条目、追溯矩阵）
- 新增测试管理系统（测试集、测试用例、测试执行、测试报告）
- 增强合同管理功能（条款、审批、交付、变更、风险、付款）
- 增强考勤管理功能（班次管理、工作日历、多级审批链）
- 完善邮件通知系统
- 完善审计日志功能
- 修复已知问题

### v1.1.0 (2025-11)
- 新增合同管理系统
- 新增配送跟踪系统
- 新增序列号管理
- 新增性能监控功能
- 新增邮件服务配置和测试功能
- 新增通知系统
- 完善日志系统（审计、业务、错误、性能日志分离）
- 修复SQLAlchemy初始化兼容性问题

### v1.0.0 (2025-11)
- 初始版本发布
- 基本Bug管理功能
- 项目和用户管理
- 统计仪表板
- 筛选和搜索功能
