# 🚀 AI 角色创建助手 - 部署指南

## 方法一：Streamlit Cloud 部署（推荐，免费）

### 第一步：准备 GitHub 仓库

1. **创建 GitHub 账号**
   - 访问：https://github.com
   - 如果已有账号，直接登录

2. **创建新仓库**
   - 点击右上角 "+" → "New repository"
   - Repository name: `character-creation-agent`
   - 选择 "Public"（公开）
   - 点击 "Create repository"

3. **上传代码到 GitHub**

在终端运行：

```bash
cd "/Users/mac017/cursor10 月/character_creation_agent"

# 初始化 Git
git init

# 添加所有文件（.env 会被 .gitignore 忽略）
git add .

# 提交
git commit -m "Initial commit: AI Character Creation Agent"

# 关联远程仓库（替换成你的 GitHub 用户名）
git remote add origin https://github.com/你的用户名/character-creation-agent.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

### 第二步：部署到 Streamlit Cloud

1. **访问 Streamlit Cloud**
   - 打开：https://share.streamlit.io/
   - 点击 "Sign up" 或 "Log in"
   - 使用 GitHub 账号登录

2. **创建新应用**
   - 点击 "New app"
   - 选择你的仓库：`character-creation-agent`
   - Main file path: `agent.py`
   - 点击 "Deploy"

3. **配置密钥（重要！）**
   - 在部署页面，点击右下角的 "⚙️ Settings"
   - 选择 "Secrets"
   - 复制粘贴以下内容：

```toml
# OpenAI API 配置
OPENAI_API_KEY = "sk-jrmjdqwnxpubbgwjcmoiqyewobkzhwvttyadvrgokrgnshvo"
OPENAI_BASE_URL = "https://api.siliconflow.cn/v1"

# 生图 API 配置
IMAGE_API_KEY = "sk-jrmjdqwnxpubbgwjcmoiqyewobkzhwvttyadvrgokrgnshvo"
IMAGE_API_URL = "https://api.siliconflow.cn/v1/images/generations"
IMAGE_MODEL = "black-forest-labs/FLUX.1-schnell"
```

   - 点击 "Save"

4. **等待部署完成**
   - 等待 2-5 分钟
   - 部署成功后会显示你的应用链接
   - 格式：`https://你的用户名-character-creation-agent-xxxxx.streamlit.app`

### 第三步：分享链接

现在你可以把链接分享给任何人了！🎉

---

## 方法二：本地部署（公网访问）

如果你想用自己的服务器：

### 使用 ngrok（临时公网链接）

1. **安装 ngrok**
```bash
brew install ngrok  # Mac
# 或访问 https://ngrok.com 下载
```

2. **运行应用**
```bash
streamlit run agent.py
```

3. **开启公网访问**
```bash
ngrok http 8501
```

4. **获取链接**
- ngrok 会显示一个公网链接，如：`https://xxxx.ngrok.io`
- 把这个链接分享给别人即可

⚠️ **注意**：ngrok 免费版链接会在重启后变化

---

## 方法三：Docker 部署

### 创建 Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "agent.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 部署到 Railway/Render

1. 访问 https://railway.app 或 https://render.com
2. 连接 GitHub 仓库
3. 自动部署

---

## 📝 部署前检查清单

- [ ] `.gitignore` 包含 `.env` 文件（不上传密钥）
- [ ] `requirements.txt` 包含所有依赖
- [ ] 在 Streamlit Cloud 配置了 secrets
- [ ] 测试应用运行正常
- [ ] API Key 有足够余额

---

## 🔒 安全建议

1. **不要上传 .env 文件到 GitHub**
   - `.gitignore` 已包含 `.env`
   - 密钥只在 Streamlit Cloud 的 Secrets 中配置

2. **监控 API 使用**
   - 定期检查 API 调用量
   - 设置使用限制

3. **添加使用说明**
   - 告诉用户这是 AI 角色创建工具
   - 说明需要 3 轮对话

---

## 🎉 部署完成后

你的应用链接格式：
```
https://你的用户名-character-creation-agent.streamlit.app
```

别人打开这个链接就能使用了！

---

## 💰 费用说明

- **Streamlit Cloud**：免费（有限制）
  - 单个应用限制：1GB 内存
  - 适合个人项目

- **API 费用**：
  - DeepSeek-V3：¥0.5/百万 tokens
  - FLUX.1-schnell：¥0.05-0.1/张图
  - 需要你自己的 API Key

---

## ⚠️ 常见问题

### Q: 部署后无法访问？
A: 检查是否配置了 Secrets，API Key 是否正确

### Q: 链接想要自定义？
A: Streamlit Cloud 免费版不支持自定义域名，可以升级 Pro 版

### Q: 多人同时访问会超额吗？
A: 是的，建议设置 API 使用限制或使用自己的服务器

---

需要帮助？随时联系我！😊

