# 部署说明

本文档详细说明TOPO系统的生产环境部署流程。

## 系统概述

TOPO系统是一个功能完整的组织架构管理与工作协同平台，包含以下核心模块：
- 项目管理
- Bug跟踪管理
- 物料管理系统
- 合同管理系统
- 配送跟踪系统
- 考勤管理系统
- 任务管理
- 需求管理
- 测试管理
- 用户权限管理
- 知识库系统
- 通知系统
- 统计报表
- 系统监控
- 审计日志

## 生产环境要求

### 服务器要求
- **操作系统**: Ubuntu 20.04+ / CentOS 7+ / Windows Server 2019+
- **内存**: 至少 4GB RAM（推荐8GB+）
- **存储**: 至少 20GB 可用空间
- **网络**: 稳定的网络连接

### 软件要求
- **Python**: 3.8+ (推荐3.9+)
- **Node.js**: 14+ (推荐16+)
- **npm**: 6+ (推荐8+)
- **数据库**: SQLite（开发）或 PostgreSQL/MySQL（生产）
- **Web服务器**: Nginx 或 Apache
- **进程管理**: systemd 或 Supervisor

## 部署步骤

### 1. 服务器准备

#### 更新系统包
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

#### 安装基础软件
```bash
# Ubuntu/Debian
sudo apt install -y python3 python3-pip python3-venv nodejs npm nginx

# CentOS/RHEL
sudo yum install -y python3 python3-pip nodejs npm nginx
```

### 2. 项目部署

#### 克隆项目
```bash
cd /var/www
sudo git clone <repository-url> topo_system
sudo chown -R www-data:www-data topo_system
cd topo_system
```

#### 后端环境配置
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
cd backend
pip install -r requirements.txt

# 初始化数据库
python init_enhanced_db.py
```

#### 前端构建
```bash
cd ../vue-frontend
npm install
npm run build
```

### 3. 生产环境配置

#### 后端配置
创建生产环境配置文件 `backend/config.py`:
```python
import os

class ProductionConfig:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///production.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24小时

    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = '/var/www/topo_system/uploads'
```

#### 环境变量设置
创建 `.env` 文件：
```bash
SECRET_KEY=your-production-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
DATABASE_URL=sqlite:///var/www/topo_system/instance/production.db
JWT_ACCESS_TOKEN_EXPIRES=86400

# 邮件配置
EMAIL_ENABLED=true
SMTP_SERVER=smtp.vip.163.com
SMTP_PORT=465
SMTP_USERNAME=your-email@163.com
SMTP_PASSWORD=your-authorization-code
FROM_EMAIL=your-email@163.com
USE_SSL=true
```

### 4. Web服务器配置

#### Nginx配置
创建 `/etc/nginx/sites-available/topo_system`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/topo_system/vue-frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 文件上传目录
    location /uploads/ {
        alias /var/www/topo_system/uploads/;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        root /var/www/topo_system/vue-frontend/dist;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

启用站点：
```bash
sudo ln -s /etc/nginx/sites-available/topo_system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 5. 进程管理

#### 使用systemd管理后端服务
创建 `/etc/systemd/system/topo_system.service`:
```ini
[Unit]
Description=TOPO System Backend
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/topo_system/backend
Environment=PATH=/var/www/topo_system/venv/bin
ExecStart=/var/www/topo_system/venv/bin/python run_app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable topo_system
sudo systemctl start topo_system
```

### 6. 数据库备份

#### 自动备份脚本
创建 `backend/backup_script.py`:
```python
import os
import shutil
from datetime import datetime

def backup_database():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    source_db = "instance/production.db"
    backup_dir = "backups"
    backup_file = f"{backup_dir}/topo_system_backup_{timestamp}.db"

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    shutil.copy2(source_db, backup_file)
    print(f"Database backed up to: {backup_file}")

if __name__ == "__main__":
    backup_database()
```

#### 定时备份
添加cron任务：
```bash
# 每天凌晨2点备份
0 2 * * * /var/www/topo_system/venv/bin/python /var/www/topo_system/backend/backup_script.py
```

### 7. 安全配置

#### SSL证书（使用Let's Encrypt）
```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com
```

#### 防火墙配置
```bash
# 启用防火墙
sudo ufw enable

# 允许SSH、HTTP、HTTPS
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
```

