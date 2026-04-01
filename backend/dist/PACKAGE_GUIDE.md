# TOPO System 打包说明

本文档说明如何将TOPO系统打包成Windows可执行文件和安装包。

## 系统要求

- Windows 10/11 (64位)
- Python 3.8+ (用于打包过程)
- Node.js 14+ (用于打包过程)
- Inno Setup 6 (可选，用于创建安装包)

## 打包步骤

### 方法一：一键打包（推荐）

1. 双击运行 `Build-Package.bat`
2. 等待打包完成（约10-15分钟）
3. 打包结果在 `backend\dist\TOPOSystem\` 目录

### 方法二：分步打包

1. 先构建前端：
   ```bash
   cd vue-frontend
   npm install
   npm run build
   ```

2. 打包后端：
   ```bash
   cd backend
   pip install -r requirements.txt
   pip install pyinstaller pywin32
   cd dist
   pyinstaller run_app.spec --clean
   ```

3. 复制前端到后端目录：
   ```bash
   xcopy /s /y ..\..\vue-frontend\dist\* TOPOSystem\frontend\
   ```

### 方法三：PowerShell脚本打包

```powershell
cd backend\dist
.\Build-Package.ps1
```

### 创建安装包（可选）

1. 下载安装 Inno Setup 6: https://jrsoftware.org/isinfo.php

2. 编译安装脚本：
   ```bash
   cd backend\dist
   iscc setup.iss
   ```

3. 安装包生成在 `backend\dist\installer\TOPOSystem_Setup_v1.0.0.exe`

## 打包结果

打包完成后，目录结构如下：

```
backend\dist\TOPOSystem\
├── TOPOSystem.exe      # 主程序（双击运行）
├── python*.dll          # Python运行时
├── libs\                # 依赖库
├── frontend\            # Vue前端文件
│   ├── index.html
│   ├── assets\
│   └── ...
├── instance\            # 数据库目录（首次运行自动创建）
├── uploads\             # 上传文件目录
├── logs\                # 日志目录
└── backups\             # 备份目录
```

## 安装程序功能

使用Inno Setup创建的安装包具备以下功能：

- [x] 桌面快捷方式
- [x] 开始菜单项
- [x] 卸载程序
- [x] 自动创建必要目录
- [x] 自定义安装路径

## 首次运行

1. 双击 `TOPOSystem.exe`
2. 程序会自动初始化数据库
3. 默认管理员账户：
   - 用户名: `admin`
   - 密码: `admin123`

**重要**: 首次使用后请立即修改默认密码！

## 系统功能

打包后的桌面版包含以下功能模块：

- 项目管理
- Bug跟踪管理
- 物料管理系统（物料、仓库、库存、序列号）
- 合同管理系统
- 配送跟踪系统
- 考勤管理系统（打卡、请假、加班、班次管理）
- 任务管理
- 需求管理
- 测试管理
- 用户权限管理
- 知识库系统
- 通知系统
- 统计报表
- 系统监控
- 审计日志

## 注意事项

1. 杀毒软件可能误报，请添加信任
2. 建议关闭杀毒软件后再打包
3. 打包过程需要管理员权限
4. 确保磁盘空间充足（至少2GB）

## 故障排除

### PyInstaller 打包失败

- 确保所有依赖已安装
- 尝试以管理员身份运行
- 检查是否有特殊字符路径

### 前端构建失败

- 删除 `node_modules` 后重新 `npm install`
- 确保 Node.js 版本 >= 14

### 安装包无法创建

- 确认已安装 Inno Setup 6
- 检查 `setup.iss` 路径是否正确

## 技术支持

如有问题，请联系系统管理员。

---

**版本**: v1.4.0
**最后更新**: 2026-04
