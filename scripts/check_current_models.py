#!/usr/bin/env python3
"""
检查当前可用的模型配置
"""

import json
import os
from pathlib import Path

def check_openclaw_config():
    """检查OpenClaw配置"""
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    
    print("检查OpenClaw配置...")
    print(f"配置文件: {config_path}")
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        providers = config.get("models", {}).get("providers", {})
        
        print(f"\n当前配置的提供商: {len(providers)} 个")
        for provider, info in providers.items():
            print(f"\n{provider}:")
            print(f"  baseUrl: {info.get('baseUrl', '未设置')}")
            print(f"  API Key: {info.get('apiKey', '未设置')[:8]}...{info.get('apiKey', '')[-4:] if info.get('apiKey') else ''}")
            
            models = info.get("models", [])
            print(f"  模型数量: {len(models)}")
            for model in models[:3]:  # 只显示前3个
                print(f"    - {model.get('id', '未知')}")
            
            if len(models) > 3:
                print(f"    - ... 还有 {len(models)-3} 个模型")
    else:
        print("❌ OpenClaw配置文件不存在")

def check_available_models():
    """检查可用的模型"""
    print("\n" + "="*60)
    print("当前可用模型测试")
    print("="*60)
    
    # 测试DeepSeek
    print("\n1. 测试DeepSeek模型...")
    try:
        import requests
        
        # 从环境变量或配置获取DeepSeek API Key
        deepseek_key = os.getenv("DEEPSEEK_API_KEY", "")
        if not deepseek_key:
            # 尝试从配置读取
            config_path = Path.home() / ".openclaw" / "openclaw.json"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    deepseek_config = config.get("models", {}).get("providers", {}).get("deepseek", {})
                    deepseek_key = deepseek_config.get("apiKey", "")
        
        if deepseek_key:
            headers = {"Authorization": f"Bearer {deepseek_key}"}
            response = requests.get("https://api.deepseek.com/v1/models", headers=headers, timeout=10)
            
            if response.status_code == 200:
                models = response.json().get("data", [])
                print(f"✅ DeepSeek可用，找到 {len(models)} 个模型:")
                for model in models:
                    print(f"    - {model.get('id', '未知')}")
            else:
                print(f"❌ DeepSeek测试失败: {response.status_code}")
        else:
            print("⚠️  未找到DeepSeek API Key")
            
    except Exception as e:
        print(f"❌ DeepSeek测试异常: {e}")
    
    # 测试豆包
    print("\n2. 测试豆包模型...")
    doubao_key = "fbffb5c8-6497-47b7-b165-a2d3a25769c2"
    
    try:
        import requests
        
        # 测试模型列表
        headers = {"Authorization": f"Bearer {doubao_key}"}
        response = requests.get("https://ark.cn-beijing.volces.com/api/v3/models", headers=headers, timeout=10)
        
        if response.status_code == 200:
            models = response.json().get("data", [])
            print(f"✅ 豆包模型列表可获取，找到 {len(models)} 个模型")
            
            # 显示一些模型
            lite_models = [m for m in models if "lite" in m.get("id", "").lower()]
            pro_models = [m for m in models if "pro" in m.get("id", "").lower()]
            
            print(f"  Lite模型: {len(lite_models)} 个")
            print(f"  Pro模型: {len(pro_models)} 个")
            
            # 测试调用
            print("\n  测试模型调用...")
            test_model = lite_models[0].get("id") if lite_models else pro_models[0].get("id") if pro_models else None
            
            if test_model:
                payload = {
                    "model": test_model,
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 5
                }
                
                call_response = requests.post(
                    "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=10
                )
                
                if call_response.status_code == 200:
                    print(f"  ✅ 模型调用成功: {test_model}")
                else:
                    print(f"  ❌ 模型调用失败 ({call_response.status_code}): {test_model}")
                    print(f"     错误: {call_response.text[:100]}")
        else:
            print(f"❌ 豆包模型列表获取失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 豆包测试异常: {e}")

def create_doubao_integration_guide():
    """创建豆包集成指南"""
    print("\n" + "="*60)
    print("豆包模型集成指南")
    print("="*60)
    
    guide = """
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
curl -X POST "https://ark.cn-beijing.volces.com/api/v3/chat/completions" \\
  -H "Authorization: Bearer fbffb5c8-6497-47b7-b165-a2d3a25769c2" \\
  -H "Content-Type: application/json" \\
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
"""
    
    print(guide)
    
    # 保存指南到文件
    guide_path = Path("/root/.openclaw/workspace/docs/doubao_integration_guide.md")
    guide_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print(f"\n📄 指南已保存到: {guide_path}")

def main():
    """主函数"""
    print("当前模型配置检查")
    print("="*60)
    
    # 1. 检查配置
    check_openclaw_config()
    
    # 2. 检查可用模型
    check_available_models()
    
    # 3. 创建集成指南
    create_doubao_integration_guide()
    
    print("\n" + "="*60)
    print("✅ 检查完成")
    print("="*60)
    print("\n下一步:")
    print("1. Jim检查火山引擎控制台豆包服务状态")
    print("2. 获取正确的模型调用信息")
    print("3. 我再次测试并配置")
    print("4. 在TG中切换模型")

if __name__ == "__main__":
    main()