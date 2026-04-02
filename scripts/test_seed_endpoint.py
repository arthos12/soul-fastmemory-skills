#!/usr/bin/env python3
"""
测试Seed专用接入点
"""

import requests
import json

API_KEY = "fbffb5c8-6497-47b7-b165-a2d3a25769c2"
BASE_URL = "https://ark.cn-beijing.volces.com"

def test_seed_endpoint():
    """测试Seed端点"""
    print("测试Seed专用接入点...")
    print(f"API Key: {API_KEY}")
    print(f"模型: doubao-seed-2-0-lite")
    print("="*60)
    
    # 测试不同路径
    endpoints = [
        "/api/seed/v3/chat/completions",
        "/seed/v3/chat/completions",
        "/api/seed/chat/completions",
        "/seed/chat/completions",
        "/api/v3/seed/chat/completions",
    ]
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "doubao-seed-2-0-lite",
        "messages": [{"role": "user", "content": "你好，请回复'测试成功'"}],
        "max_tokens": 20,
        "temperature": 0.7
    }
    
    for endpoint in endpoints:
        url = BASE_URL + endpoint
        print(f"\n测试端点: {endpoint}")
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ 成功!")
                print(f"  响应: {result.get('choices', [{}])[0].get('message', {}).get('content', '')}")
                print(f"  Token使用: {result.get('usage', {})}")
                return True, endpoint, result
            elif response.status_code == 404:
                print(f"  ❌ 端点不存在")
            elif response.status_code == 401:
                print(f"  ⚠️  认证失败")
                print(f"  错误: {response.text[:100]}")
            else:
                print(f"  响应: {response.text[:100]}")
                
        except requests.exceptions.ConnectionError:
            print(f"  ❌ 连接失败")
        except Exception as e:
            print(f"  ❌ 异常: {e}")
    
    return False, None, None

def test_model_variants():
    """测试模型变体"""
    print("\n" + "="*60)
    print("测试模型名称变体...")
    
    endpoints = [
        "/api/seed/v3/chat/completions",
        "/api/v3/chat/completions",
    ]
    
    models = [
        "doubao-seed-2-0-lite",
        "doubao-seed-2.0-lite",
        "doubao-seed-lite",
        "seed-2-0-lite",
        "seed-lite",
        "doubao-lite-128k-240428",
    ]
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    for endpoint in endpoints:
        for model in models:
            url = BASE_URL + endpoint
            print(f"\n测试: {endpoint} + {model}")
            
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 5
            }
            
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=5)
                print(f"  状态码: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"  ✅ 找到可用组合!")
                    return True, endpoint, model
                elif "does not exist" in response.text:
                    continue
                else:
                    print(f"  响应: {response.text[:50]}")
                    
            except Exception as e:
                print(f"  异常: {e}")
    
    return False, None, None

def main():
    print("方舟Seed模型测试")
    print("="*60)
    
    # 1. 测试Seed端点
    success, endpoint, result = test_seed_endpoint()
    
    if success:
        print(f"\n🎯 Seed端点测试成功!")
        print(f"   端点: {endpoint}")
        print(f"   模型: doubao-seed-2-0-lite")
        
        # 更新OpenClaw配置
        print(f"\n更新OpenClaw配置...")
        config = {
            "baseUrl": BASE_URL + endpoint.replace("/chat/completions", ""),
            "apiKey": API_KEY,
            "api": "openai-completions",
            "models": [
                {
                    "id": "doubao-seed-2-0-lite",
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
        
        config_json = json.dumps(config, indent=2, ensure_ascii=False)
        print(f"配置:")
        print(config_json)
        
        # 保存配置
        config_path = "/root/.openclaw/workspace/data/seed_final_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump({"providers": {"volcengine": config}}, f, indent=2, ensure_ascii=False)
        
        print(f"\n配置已保存到: {config_path}")
        print(f"\n✅ 配置完成!")
        
    else:
        # 2. 测试模型变体
        success, endpoint, model = test_model_variants()
        
        if success:
            print(f"\n🎯 找到可用组合!")
            print(f"   端点: {endpoint}")
            print(f"   模型: {model}")
        else:
            print(f"\n❌ 所有测试失败")
            print(f"\n可能原因:")
            print(f"1. Seed端点路径不正确")
            print(f"2. 需要其他认证方式")
            print(f"3. 服务未开通或权限不足")
            print(f"4. 需要查看具体的API文档")

if __name__ == "__main__":
    main()