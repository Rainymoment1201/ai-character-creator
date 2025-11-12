# 🚀 DeepSeek-V3 配置说明

## 📍 第一步：获取 DeepSeek API Key

1. 访问 DeepSeek 官网：https://platform.deepseek.com/
2. 注册/登录账号
3. 进入"API Keys"页面
4. 点击"创建 API Key"
5. 复制生成的 API Key（格式类似：`sk-xxxxxxxxxxxxxxxx`）

## 📝 第二步：填写 API Key

打开 `character_creation_agent` 目录下的 `.env` 文件：

```bash
cd "/Users/mac017/cursor10 月/character_creation_agent"
open .env  # Mac 系统
# 或者使用任何文本编辑器打开
```

将文件内容修改为（**替换成你的真实 API Key**）：

```env
# DeepSeek API 配置
OPENAI_API_KEY=sk-你的真实DeepSeek-API-Key
OPENAI_BASE_URL=https://api.deepseek.com

# 生图 API 配置（可选）
IMAGE_API_KEY=
IMAGE_API_URL=
```

### 示例

假设你的 API Key 是 `sk-abc123xyz789`，那么配置应该是：

```env
OPENAI_API_KEY=sk-abc123xyz789
OPENAI_BASE_URL=https://api.deepseek.com
```

**重要**：
- ✅ 不要有引号
- ✅ 等号两边不要有空格
- ✅ Key 前面有 `sk-` 前缀
- ❌ 不要分享你的 API Key 给任何人

## ✅ 第三步：验证配置

运行程序：

```bash
./start.sh
```

如果配置正确，程序会正常启动并打开浏览器。

### 可能遇到的问题

#### 1. 报错：`Invalid API Key`
**原因**：API Key 填写错误

**解决**：
- 检查 `.env` 文件中的 API Key 是否完整
- 确认在 DeepSeek 平台上该 Key 是否有效
- 重新生成一个新的 API Key

#### 2. 报错：`Connection Error`
**原因**：网络连接问题

**解决**：
- 检查网络连接
- 确认 DeepSeek API 服务是否正常（访问 https://platform.deepseek.com/）
- 如果在国内，DeepSeek API 是可以直接访问的，不需要代理

#### 3. 报错：`Rate Limit Exceeded`
**原因**：API 调用频率超限

**解决**：
- 等待一段时间再试
- 检查你的 DeepSeek 账户余额
- 升级账户套餐

## 💰 费用说明

DeepSeek-V3 的定价（截至当前）：
- **输入**：约 ¥0.5/百万 tokens（非常便宜！）
- **输出**：约 ¥2/百万 tokens

普通对话创建一个角色大约消耗 5000-10000 tokens，成本约 ¥0.01-0.02（1-2 分钱）

## 🎯 为什么选择 DeepSeek-V3？

✅ **价格便宜**：比 GPT-4 便宜 90% 以上  
✅ **中文友好**：对中文理解和生成能力极强  
✅ **性能强劲**：DeepSeek-V3 的性能接近 GPT-4  
✅ **国内可用**：不需要代理，直接访问  
✅ **响应快速**：推理速度快，用户体验好  

## 📞 需要帮助？

如果还有问题：

1. **检查 .env 文件格式**：确保没有多余的空格和引号
2. **查看终端错误信息**：启动时的错误信息会提示具体问题
3. **访问 DeepSeek 文档**：https://platform.deepseek.com/docs

---

配置完成后，运行 `./start.sh` 即可开始使用！🎉

