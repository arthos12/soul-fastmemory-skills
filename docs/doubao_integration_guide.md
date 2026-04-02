
## 豆包模型集成步骤

### 当前状态
✅ 模型列表可获取 (110个模型)
❌ 模型调用不可用 (权限问题)

### 需要Jim在火山引擎控制台检查

1. **登录火山引擎控制台**
   - 访问: https://console.volcengine.com/
   - 使用API Key对应的账户登录

2. **检查豆包服务状态**
   - 进入「人工智能」->「豆包」
   - 确认服务已开通
   - 查看可用额度

3. **获取正确的调用信息**
   - 查看API文档
   - 获取正确的模型名称
   - 确认调用端点

4. **常见问题排查**
   - 服务未开通 -> 需要开通服务
   - 额度不足 -> 需要充值
   - 模型名称错误 -> 查看正确名称
   - 端点错误 -> 使用正确的API版本

### 测试命令（获取正确信息后）

```bash
# 1. 测试正确的模型名称
curl -X POST "https://ark.cn-beijing.volces.com/api/v3/chat/completions" \
  -H "Authorization: Bearer fbffb5c8-6497-47b7-b165-a2d3a25769c2" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "正确的模型名称",
    "messages": [{"role": "user", "content": "hello"}],
    "max_tokens": 10
  }'

# 2. 添加到OpenClaw配置
openclaw config set models.providers.doubao '{
  "baseUrl": "https://ark.cn-beijing.volces.com/api/v3",
  "apiKey": "fbffb5c8-6497-47b7-b165-a2d3a25769c2",
  "api": "openai-completions",
  "models": [{
    "id": "正确的模型名称",
    "name": "豆包模型",
    "contextWindow": 128000
  }]
}'

# 3. 切换模型
/model doubao/正确的模型名称
```

### 备用方案
如果豆包暂时不可用，可以：
1. 继续使用DeepSeek（当前可用）
2. 测试其他已配置的模型
3. 等待豆包服务开通
