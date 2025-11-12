# 🎨 硅基流动生图 API 配置说明

## ✅ 已完成配置

你的 `.env` 文件中已经配置好了硅基流动的生图API！

```env
# SiliconFlow API 配置（支持 DeepSeek 和生图模型）
OPENAI_API_KEY=sk-jrmjdqwnxpubbgwjcmoiqyewobkzhwvttyadvrgokrgnshvo
OPENAI_BASE_URL=https://api.siliconflow.cn/v1

# 生图 API 配置（使用硅基流动）
IMAGE_API_KEY=sk-jrmjdqwnxpubbgwjcmoiqyewobkzhwvttyadvrgokrgnshvo
IMAGE_API_URL=https://api.siliconflow.cn/v1/images/generations
IMAGE_MODEL=Qwen/Qwen-Image-Edit-2509
```

---

## 🔧 配置说明

### 1. IMAGE_API_KEY（生图 API 密钥）
- **值**：`sk-jrmjdqwnxpubbgwjcmoiqyewobkzhwvttyadvrgokrgnshvo`
- **说明**：你的硅基流动 API Key
- **获取方式**：https://cloud.siliconflow.cn/account/ak

### 2. IMAGE_API_URL（生图 API 地址）
- **值**：`https://api.siliconflow.cn/v1/images/generations`
- **说明**：硅基流动的图像生成 API 端点
- **固定地址**：无需修改

### 3. IMAGE_MODEL（生图模型）
- **值**：`Qwen/Qwen-Image-Edit-2509`
- **说明**：千问图像编辑模型 2509 版本
- **其他可选模型**：
  - `stabilityai/stable-diffusion-xl-base-1.0`
  - `stabilityai/stable-diffusion-3-5-large`
  - `black-forest-labs/FLUX.1-schnell`

---

## 📋 API 参数说明

生图时使用的参数：

```python
{
    "model": "Qwen/Qwen-Image-Edit-2509",     # 模型名称
    "prompt": "英文提示词...",                 # 生图提示词
    "image_size": "1024x1024",                # 图像尺寸
    "num_inference_steps": 20,                # 推理步数
    "guidance_scale": 7.5                     # 引导系数
}
```

### 可调整参数

#### image_size（图像尺寸）
- `512x512` - 小尺寸，生成快
- `1024x1024` - 标准尺寸（当前配置）
- `1024x1536` - 竖版
- `1536x1024` - 横版

#### num_inference_steps（推理步数）
- `10-20` - 快速生成，质量一般
- `20-30` - 标准质量（当前配置：20）
- `30-50` - 高质量，生成慢

#### guidance_scale（引导系数）
- `5.0-7.0` - 较自由，创意性强
- `7.0-9.0` - 平衡（当前配置：7.5）
- `9.0-15.0` - 严格遵循提示词

---

## 🎯 工作流程

### 1. 用户对话收集信息
```
用户：我想要一个可爱的猫娘
Agent：好的！什么画风呢？
用户：二次元风格，粉色长发
...（持续3轮对话）
```

### 2. 点击"帮我生图"按钮
```
[🎨 帮我生图] ← 点击
```

### 3. Agent 生成 SD 提示词
```
提取对话信息 → 生成英文关键词提示词
例如：
masterpiece, best quality, 1girl, anime style, 
long pink hair, blue eyes, cat ears, white dress, 
gentle smile, standing
|||
lowres, bad anatomy, bad hands, text, error...
```

### 4. 调用硅基流动 API
```python
POST https://api.siliconflow.cn/v1/images/generations
Headers: {
    "Authorization": "Bearer sk-jrmjdqw...",
    "Content-Type": "application/json"
}
Body: {
    "model": "Qwen/Qwen-Image-Edit-2509",
    "prompt": "masterpiece, best quality, 1girl...",
    "image_size": "1024x1024",
    ...
}
```

### 5. 返回图像 URL
```json
{
    "images": [
        {
            "url": "https://siliconflow-oss.cn-beijing.aliyuncs.com/..."
        }
    ]
}
```

