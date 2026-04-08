# TOPO系统

一个功能完整的TOPO系统（组织架构管理与工作协同平台），基于Flask后端和Vue.js前端，集成了项目管理、Bug跟踪、物料管理、考勤管理、任务管理、合同管理、配送跟踪、需求管理、测试管理、用户权限管理等综合功能。

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

#### 7. 任务管理
- 任务创建、分配、跟踪
- 任务状态管理（todo、in_progress、review、done、blocked、cancelled）
- 任务优先级和里程碑
- 任务参与人管理
- 任务评论和附件
- 父子任务关联
- 任务依赖管理

#### 8. 需求管理
- 需求文档管理
- 需求条目管理（支持树形结构）
- 需求评审和审批流程
- 需求状态跟踪
- 需求与Bug/任务/测试用例关联
- 需求追溯矩阵
- 需求版本历史
- 需求仪表板

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
- 基于角色的权限控制（admin、user、hr、department_manager、division_leader、project_manager、software_engineer、test_engineer、developer、tester）
- JWT Token认证
- 权限细粒度控制
- 头像管理
- 用户个人资料管理
- 用户列表和详情管理
- 部门管理

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
- 知识文章管理（创建、编辑、删除、点赞）
- 分类管理（多级分类树形结构）
- 标签管理（热门标签云）
- 全文搜索功能
- Markdown内容支持
- 附件上传下载管理
- 文章统计（浏览量、点赞数）
- 热门文章排行
- 最近更新追踪

#### 14. 系统监控
- 性能指标监控
- 数据库健康检查
- API响应时间统计
- 系统资源使用率

#### 15. 审计日志
- 操作审计记录
- 登录日志追踪
- 业务操作日志
- 日志查询和导出
- 活动记录追踪

#### 15. 个人工作台
- 我的待办事项
- 工作日志记录
- 活动记录跟踪
- 个人统计概览
- 工作统计详情
- 个人工作计划（收件箱、四象限、日历、专注、习惯追踪）
- 番茄钟专注模式

#### 17. 风险管理
- 风险/问题创建、编辑、删除
- 风险状态管理（identified、analyzing、mitigating、resolved、closed等）
- 风险等级和优先级管理（low、medium、high、critical）
- 风险类别管理
- 风险敞口计算（probability × impact）
- 风险矩阵可视化
- 风险统计和分布分析
- 关联Bug和任务

#### 18. 数据导入导出
- 批量数据导入
- 批量数据导出
- 数据格式转换

## 技术栈

### 后端技术栈
- **核心框架**: Flask 2.3.3 - Python Web框架
- **数据库**: SQLite - 轻量级关系型数据库
- **ORM**: SQLAlchemy 2.0.23 - 数据库对象关系映射
- **认证授权**:
  - Flask-JWT-Extended 4.5.3 - JWT Token认证
  - 自定义权限系统 - 基于角色的细粒度权限控制
- **API开发**: Flask-RESTful - RESTful API开发
- **文件处理**:
  - Flask-Uploads - 文件上传管理
  - Pillow 10.0.1 - 图像处理
- **数据导出**: openpyxl 3.1.2 - Excel文件处理
- **其他依赖**:
  - Flask-CORS 4.0.0 - 跨域资源共享
  - Flask-Mail 0.9.1 - 邮件发送
  - python-dotenv 1.0.0 - 环境变量管理

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

#### 1. 认证管理 API
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/refresh` - 刷新Token
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/me` - 获取当前用户信息

#### 2. 用户管理 API
- `GET /api/users` - 获取用户列表
- `POST /api/users` - 创建用户
- `GET /api/users/{id}` - 获取用户详情
- `PUT /api/users/{id}` - 更新用户信息
- `DELETE /api/users/{id}` - 删除用户
- `GET /api/users/departments` - 获取部门列表
- `GET /api/users/profile` - 获取当前用户资料

#### 3. 头像管理 API
- `POST /api/avatar/upload` - 上传头像
- `GET /api/avatar/<user_id>` - 获取用户头像

#### 4. 项目管理 API
- `GET /api/projects` - 获取项目列表
- `POST /api/projects` - 创建新项目
- `GET /api/projects/{id}` - 获取项目详情
- `PUT /api/projects/{id}` - 更新项目信息
- `DELETE /api/projects/{id}` - 删除项目
- `GET /api/projects/{id}/members` - 获取项目成员
- `POST /api/projects/{id}/members` - 添加项目成员
- `GET /api/projects/{id}/logs` - 获取项目日志

