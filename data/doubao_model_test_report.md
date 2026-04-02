# 豆包模型测试报告

## 📅 测试时间
2026-03-20

## 🔑 API Key
`fbffb5c8-6497-47b7-b165-a2d3a25769c2`

## 📊 测试结果

### 1. 模型列表获取 ✅ 成功
- **端点**: `https://ark.cn-beijing.volces.com/api/v3/models`
- **状态**: 成功获取110个模型
- **发现模型**:
  - `doubao-lite-128k-240428`
  - `doubao-pro-128k-240515`
  - `doubao-lite-32k-240428`
  - `doubao-pro-4k-240515`
  - `doubao-lite-4k-240328`
  - 等110个模型

### 2. 模型调用测试 ❌ 失败
- **端点**: `https://ark.cn-beijing.volces.com/api/v3/chat/completions`
- **状态**: 所有模型调用返回404错误
- **错误信息**: `"The model or endpoint does not exist or you do not have access to it"`

### 3. 可能原因分析

#### 可能性1: API Key权限不足
- Key可能只有模型列表读取权限
- 缺少模型调用权限
- 需要开通相应的服务

#### 可能性2: 模型名称格式问题
- 列表中的模型ID可能不是调用时的名称
- 需要查看具体的调用文档

#### 可能性3: 端点版本问题
- 可能需要使用不同的API版本
- 如 `/api/v1` 或 `/api/v2`

#### 可能性4: 服务未开通
- 账户可能未开通豆包模型调用服务
- 需要在火山引擎控制台开通

## 🔧 建议下一步

### 立即行动
1. **检查火山引擎控制台**
   - 确认豆包服务已开通
   - 查看可用的模型和端点

2. **查看API文档**
   - 获取正确的调用格式
   - 确认模型名称和端点

3. **测试其他端点**
   ```bash
   # 尝试不同版本
   https://ark.cn-beijing.volces.com/api/v1/chat/completions
   https://ark.cn-beijing.volces.com/api/v2/chat/completions
   
   # 尝试不同模型名称格式
   "Doubao-Lite"
   "doubao_lite_128k"
   "seed-lite"
   ```

### 备用方案
1. **使用其他模型**
   - 继续使用DeepSeek（当前可用）
   - 测试其他支持的模型

2. **申请正确权限**
   - 联系火山引擎技术支持
   - 申请模型调用权限

## 📝 OpenClaw配置模板

一旦找到可用的模型，可以使用以下配置：

```json
{
  "providers": {
    "doubao": {
      "baseUrl": "https://ark.cn-beijing.volces.com/api/v3",
      "apiKey": "fbffb5c8-6497-47b7-b165-a2d3a25769c2",
      "api": "openai-completions",
      "models": [
        {
          "id": "doubao-lite-128k-240428",  // 需要替换为实际可用的模型ID
          "name": "豆包 Lite",
          "reasoning": false,
          "input": ["text"],
          "cost": {
            "input": 0.000,
            "output": 0.000,
            "cacheRead": 0,
            "cacheWrite": 0
          },
          "contextWindow": 128000,
          "maxTokens": 4000,
          "supportsJson": true,
          "supportsTools": false,
          "supportsVision": false,
          "supportsAudio": false
        }
      ]
    }
  }
}
```

## 📞 技术支持

1. **火山引擎文档**: https://www.volcengine.com/docs/6459/75268
2. **豆包模型文档**: https://www.volcengine.com/docs/82379/1263503
3. **技术支持**: 火山引擎控制台 - 工单系统

## ✅ 当前状态

- **模型列表**: ✅ 可获取
- **模型调用**: ❌ 不可用（权限问题）
- **建议**: 检查火山引擎控制台，确认服务开通状态

## 🎯 下一步

请Jim在火山引擎控制台：
1. 确认豆包服务已开通
2. 查看可用的模型调用权限
3. 获取正确的调用示例
4. 然后我再次测试