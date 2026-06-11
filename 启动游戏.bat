@echo off
chcp 65001 >nul 2>&1
echo ================================
echo   桂子山秘境探险 - 启动脚本
echo ================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查依赖是否安装
python -c "import pygame" >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败，请手动运行: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

echo [启动] 正在启动游戏...
python main.py

if errorlevel 1 (
    echo.
    echo [错误] 游戏运行出错，请检查上方错误信息
    pause
)