#### 5. Bug跟踪管理 API
- `GET /api/bugs` - 获取Bug列表（支持筛选）
- `POST /api/bugs` - 创建新Bug
- `GET /api/bugs/{id}` - 获取Bug详情
- `PUT /api/bugs/{id}` - 更新Bug信息
- `POST /api/bugs/{id}/comments` - 添加Bug评论
- `PUT /api/bugs/{id}/status` - 更新Bug状态
- `GET /api/bugs/{id}/comments` - 获取Bug评论列表
- `GET /api/bugs/statistics` - Bug统计数据

#### 6. 任务管理 API
- `GET /api/tasks` - 获取任务列表
- `POST /api/tasks` - 创建新任务
- `PUT /api/tasks/{id}` - 更新任务信息
- `PUT /api/tasks/{id}/status` - 更新任务状态

#### 7. 物料管理 API
- `GET /api/materials` - 获取物料列表
- `POST /api/materials` - 创建新物料
- `PUT /api/materials/{id}` - 更新物料信息
- `POST /api/materials/import` - 批量导入物料
- `GET /api/materials/export` - 导出物料数据
- `GET /api/materials/statistics` - 物料统计信息
- `GET /api/materials/categories` - 物料分类
- `GET /api/materials/warehouses` - 仓库管理
- `GET /api/materials/inventory` - 库存管理
- `GET /api/materials/locations` - 库位管理
- `GET /api/materials/serial-numbers` - 序列号管理
- `GET /api/materials/relationships` - 物料关系

#### 8. 合同管理 API
- `GET /api/contracts` - 获取合同列表
- `POST /api/contracts` - 创建新合同
- `PUT /api/contracts/{id}` - 更新合同信息
- `DELETE /api/contracts/{id}` - 删除合同
- `GET /api/contracts/statistics` - 合同统计信息
- `GET /api/contracts/enhanced/{id}` - 获取增强合同详情
- `POST /api/contracts/enhanced/{id}/approve` - 合同审批

#### 9. 配送跟踪 API
- `GET /api/contracts/delivery` - 获取配送列表
- `POST /api/contracts/delivery` - 创建配送单
- `PUT /api/contracts/delivery/{id}` - 更新配送状态

#### 10. 考勤管理 API
- `POST /api/attendance/clock-in` - 上班打卡
- `POST /api/attendance/clock-out` - 下班打卡
- `GET /api/attendance/records` - 获取考勤记录
- `POST /api/attendance/leave` - 请假申请
- `POST /api/attendance/overtime` - 加班申请
- `GET /api/attendance/shifts` - 班次管理
- `POST /api/attendance/leave-approval` - 请假审批
- `POST /api/attendance/overtime-approval` - 加班审批
- `GET /api/attendance/report` - 考勤报表

#### 11. 需求管理 API
- `GET /api/requirements/documents` - 需求文档列表
- `POST /api/requirements/documents` - 创建需求文档
- `GET /api/requirements/items` - 需求条目列表
- `POST /api/requirements/items` - 创建需求条目
- `GET /api/requirements/trace` - 需求追溯矩阵

#### 12. 测试管理 API
- `GET /api/test-management/suites` - 测试集列表
- `POST /api/test-management/suites` - 创建测试集
- `GET /api/test-management/cases` - 测试用例列表
- `POST /api/test-management/cases` - 创建测试用例
- `POST /api/test-management/executions` - 创建测试执行
- `GET /api/test-management/results` - 测试结果

#### 13. 统计报表 API
- `GET /api/statistics/projects` - 项目统计
- `GET /api/statistics/bugs` - Bug统计
- `GET /api/statistics/users` - 用户活跃度统计
- `GET /api/statistics/attendance` - 考勤统计
- `GET /api/statistics/contracts` - 合同统计
- `GET /api/reports` - 智能报表

#### 14. 系统管理 API
- `GET /api/admin/users` - 用户管理列表
- `PUT /api/admin/users/{id}/role` - 修改用户角色
- `POST /api/system/backup` - 数据库备份
- `GET /api/system/config` - 获取系统配置
- `PUT /api/system/config` - 更新系统配置

#### 15. 通知管理 API
- `GET /api/notifications` - 获取通知列表
- `PUT /api/notifications/{id}/read` - 标记通知为已读

