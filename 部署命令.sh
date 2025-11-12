#!/bin/bash

echo "🚀 AI角色创建助手 - 部署脚本"
echo "================================"
echo ""
echo "请先完成以下步骤："
echo "1. 访问 https://github.com/new 创建仓库"
echo "2. 仓库名称：ai-character-creator"
echo "3. 选择 Public（公开）"
echo "4. 点击 Create repository"
echo ""
echo "然后输入你的 GitHub 用户名："
read -p "GitHub用户名: " username

if [ -z "$username" ]; then
    echo "❌ 用户名不能为空"
    exit 1
fi

echo ""
echo "正在推送代码到 GitHub..."

# 设置远程仓库
git remote remove origin 2>/dev/null
git remote add origin https://github.com/$username/ai-character-creator.git

# 推送代码
git branch -M main
git push -u origin main

echo ""
echo "✅ 代码已推送到 GitHub！"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "接下来："
echo "1. 访问 https://share.streamlit.io/"
echo "2. 用 GitHub 登录"
echo "3. 点击 'New app'"
echo "4. 选择仓库：$username/ai-character-creator"
echo "5. Branch: main"
echo "6. Main file: agent.py"
echo "7. 点击 'Advanced settings' → 'Secrets'"
echo "8. 复制粘贴以下内容："
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat << 'EOF'
OPENAI_API_KEY = "sk-jrmjdqwnxpubbgwjcmoiqyewobkzhwvttyadvrgokrgnshvo"
OPENAI_BASE_URL = "https://api.siliconflow.cn/v1"
IMAGE_API_KEY = "sk-jrmjdqwnxpubbgwjcmoiqyewobkzhwvttyadvrgokrgnshvo"
IMAGE_API_URL = "https://api.siliconflow.cn/v1/images/generations"
IMAGE_MODEL = "black-forest-labs/FLUX.1-schnell"
EOF
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "9. 点击 'Deploy'"
echo "10. 等待2-3分钟"
echo "11. 完成！你会得到一个网址可以分享 🎉"
echo ""

