#!/usr/bin/env python3
"""
最终方舟API测试
"""

import requests
import json

API_KEY = "fbffb5c8-6497-47b7-b165-a2d3a25769c2"
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

def test_model(model_name):
    """测试特定模型"""
    print(f"\n测试模型: {model_name}")
    
    url = f"{BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": "你好，请回复'测试成功'"}],
        "max_tokens": 20,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ 成功!")
            print(f"  响应: {result.get('choices', [{}])[0].get('message', {}).get('content', '')}")
            print(f"  Token使用: {result.get('usage', {})}")
            return True, model_name, result
        else:
            error_data = response.json() if response.text else {}
            error_msg = error_data.get("error", {}).get("message", response.text[:100])
            print(f"  错误: {error_msg}")
            return False, model_name, error_msg
            
    except Exception as e:
        print(f"  异常: {e}")
        return False, model_name, str(e)

def main():
    print("方舟API最终测试")
    print("="*60)
    print(f"API Key: {API_KEY}")
    print(f"端点: {BASE_URL}")
    print("="*60)
    
    # 测试可能的模型名称
    test_cases = [
        # 根据图片信息
        "doubao-seed-2-0-lite",
        
        # 常见变体
        "doubao-seed-2.0-lite",
        "doubao-seed-lite-2.0",
        "seed-2-0-lite",
        "seed-2.0-lite",
        
        # 简写
        "doubao-seed-lite",
        "seed-lite",
        "doubao-lite",
        
        # 完整格式
        "doubao-seed-2-0-lite-260215",  # 之前错误的
        "doubao-lite-128k-240428",      # 模型列表中的
    ]
    
    success = False
    
    for model in test_cases:
        success, model_name, result = test_model(model)
        if success:
            print(f"\n🎯 找到可用模型: {model_name}")
            
            # 更新OpenClaw配置
            print(f"\n更新OpenClaw配置...")
            config_cmd = f"""openclaw config set 'models.providers.volcengine' --json '{{
 "baseUrl": "https://ark.cn-beijing.volces.com/api/v3",
 "apiKey": "{API_KEY}",
 "api": "openai-completions",
 "models": [
 {{
 "id": "{model_name}",
 "name": "DoubaoSeed 2.0 Lite",
 "reasoning": false,
 "input": ["text"],
 "cost": {{
 "input": 0,
 "output": 0,
 "cacheRead": 0,
 "cacheWrite": 0
 }},
 "contextWindow": 128000,
 "maxTokens": 4000,
 "api": "openai-completions"
 }}
 ]
}}'"""
            
            print(f"配置命令:")
            print(config_cmd)
            
            # 保存配置到文件
            config = {
                "providers": {
                    "volcengine": {
                        "baseUrl": "https://ark.cn-beijing.volces.com/api/v3",
                        "apiKey": API_KEY,
                        "api": "openai-completions",
                        "models": [
                            {
                                "id": model_name,
                                "name": "DoubaoSeed 2.0 Lite",
                                "reasoning": False,
                                "input": ["text"],
                                "cost": {
                                    "input": 0,
                                    "output": 0,
                                    "cacheRead": 0,
                                    "cacheWrite": 0
                                },
                                "contextWindow": 128000,
                                "maxTokens": 4000,
                                "api": "openai-completions"
                            }
                        ]
                    }
                }
            }
            
            config_path = "/root/.openclaw/workspace/data/ark_final_config.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"\n配置已保存到: {config_path}")
            print(f"\n✅ 方舟模型配置完成!")
            print(f"   模型: {model_name}")
            print(f"   端点: {BASE_URL}")
            print(f"\n下一步: 在TG中使用命令切换模型")
            print(f"   /model volcengine/{model_name}")
            
            return
    
    if not success:
        print(f"\n❌ 所有模型测试失败")
        print(f"\n可能原因:")
        print(f"1. 服务未开通 - 需要在控制台开通方舟服务")
        print(f"2. API Key权限不足 - 只有读取权限")
        print(f"3. 需要开通计费 - 免费额度可能已用完")
        print(f"4. 区域限制 - 服务在特定区域不可用")
        
        print(f"\n建议:")
        print(f"1. 登录火山引擎控制台检查方舟服务状态")
        print(f"2. 确认API Key有调用权限")
        print(f"3. 查看具体的API调用示例")
        print(f"4. 联系技术支持")

if __name__ == "__main__":
    main()