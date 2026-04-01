@echo off
chcp 65001 >nul
echo ==========================================
echo    TOPO System 打包脚本
echo ==========================================
echo.

:: 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

:: 检查Node.js环境
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Node.js，请先安装Node.js 14+
    pause
    exit /b 1
)

:: 获取当前目录
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo [步骤1] 检查并安装前端依赖...
cd ..\..\vue-frontend
if not exist "node_modules" (
    echo    安装前端依赖中...
    call npm install
) else (
    echo    前端依赖已安装
)

echo.
echo [步骤2] 构建前端...
if not exist "dist" (
    mkdir dist
)
call npm run build
if errorlevel 1 (
    echo [错误] 前端构建失败
    pause
    exit /b 1
)
echo    前端构建完成

echo.
echo [步骤3] 安装后端依赖...
cd ..\backend
pip install -r requirements.txt -q

echo.
echo [步骤4] 使用PyInstaller打包后端...
cd dist
if exist "TOPOSystem" rmdir /s /q "TOPOSystem"
if exist "TOPOSystem.exe" del /q "TOPOSystem.exe"

pyinstaller run_app.spec --clean
if errorlevel 1 (
    echo [错误] PyInstaller打包失败
    pause
    exit /b 1
)
echo    后端打包完成

echo.
echo [步骤5] 复制前端到后端目录...
xcopy /s /y ..\..\vue-frontend\dist\* TOPOSystem\frontend\ >nul
echo    前端已复制

echo.
echo [步骤6] 创建数据目录...
if not exist "TOPOSystem\instance" mkdir "TOPOSystem\instance"
if not exist "TOPOSystem\uploads" mkdir "TOPOSystem\uploads"
if not exist "TOPOSystem\logs" mkdir "TOPOSystem\logs"
if not exist "TOPOSystem\backups" mkdir "TOPOSystem\backups"
echo    目录创建完成

echo.
echo ==========================================
echo    打包完成！
echo ==========================================
echo.
echo 打包文件位于: %SCRIPT_DIR%TOPOSystem
echo.
echo 如需创建安装包，请:
echo 1. 安装 Inno Setup: https://jrsoftware.org/isinfo.php
echo 2. 运行: iscc setup.iss
echo.
pause
