@echo off
chcp 65001 > nul
echo 🚀 微信工具箱 - 一键打包（虚拟环境版本）
echo.

REM 检查虚拟环境
if not exist "venv\Scripts\python.exe" (
    echo ❌ 未找到虚拟环境 venv，请先创建虚拟环境
    echo 💡 运行以下命令创建虚拟环境：
    echo    python -m venv venv
    echo    venv\Scripts\activate
    echo    pip install -r requirements.txt
    pause
    exit /b 1
)

REM 激活虚拟环境并检查依赖
echo ✅ 找到虚拟环境，正在激活...
call venv\Scripts\activate.bat

REM 检查 PySide6 是否安装
venv\Scripts\python.exe -c "import PySide6; print('✅ PySide6 版本:', PySide6.__version__)" 2>nul
if errorlevel 1 (
    echo ❌ 虚拟环境中未安装 PySide6
    echo 💡 请运行: pip install -r requirements.txt
    pause
    exit /b 1
)

REM 使用虚拟环境的 Python 执行无控制台打包脚本
echo 🔨 使用虚拟环境执行无控制台打包...
venv\Scripts\python.exe build_no_console.py

REM 询问是否打开结果目录
if exist "dist\KiwiKit.exe" (
    echo.
    set /p choice="是否打开输出目录? (y/n): "
    if /i "%choice%"=="y" explorer dist
)

pause