### 8. 监控和日志

#### 日志配置
后端日志会自动记录到系统日志，可通过以下命令查看：
```bash
# 查看后端服务日志
sudo journalctl -u topo_system -f

# 查看Nginx访问日志
sudo tail -f /var/log/nginx/access.log

# 查看Nginx错误日志
sudo tail -f /var/log/nginx/error.log

# 应用日志位置
tail -f /var/www/topo_system/backend/logs/enhanced_app.log
```

#### 日志文件说明
- `backend/logs/enhanced_app.log` - 应用主日志
- `backend/logs/audit/` - 审计日志目录
- `backend/logs/business/` - 业务日志目录
- `backend/logs/errors/` - 错误日志目录
- `backend/logs/performance/` - 性能日志目录
- `backend/logs/requests/` - 请求日志目录

#### 健康检查脚本
创建 `backend/health_check.py`:
```python
import requests

def check_health():
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            print("Service is healthy")
            return True
        else:
            print(f"Service unhealthy: {response.status_code}")
            return False
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

if __name__ == "__main__":
    check_health()
```

### 9. 更新流程

#### 代码更新
```bash
cd /var/www/topo_system
sudo systemctl stop topo_system
sudo git pull origin main

# 更新后端
cd backend
source ../venv/bin/activate
pip install -r requirements.txt

# 更新前端
cd ../vue-frontend
npm install
npm run build

sudo systemctl start topo_system
```

#### 数据库迁移（如果需要）
```bash
cd backend
source ../venv/bin/activate
python migrate_database.py
```

## 故障排除

### 常见问题

#### 服务无法启动
1. 检查端口是否被占用：`netstat -tulpn | grep :5000`
2. 查看服务状态：`sudo systemctl status topo_system`
3. 检查日志：`sudo journalctl -u topo_system`

#### 数据库连接问题
1. 检查数据库文件权限
2. 验证数据库路径配置
3. 检查磁盘空间

#### 前端资源加载失败
1. 检查Nginx配置
2. 验证静态文件路径
3. 检查文件权限

### 性能优化

#### 数据库优化
```python
# 在Flask配置中添加
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_recycle": 300,
    "pool_pre_ping": True
}
```

#### 缓存配置
考虑添加Redis缓存：
```python
CACHE_TYPE = "RedisCache"
CACHE_REDIS_URL = "redis://localhost:6379/0"
```

#### 前端优化
```javascript
// vite.config.js
export default defineConfig({
  build: {
    chunkSizeWarningLimit: 1500,
    rollupOptions: {
      output: {
        manualChunks: {
          'element-plus': ['element-plus'],
          'echarts': ['echarts', 'vue-echarts']
        }
      }
    }
  }
})
```

## 备份和恢复

### 完整备份
```bash
# 备份数据库
sudo cp /var/www/topo_system/instance/production.db /backup/location/

# 备份上传文件
sudo tar -czf uploads_backup.tar.gz /var/www/topo_system/uploads/

# 备份配置文件
sudo tar -czf config_backup.tar.gz /var/www/topo_system/backend/.env
```

### 灾难恢复
1. 恢复数据库文件
2. 恢复上传文件
3. 恢复配置文件
4. 重新启动服务

## Docker部署（可选）

### Dockerfile
创建 `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 5000

CMD ["python", "run_app.py"]
```

