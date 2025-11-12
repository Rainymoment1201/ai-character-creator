# -*- coding: utf-8 -*-
"""测试 API 配置是否正确"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

print("🔍 正在测试 API 配置...\n")

# 显示配置信息
api_key = os.getenv("OPENAI_API_KEY", "")
base_url = os.getenv("OPENAI_BASE_URL", "")

print(f"API Key: {api_key[:20]}...{api_key[-10:] if len(api_key) > 30 else ''}")
print(f"Base URL: {base_url}")
print()

# 初始化客户端
client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

# 测试调用
print("📡 正在发送测试请求...")
try:
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3",
        messages=[
            {"role": "user", "content": "你好，请回复'测试成功'"}
        ],
        max_tokens=50
    )
    
    reply = response.choices[0].message.content
    print(f"✅ API 配置正确！")
    print(f"📨 模型回复: {reply}")
    print()
    print("🎉 配置验证通过！可以开始使用角色创建 Agent 了！")
    
except Exception as e:
    print(f"❌ API 调用失败！")
    print(f"错误信息: {str(e)}")
    print()
    print("请检查：")
    print("1. API Key 是否正确")
    print("2. 网络连接是否正常")
    print("3. SiliconFlow 账户是否有余额")

