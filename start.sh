#!/bin/bash

# AI 角色创建助手 启动脚本

echo "🎨 AI 角色创建助手"
echo "=================="
echo ""

# 检查是否存在 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  未找到 .env 文件"
    echo "📝 请先复制 config_example.env 为 .env 并配置你的 API Key"
    echo ""
    echo "可以运行以下命令："
    echo "  cp config_example.env .env"
    echo "  然后编辑 .env 文件填入你的 API Key"
    echo ""
    exit 1
fi

# 检查是否安装了依赖
if ! pip show streamlit > /dev/null 2>&1; then
    echo "📦 正在安装依赖..."
    pip install -r requirements.txt
fi

echo "🚀 启动程序..."
echo ""
streamlit run agent.py

