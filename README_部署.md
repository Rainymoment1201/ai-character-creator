# 🚀 部署到 Streamlit Cloud

## 方法 1：Streamlit Cloud（免费，推荐）

### 第 1 步：准备 GitHub 仓库

1. 访问 https://github.com/
2. 登录你的 GitHub 账号（如果没有就注册一个）
3. 点击右上角 "+" → "New repository"
4. 填写：
   - Repository name: `character-creation-agent`
   - 选择 Public（公开）
   - 点击 "Create repository"

### 第 2 步：上传代码到 GitHub

在项目目录打开终端，运行：

```bash
cd "/Users/mac017/cursor10 月/character_creation_agent"

# 初始化 Git
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit"

# 添加远程仓库（替换成你的 GitHub 用户名）
git remote add origin https://github.com/你的用户名/character-creation-agent.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

### 第 3 步：部署到 Streamlit Cloud

1. 访问 https://share.streamlit.io/
2. 点击 "Sign in" 用 GitHub 登录
3. 点击 "New app"
4. 选择：
   - Repository: `你的用户名/character-creation-agent`
   - Branch: `main`
   - Main file path: `agent.py`
5. 点击 "Advanced settings"
6. 在 "Secrets" 中添加（复制粘贴下面内容）：

```toml
OPENAI_API_KEY = "sk-jrmjdqwnxpubbgwjcmoiqyewobkzhwvttyadvrgokrgnshvo"
OPENAI_BASE_URL = "https://api.siliconflow.cn/v1"

IMAGE_API_KEY = "sk-jrmjdqwnxpubbgwjcmoiqyewobkzhwvttyadvrgokrgnshvo"
IMAGE_API_URL = "https://api.siliconflow.cn/v1/images/generations"
IMAGE_MODEL = "black-forest-labs/FLUX.1-schnell"
```

7. 点击 "Deploy"
8. 等待 2-3 分钟部署完成

### 第 4 步：获取网址

部署完成后，你会得到一个网址，类似：
```
https://你的用户名-character-creation-agent-xxxx.streamlit.app
```

把这个网址分享给别人，他们就能直接使用了！

---

## 方法 2：Hugging Face Spaces（免费）

### 第 1 步：注册 Hugging Face

1. 访问 https://huggingface.co/join
2. 注册账号

### 第 2 步：创建 Space

1. 访问 https://huggingface.co/spaces
2. 点击 "Create new Space"
3. 填写：
   - Space name: `character-creation-agent`
   - License: MIT
   - Select the SDK: Streamlit
   - 点击 "Create Space"

### 第 3 步：上传文件

在 Space 页面：
1. 点击 "Files" → "Add file" → "Upload files"
2. 上传以下文件：
   - `agent.py`
   - `prompts.py`
   - `requirements.txt`
3. 点击 "Commit changes to main"

### 第 4 步：配置环境变量

1. 点击 "Settings"
2. 在 "Repository secrets" 添加：
   - Name: `OPENAI_API_KEY`, Value: `sk-jrmjdqw...`
   - Name: `OPENAI_BASE_URL`, Value: `https://api.siliconflow.cn/v1`
   - Name: `IMAGE_API_KEY`, Value: `sk-jrmjdqw...`
   - Name: `IMAGE_API_URL`, Value: `https://api.siliconflow.cn/v1/images/generations`
   - Name: `IMAGE_MODEL`, Value: `black-forest-labs/FLUX.1-schnell`

### 第 5 步：访问网址

网址是：`https://huggingface.co/spaces/你的用户名/character-creation-agent`

---

## 方法 3：ngrok（临时方案，立即可用）

如果你只是想快速测试，可以用 ngrok：

```bash
# 1. 安装 ngrok
brew install ngrok

# 2. 在一个终端启动应用
cd "/Users/mac017/cursor10 月/character_creation_agent"
python3 -m streamlit run agent.py

# 3. 在另一个终端运行 ngrok
ngrok http 8501
```

会得到一个临时网址，例如：
```
https://xxxx-xx-xx-xx-xx.ngrok-free.app
```

**注意**：这个网址只在你的电脑运行时有效，关闭就失效了。

---

## 📊 方案对比

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| Streamlit Cloud | 免费、稳定、永久 | 需要 GitHub | ⭐⭐⭐⭐⭐ |
| Hugging Face | 免费、AI 社区 | 配置稍复杂 | ⭐⭐⭐⭐ |
| ngrok | 立即可用 | 临时网址 | ⭐⭐⭐ |

---

## 🎯 推荐流程

**最简单的部署方案（5 分钟完成）：**

1. 去 GitHub 创建账号和仓库
2. 上传代码到 GitHub
3. 去 Streamlit Cloud 部署
4. 获得永久网址
5. 分享给别人使用

我可以一步步指导你完成！需要我帮忙吗？😊