### 6. 显示生成的图像
```
✅ 图像生成完成！
[显示图像]
```

---

## 🔍 API 调用代码

在 `agent.py` 中的实现：

```python
def call_image_generation_api(prompt_text):
    """调用硅基流动生图 API"""
    import requests
    
    # 从环境变量读取配置
    api_key = os.getenv("IMAGE_API_KEY")
    api_url = os.getenv("IMAGE_API_URL")
    model = os.getenv("IMAGE_MODEL")
    
    # 提取正面提示词
    if "|||" in prompt_text:
        positive_prompt = prompt_text.split("|||")[0].strip()
    else:
        positive_prompt = prompt_text.strip()
    
    # 构建请求
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "prompt": positive_prompt,
        "image_size": "1024x1024",
        "num_inference_steps": 20,
        "guidance_scale": 7.5
    }
    
    # 发送请求
    response = requests.post(api_url, headers=headers, json=payload)
    result = response.json()
    
    # 返回图像 URL
    return result["images"][0]["url"]
```

---

## 💰 费用说明

硅基流动的 Qwen/Qwen-Image-Edit-2509 模型：
- **价格**：约 ¥0.05-0.1 / 张（1024x1024）
- **速度**：约 10-30 秒 / 张
- **质量**：高质量 AI 生成图像

---

## ⚠️ 常见问题

### 1. 生图失败：API Key 无效
**问题**：`❌ 生图失败：401 Unauthorized`

**解决**：
- 检查 `.env` 文件中的 `IMAGE_API_KEY` 是否正确
- 确认 API Key 是否有效（登录硅基流动查看）
- 确认 API Key 前面有 `sk-` 前缀

### 2. 生图失败：余额不足
**问题**：`❌ 生图失败：insufficient balance`

**解决**：
- 登录硅基流动充值：https://cloud.siliconflow.cn/account/balance
- 查看账户余额是否充足

### 3. 生图失败：超时
**问题**：`❌ 生图失败：timeout`

**解决**：
- 检查网络连接
- 生图需要 10-30 秒，请耐心等待
- 可以增加 timeout 参数（当前60秒）

### 4. 生图质量不满意
**问题**：生成的图像不符合预期

**解决**：
- 优化提示词（更具体的描述）
- 调整 `num_inference_steps`（增加到30-50）
- 调整 `guidance_scale`（增加到9-12）
- 尝试不同的模型

---

## 🔧 自定义参数

如果想修改生图参数，编辑 `agent.py` 中的 `call_image_generation_api` 函数：

```python
payload = {
    "model": model,
    "prompt": positive_prompt,
    "image_size": "1024x1024",        # 改为 "512x512" 或 "1536x1024"
    "num_inference_steps": 20,        # 改为 30 或 40
    "guidance_scale": 7.5             # 改为 9.0 或 10.0
}
```

---

## 🚀 测试生图功能

### 1. 启动应用
```bash
python3 -m streamlit run agent.py
```

### 2. 开始对话
```
你：我想先生成图像
Agent：好的！你想创建什么类型的角色呢？
```

### 3. 描述角色外观
```
你：可爱的猫娘，二次元风格
你：粉色长发，蓝色眼睛
你：穿白色连衣裙
```

### 4. 点击生图
```
[🎨 帮我生图] ← 点击

⏳ 正在调用硅基流动生图 API（Qwen/Qwen-Image-Edit-2509），请稍候...
✅ 图像生成完成！
[显示生成的图像]
```

---

## 📖 参考链接

- **硅基流动官网**：https://cloud.siliconflow.cn/
- **API 文档**：https://docs.siliconflow.cn/api-reference/image-generation
- **模型列表**：https://cloud.siliconflow.cn/models
- **账户管理**：https://cloud.siliconflow.cn/account

---

**生图功能已经配置完成，可以直接使用了！** 🎉

你的 API Key 和配置都已经设置好，现在可以：
1. 启动应用
2. 和 Agent 对话3轮+
3. 点击"帮我生图"
4. 等待10-30秒
5. 获得高质量的角色图像！

有任何问题随时告诉我~ 😊

