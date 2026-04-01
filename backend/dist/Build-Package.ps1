# TOPO System 完整打包脚本
# 运行方式: 右键 -> 使用PowerShell运行

param(
    [switch]$SkipFrontend,
    [switch]$SkipBackend,
    [switch]$CreateInstaller
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   TOPO System 打包构建脚本" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$BackendDir = Join-Path $ProjectRoot "backend"
$FrontendDir = Join-Path $ProjectRoot "vue-frontend"
$DistDir = Join-Path $BackendDir "dist"

# 检查Python
Write-Host "[检查] Python 环境..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  [错误] 未找到Python，请先安装Python 3.8+" -ForegroundColor Red
    Write-Host "  下载地址: https://www.python.org/downloads/" -ForegroundColor Yellow
    pause
    exit 1
}

# 检查Node.js
Write-Host "[检查] Node.js 环境..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "  Node.js $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  [错误] 未找到Node.js，请先安装Node.js 14+" -ForegroundColor Red
    Write-Host "  下载地址: https://nodejs.org/" -ForegroundColor Yellow
    pause
    exit 1
}

# 步骤1: 构建前端
if (-not $SkipFrontend) {
    Write-Host ""
    Write-Host "[步骤1] 构建前端..." -ForegroundColor Cyan
    Write-Host "----------------------------------------------" -ForegroundColor DarkGray

    Set-Location $FrontendDir

    if (-not (Test-Path "node_modules")) {
        Write-Host "  安装前端依赖..." -ForegroundColor Yellow
        npm install
        if ($LASTEXITCODE -ne 0) { throw "npm install failed" }
    }

    Write-Host "  构建生产版本..." -ForegroundColor Yellow
    npm run build
    if ($LASTEXITCODE -ne 0) { throw "npm run build failed" }

    Write-Host "  前端构建完成!" -ForegroundColor Green
} else {
    Write-Host "[跳过] 前端构建" -ForegroundColor Gray
}

# 步骤2: 安装后端依赖
Write-Host ""
Write-Host "[步骤2] 安装后端依赖..." -ForegroundColor Cyan
Write-Host "----------------------------------------------" -ForegroundColor DarkGray

Set-Location $BackendDir
pip install -r requirements.txt -q
pip install pyinstaller pywin32 -q

Write-Host "  后端依赖安装完成!" -ForegroundColor Green

# 步骤3: 打包后端
if (-not $SkipBackend) {
    Write-Host ""
    Write-Host "[步骤3] 使用PyInstaller打包后端..." -ForegroundColor Cyan
    Write-Host "----------------------------------------------" -ForegroundColor DarkGray

    Set-Location $DistDir

    if (Test-Path "TOPOSystem") {
        Remove-Item -Recurse -Force "TOPOSystem"
    }
    if (Test-Path "TOPOSystem.exe") {
        Remove-Item -Force "TOPOSystem.exe"
    }

    Write-Host "  运行PyInstaller..." -ForegroundColor Yellow
    pyinstaller run_app.spec --clean

    if ($LASTEXITCODE -ne 0) { throw "PyInstaller打包失败" }
    Write-Host "  后端打包完成!" -ForegroundColor Green
} else {
    Write-Host "[跳过] 后端打包" -ForegroundColor Gray
}

# 步骤4: 复制前端文件
Write-Host ""
Write-Host "[步骤4] 复制前端文件到后端目录..." -ForegroundColor Cyan
Write-Host "----------------------------------------------" -ForegroundColor DarkGray

$FrontendDist = Join-Path $FrontendDir "dist"
$TargetFrontend = Join-Path $DistDir "TOPOSystem\frontend"

if (Test-Path $FrontendDist) {
    if (-not (Test-Path $TargetFrontend)) {
        New-Item -ItemType Directory -Path $TargetFrontend -Force | Out-Null
    }
    Copy-Item -Path "$FrontendDist\*" -Destination $TargetFrontend -Recurse -Force
    Write-Host "  前端文件已复制!" -ForegroundColor Green
} else {
    Write-Host "  [警告] 未找到前端构建文件，请先运行前端构建" -ForegroundColor Yellow
}

# 步骤5: 创建必要目录
Write-Host ""
Write-Host "[步骤5] 创建数据目录..." -ForegroundColor Cyan
Write-Host "----------------------------------------------" -ForegroundColor DarkGray

$TargetDirs = @("instance", "uploads", "logs", "backups")
foreach ($dir in $TargetDirs) {
    $path = Join-Path $DistDir "TOPOSystem\$dir"
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
    }
    Write-Host "  $dir\" -ForegroundColor Gray
}
Write-Host "  目录创建完成!" -ForegroundColor Green

# 步骤6: 创建安装包
if ($CreateInstaller) {
    Write-Host ""
    Write-Host "[步骤6] 检查Inno Setup..." -ForegroundColor Cyan
    Write-Host "----------------------------------------------" -ForegroundColor DarkGray

    $isccPaths = @(
        "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        "C:\Program Files\Inno Setup 6\ISCC.exe",
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
    )

    $iscc = $null
    foreach ($path in $isccPaths) {
        if (Test-Path $path) {
            $iscc = $path
            break
        }
    }

    if ($null -eq $iscc) {
        Write-Host "  [警告] 未找到Inno Setup" -ForegroundColor Yellow
        Write-Host "  请手动安装Inno Setup: https://jrsoftware.org/isinfo.php" -ForegroundColor Yellow
        Write-Host "  安装后运行: iscc setup.iss" -ForegroundColor Yellow
    } else {
        Write-Host "  找到Inno Setup: $iscc" -ForegroundColor Green
        Write-Host "  编译安装脚本..." -ForegroundColor Yellow

        $installerDir = Join-Path $DistDir "installer"
        if (-not (Test-Path $installerDir)) {
            New-Item -ItemType Directory -Path $installerDir -Force | Out-Null
        }

        & $iscc (Join-Path $DistDir "setup.iss")
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  安装包创建完成!" -ForegroundColor Green
        } else {
            Write-Host "  [错误] 安装包创建失败" -ForegroundColor Red
        }
    }
}

# 完成
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   打包完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "打包文件位于: $DistDir\TOPOSystem" -ForegroundColor White
Write-Host ""
Write-Host "目录结构:" -ForegroundColor White
Write-Host "  TOPOSystem/" -ForegroundColor Gray
Write-Host "  ├── TOPOSystem.exe    (主程序)" -ForegroundColor Gray
Write-Host "  ├── frontend/         (前端文件)" -ForegroundColor Gray
Write-Host "  ├── instance/         (数据库)" -ForegroundColor Gray
Write-Host "  ├── uploads/          (上传文件)" -ForegroundColor Gray
Write-Host "  ├── logs/             (日志)" -ForegroundColor Gray
Write-Host "  └── backups/          (备份)" -ForegroundColor Gray
Write-Host ""

if (-not $CreateInstaller) {
    Write-Host "如需创建安装包，请安装Inno Setup后使用 -CreateInstaller 参数运行" -ForegroundColor Yellow
}

Write-Host ""
pause