#### 16. 知识库 API
- `GET /api/knowledge/categories` - 获取知识库分类列表
- `POST /api/knowledge/categories` - 创建分类
- `PUT /api/knowledge/categories/{id}` - 更新分类
- `DELETE /api/knowledge/categories/{id}` - 删除分类
- `GET /api/knowledge/articles` - 获取文章列表
- `GET /api/knowledge/articles/{id}` - 获取文章详情
- `POST /api/knowledge/articles` - 创建文章
- `PUT /api/knowledge/articles/{id}` - 更新文章
- `DELETE /api/knowledge/articles/{id}` - 删除文章
- `POST /api/knowledge/articles/{id}/like` - 点赞文章
- `GET /api/knowledge/search` - 全文搜索文章
- `GET /api/knowledge/tags` - 获取所有标签
- `GET /api/knowledge/statistics` - 获取知识库统计

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
- `GET /api/data/export` - 批量导出

#### 21. 待办事项 API
- `GET /api/todos` - 获取待办列表
- `POST /api/todos` - 创建待办
- `PUT /api/todos/{id}` - 更新待办
- `DELETE /api/todos/{id}` - 删除待办

#### 22. 工作日志 API
- `GET /api/work-logs` - 获取工作日志
- `POST /api/work-logs` - 创建工作日志
- `GET /api/work-logs/statistics` - 工作日志统计

#### 23. 个人计划 API
- `GET /api/personal-plan/tasks` - 获取任务列表
- `POST /api/personal-plan/tasks` - 创建任务
- `GET /api/personal-plan/tasks/{id}` - 获取任务详情
- `PUT /api/personal-plan/tasks/{id}` - 更新任务
- `DELETE /api/personal-plan/tasks/{id}` - 删除任务
- `GET /api/personal-plan/tasks/inbox` - 获取收件箱任务
- `POST /api/personal-plan/tasks/inbox/process` - 处理收件箱
- `GET /api/personal-plan/tasks/quadrant` - 获取四象限任务
- `POST /api/personal-plan/tasks/start` - 开始任务
- `POST /api/personal-plan/tasks/complete` - 完成任务
- `GET /api/personal-plan/calendar/events` - 获取日历事件
- `GET /api/personal-plan/time-blocks` - 获取时间块
- `POST /api/personal-plan/focus/start` - 开始专注
- `POST /api/personal-plan/focus/end` - 结束专注
- `GET /api/personal-plan/focus/stats` - 专注统计
- `GET /api/personal-plan/habits` - 获取习惯列表
- `POST /api/personal-plan/habits/check-in` - 打卡习惯
- `GET /api/personal-plan/stats/daily` - 每日统计
- `GET /api/personal-plan/stats/weekly` - 每周统计

#### 24. 风险管理 API
- `GET /api/risks` - 获取风险列表
- `POST /api/risks` - 创建风险/问题
- `GET /api/risks/{id}` - 获取风险详情
- `PUT /api/risks/{id}` - 更新风险/问题
- `DELETE /api/risks/{id}` - 删除风险/问题
- `GET /api/risks/statistics` - 风险统计
- `GET /api/risks/matrix` - 风险矩阵

## 数据库结构

### 核心数据表结构

#### 1. 用户相关表
- **users**: 用户基本信息（ID、用户名、邮箱、角色、状态等）
- **user_profiles**: 用户详细信息（姓名、部门、职位等）

#### 2. 项目管理表
- **projects**: 项目信息（名称、描述、状态、负责人等）
- **project_members**: 项目成员关联表
- **project_logs**: 项目日志表

#### 3. Bug跟踪表
- **bugs**: Bug信息（标题、描述、严重程度、优先级、状态等）
- **bug_comments**: Bug评论记录
- **bug_attachments**: Bug附件信息

#### 4. 任务管理表
- **tasks**: 任务信息（标题、描述、优先级、截止时间等）
- **task_assignments**: 任务分配记录

#### 5. 物料管理表
- **materials**: 物料基本信息（名称、分类、规格等）
- **material_inventory**: 物料库存信息
- **material_categories**: 物料分类表
- **warehouses**: 仓库表
- **locations**: 库位表
- **serial_numbers**: 序列号表
- **inventory_transactions**: 库存交易表
- **material_relationships**: 物料关系表

#### 6. 合同管理表
- **contracts**: 合同信息（名称、金额、状态、日期等）
- **contract_clauses**: 合同条款表
- **contract_approvals**: 合同审批表
- **contract_deliveries**: 合同交付表
- **contract_changes**: 合同变更表
- **contract_risks**: 合同风险表
- **contract_payments**: 合同付款表

