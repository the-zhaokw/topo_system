# VS Code Server 配置指南

## 概述

VS Code Server 允许在远程服务器上运行 VS Code，通过浏览器访问，实现远程开发和调试。

---

## 访问方式

### 方式一：浏览器直接访问（推荐）

**地址**: `http://your-server-ip:8080`

> **注意**: 需要在服务器防火墙和安全组中开放 **8080** 端口

### 方式二：SSH 隧道访问（更安全，无需开放端口）

**本地终端执行**:
```bash
ssh -L 8080:localhost:8080 admin@your-server-ip
```

然后访问：`http://localhost:8080`

---

## 快速开始

### 1. 启动 VS Code Server

```bash
# 启动服务
code-server --port 8080 --bind-addr 0.0.0.0 /path/to/topo_system
```

### 2. 打开项目

在 VS Code Server 浏览器界面中：
- File → Open Folder
- 选择 `/home/admin/topo_system` 或你部署的项目路径

### 3. 启动后端

打开终端：
```bash
cd /path/to/topo_system/backend
python run_app.py
```

### 4. 启动前端

打开另一个终端：
```bash
cd /path/to/topo_system/vue-frontend
npm run dev
```

### 5. 访问应用

- **前端**: http://localhost:3000（如果是本地访问）或 http://your-server-ip:3000
- **后端 API**: http://localhost:5000/api

---

## 配置说明

### 启动参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--port` | 端口号 | `--port 8080` |
| `--bind-addr` | 绑定地址 | `--bind-addr 0.0.0.0` |
| `--auth` | 认证方式 | `--auth password` 或 `--auth none` |
| `--password` | 访问密码 | `--password your-password` |

### 完整配置示例

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

## 服务管理

### 手动启动

```bash
# 前台运行
code-server --port 8080 --bind-addr 0.0.0.0 /path/to/topo_system

# 后台运行
nohup code-server --port 8080 --bind-addr 0.0.0.0 /path/to/topo_system > ~/code-server.log 2>&1 &
```

### 使用 systemd 服务（推荐）

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

## 推荐扩展

在 VS Code Server 中安装以下扩展：

### Python 开发
- **Python** (ms-python.python)
- **Pylance** (ms-python.vscode-pylance)
- **Python Debugger** (ms-python.debugpy)

### Vue 开发
- **Vue - Official** (Vue.volar)
- **Volar** (Vue.volar)

### 通用工具
- **Prettier - Code formatter** (esbenp.prettier-vscode)
- **GitLens** (eamodio.gitlens)
- **Remote - SSH** (ms-vscode-remote.remote-ssh) - 本地 VS Code 使用

### 安装命令

```bash
# 在 code-server 终端中安装
code-server --install-extension ms-python.python
code-server --install-extension ms-python.vscode-pylance
code-server --install-extension Vue.volar
code-server --install-extension esbenp.prettier-vscode
```

---

## TOPO System 开发调试

### 打开项目

在 VS Code Server 中：
- File → Open Folder
- 选择 `/home/admin/topo_system` 或你的项目路径

### 启动后端

打开终端：
```bash
cd /home/admin/topo_system/backend
python run_app.py
```

### 启动前端

打开另一个终端：
```bash
cd /home/admin/topo_system/vue-frontend
npm run dev
```

### 访问应用

- **前端**: 点击弹出的 http://localhost:3000 链接，或使用服务器IP访问
- **后端 API**: http://localhost:5000/api

### 调试

1. **Python 后端调试**
   - 在代码中设置断点
   - 使用 VS Code 调试面板启动 "Python: Flask Backend"

2. **Vue 前端调试**
   - 在 Vue 组件中设置断点
   - 使用浏览器开发者工具查看

---

## 端口开放（服务器防火墙）

### Linux 防火墙

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

### 云服务器安全组

如果使用阿里云、腾讯云等：
- 登录云服务器控制台
- 配置安全组规则，开放 8080、3000、5000 端口

---

## 服务状态

| 项目 | 说明 |
|------|------|
| code-server | 运行在服务器上 |
| 端口 | 8080（默认） |
| 认证 | 可配置密码或无认证 |
| 工作目录 | /path/to/topo_system |

---

## 常用操作

### 查看日志

```bash
# 查看 code-server 日志
tail -f ~/code-server.log

# 或使用 journalctl
sudo journalctl -u code-server -f
```

### 停止服务

```bash
# 如果是前台运行
Ctrl+C

# 如果是后台运行
pkill code-server

# 如果使用 systemd
sudo systemctl stop code-server
```

### 重启服务

```bash
# 如果使用 systemd
sudo systemctl restart code-server

# 如果是手动运行
pkill code-server
code-server --port 8080 --bind-addr 0.0.0.0 /path/to/topo_system &
```

### 查看进程

```bash
ps aux | grep code-server
```

### 查看端口占用

```bash
netstat -tlnp | grep 8080
```

---

## 故障排查

### 问题 1: 无法访问 8080 端口

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

### 问题 2: code-server 启动失败

**解决**:
```bash
# 查看日志
journalctl -u code-server -f

# 检查端口占用
lsof -i :8080

# 重新启动
sudo systemctl restart code-server
```

### 问题 3: Python 环境找不到

**解决**:
```bash
# 检查 Python 路径
which python3

# 设置 Python 路径
# VS Code → Settings → Python: Default Interpreter Path
# 输入：/usr/bin/python3
```

### 问题 4: 页面加载缓慢或白屏

**解决**:
```bash
# 清除浏览器缓存
# 或使用无痕模式访问

# 检查网络连接
ping your-server-ip
```

---

## 配置信息

| 配置项 | 说明 |
|--------|------|
| 安装路径 | `/usr/bin/code-server` |
| 配置文件 | `~/.config/code-server/config.yaml` |
| 数据目录 | `~/.local/share/code-server` |
| 默认端口 | 8080 |
| 工作目录 | 启动时指定 |

---

## 安全建议

1. **启用密码认证**：生产环境务必设置密码
2. **使用 HTTPS**：通过 Nginx 反向代理配置 SSL
3. **限制访问 IP**：使用防火墙规则限制可访问的 IP
4. **定期更新**：保持 code-server 版本更新

### Nginx 反向代理配置 HTTPS

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

## TOPO System 项目结构

```
topo_system/
├── backend/                    # 后端Flask应用
│   ├── api/                   # API路由目录 (33个API模块)
│   ├── models/                # 数据模型定义
│   ├── services/              # 业务服务
│   ├── uploads/               # 文件上传目录
│   ├── backups/               # 数据库备份目录
│   ├── logs/                  # 日志文件目录
│   ├── instance/              # 数据库实例目录
│   ├── migrations/           # 数据库迁移脚本
│   ├── requirements.txt       # Python依赖
│   ├── run_app.py            # 应用启动脚本
│   ├── enhanced_app.py       # 增强应用入口
│   └── logging_config.py     # 日志配置
├── vue-frontend/             # 前端Vue应用
│   ├── src/                  # 源代码
│   │   ├── views/           # 页面组件 (63个页面)
│   │   ├── components/      # 通用组件
│   │   ├── router/          # 路由配置
│   │   ├── services/        # API服务
│   │   └── stores/          # 状态管理
│   ├── dist/                 # 构建输出目录
│   └── package.json          # Node.js依赖
└── README.md                # 项目说明文档
```

---

**安装时间**: 2026-03-16
**最后更新**: 2026-04
