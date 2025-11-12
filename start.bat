@echo off
chcp 65001 > nul
echo 🎨 AI 角色创建助手
echo ==================
echo.

REM 检查是否存在 .env 文件
if not exist .env (
    echo ⚠️  未找到 .env 文件
    echo 📝 请先复制 config_example.env 为 .env 并配置你的 API Key
    echo.
    echo 可以运行以下命令：
    echo   copy config_example.env .env
    echo   然后编辑 .env 文件填入你的 API Key
    echo.
    pause
    exit /b 1
)

REM 检查是否安装了依赖
pip show streamlit > nul 2>&1
if errorlevel 1 (
    echo 📦 正在安装依赖...
    pip install -r requirements.txt
)

echo 🚀 启动程序...
echo.
streamlit run agent.py