#### 7. 配送跟踪表
- **delivery_tracking**: 配送信息（状态、进度、物流信息等）

#### 8. 考勤管理表
- **attendance_records**: 考勤记录（打卡时间、类型等）
- **leave_applications**: 请假申请
- **overtime_applications**: 加班申请
- **attendance_exceptions**: 考勤异常
- **shift_schedules**: 班次表
- **user_shifts**: 用户班次分配表
- **work_calendar**: 工作日历表

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
- **test_case_requirement_links**: 测试用例与需求关联

#### 11. 系统管理表
- **audit_logs**: 日志（操作类型、用户、时间、详情）
- **system_settings**: 系统配置表
- **backup_records**: 备份记录
- **notifications**: 通知表
- **activities**: 活动记录表

#### 12. 其他业务表
- **work_logs**: 工作日志表
- **todos**: 待办事项表
- **knowledge_articles**: 知识库文章表

## 项目结构

```
topo_system/
├── backend/                    # 后端Flask应用
│   ├── api/                   # API路由目录
│   │   ├── activities.py      # 活动记录API
│   │   ├── attendance.py      # 考勤管理API
│   │   ├── audit.py           # 审计日志API
│   │   ├── auth.py            # 认证API
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
│   │   ├── knowledge.py       # 知识库API
│   │   ├── materials.py       # 物料管理API
│   │   ├── monitoring.py      # 系统监控API
│   │   ├── notifications.py   # 通知管理API
│   │   ├── performance.py     # 性能监控API
│   │   ├── projects.py        # 项目管理API
│   │   ├── project_logs.py    # 项目日志API
│   │   ├── requirements.py    # 需求管理API
│   │   ├── search.py          # 搜索API
│   │   ├── statistics.py      # 统计API
│   │   ├── system.py          # 系统管理API
│   │   ├── tasks.py           # 任务管理API
│   │   ├── test_management.py # 测试管理API
│   │   ├── todos.py           # 待办事项API
│   │   ├── users.py           # 用户管理API
│   │   ├── work_logs.py       # 工作日志API
│   │   ├── personal_plan.py   # 个人计划API
│   │   ├── risks.py           # 风险管理API
│   │   └── system_config.json # 系统配置
│   ├── models/                # 数据模型定义
│   │   ├── __init__.py        # 模型导出
│   │   ├── materials.py       # 物料模型
│   │   └── permissions.py     # 权限模型
│   ├── services/              # 业务服务
│   │   ├── email_service.py   # 邮件服务
│   │   ├── contract_enhanced_service.py # 合同服务
│   │   └── delivery_tracking_service.py # 配送服务
│   ├── uploads/               # 文件上传目录
│   ├── backups/               # 数据库备份目录
│   ├── logs/                  # 日志文件目录
│   │   ├── audit/            # 审计日志
│   │   ├── business/         # 业务日志
│   │   ├── errors/           # 错误日志
│   │   ├── performance/      # 性能日志
│   │   └── requests/         # 请求日志
│   ├── instance/              # 数据库实例目录
│   ├── migrations/           # 数据库迁移脚本
│   ├── requirements.txt       # Python依赖
│   ├── run_app.py            # 应用启动脚本
│   ├── enhanced_app.py       # 增强应用入口
│   ├── restful_api.py        # RESTful API统一入口
│   ├── websocket_notifications.py # WebSocket通知
│   └── logging_config.py     # 日志配置
├── vue-frontend/             # 前端Vue应用
│   ├── src/                  # 源代码
│   │   ├── api/              # API封装
│   │   ├── components/       # 通用组件
│   │   │   ├── business/     # 业务组件
│   │   │   └── common/       # 通用组件
│   │   ├── composables/       # 组合式函数
│   │   ├── router/           # 路由配置
│   │   ├── services/         # API服务
│   │   ├── stores/           # 状态管理
│   │   ├── utils/            # 工具函数
│   │   └── views/            # 页面组件
│   ├── dist/                 # 构建输出目录
│   ├── package.json          # Node.js依赖
│   ├── vite.config.js        # Vite配置
│   └── index.html            # HTML模板
├── .vscode/                  # VS Code配置
├── instance/                 # 数据库文件目录
└── README.md                # 项目说明文档
```

## 更新日志

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