### docker-compose.yml
创建 `docker-compose.yml`:
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./instance:/app/instance
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    environment:
      - DATABASE_URL=sqlite:///instance/topo_system.db

  frontend:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./vue-frontend/dist:/usr/share/nginx/html
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
```

## 环境配置参考

### 开发环境
- 后端：http://localhost:5000
- 前端：http://localhost:3000
- 数据库：SQLite本地文件

### 测试环境
- 后端：http://test-api.example.com
- 前端：http://test.example.com
- 数据库：PostgreSQL

### 生产环境
- 后端：https://api.example.com
- 前端：https://www.example.com
- 数据库：PostgreSQL/MySQL
- 缓存：Redis
- SSL证书：Let's Encrypt

## 系统模块说明

### 后端模块
| 模块 | 说明 |
|------|------|
| activities.py | 活动记录API |
| attendance.py | 考勤管理API |
| audit.py | 审计日志API |
| auth.py | 认证API |
| avatar.py | 头像管理API |
| bug_statistics.py | Bug统计API |
| bugs.py | Bug管理API |
| contracts.py | 合同管理API |
| contracts_enhanced.py | 增强合同API |
| contracts_statistics_enhanced.py | 合同统计API |
| data_import_export.py | 数据导入导出API |
| delivery_tracking.py | 配送跟踪API |
| knowledge.py | 知识库API |
| materials.py | 物料管理API |
| monitoring.py | 系统监控API |
| notifications.py | 通知管理API |
| performance.py | 性能监控API |
| projects.py | 项目管理API |
| project_logs.py | 项目日志API |
| requirements.py | 需求管理API |
| search.py | 搜索API |
| statistics.py | 统计API |
| system.py | 系统管理API |
| tasks.py | 任务管理API |
| test_management.py | 测试管理API |
| todos.py | 待办事项API |
| users.py | 用户管理API |
| work_logs.py | 工作日志API |

### 前端页面
| 页面 | 说明 |
|------|------|
| Dashboard.vue | 仪表板 |
| ProjectList.vue | 项目列表 |
| ProjectDetail.vue | 项目详情 |
| ProjectForm.vue | 项目表单 |
| ProjectStatistics.vue | 项目统计 |
| BugList.vue | Bug列表 |
| BugDetail.vue | Bug详情 |
| BugForm.vue | Bug表单 |
| BugStatistics.vue | Bug统计 |
| TaskList.vue | 任务列表 |
| TaskDetail.vue | 任务详情 |
| MaterialList.vue | 物料列表 |
| MaterialCategoryList.vue | 物料分类 |
| WarehouseList.vue | 仓库列表 |
| LocationList.vue | 库位列表 |
| InventoryList.vue | 库存列表 |
| SerialNumberList.vue | 序列号 |
| MaterialRelationshipList.vue | 物料关系 |
| MaterialReport.vue | 物料报表 |
| ContractList.vue | 合同列表 |
| ContractDetail.vue | 合同详情 |
| ContractStatistics.vue | 合同统计 |
| AttendanceList.vue | 考勤列表 |
| AttendanceDetail.vue | 考勤详情 |
| AttendanceReport.vue | 考勤报表 |
| ShiftManagement.vue | 班次管理 |
| LeaveApplication.vue | 请假申请 |
| LeaveApproval.vue | 请假审批 |
| OvertimeApplication.vue | 加班申请 |
| OvertimeApproval.vue | 加班审批 |
| RequirementDocumentList.vue | 需求文档列表 |
| RequirementDocumentDetail.vue | 需求文档详情 |
| RequirementDashboard.vue | 需求仪表板 |
| RequirementTraceMatrix.vue | 需求追溯矩阵 |
| TestSuiteList.vue | 测试集列表 |
| TestSuiteDetail.vue | 测试集详情 |
| TestCaseList.vue | 测试用例列表 |
| TestCaseDetail.vue | 测试用例详情 |
| TestExecutionList.vue | 测试执行列表 |
| TestDashboard.vue | 测试仪表板 |
| TestReport.vue | 测试报告 |
| UserList.vue | 用户列表 |
| UserDetail.vue | 用户详情 |
| UserProfile.vue | 用户资料 |
| MyDepartment.vue | 我的部门 |
| KnowledgeBase.vue | 知识库 |
| KnowledgeListFinal.vue | 知识列表 |
| KnowledgeEnhanced.vue | 知识增强 |
| KnowledgeShare.vue | 知识分享 |
| MyTodos.vue | 我的待办 |
| WorkLogs.vue | 工作日志 |
| WorkLogList.vue | 工作日志列表 |
| WorkStatisticsDetail.vue | 工作统计详情 |
| NotificationList.vue | 通知列表 |
| MonitoringList.vue | 监控列表 |
| ActivityList.vue | 活动记录 |
| SystemSettings.vue | 系统设置 |
| CustomReport.vue | 自定义报表 |
| Login.vue | 登录 |

## 支持联系方式

- **系统管理员**: admin@your-company.com
- **技术支持**: support@your-company.com
- **紧急联系**: +86-XXX-XXXX-XXXX

---

**注意**: 生产环境部署前请务必进行充分测试，并确保所有安全措施到位。

**版本**: v1.4.0
**最后更新**: 2026-04
