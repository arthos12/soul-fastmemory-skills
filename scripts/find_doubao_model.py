#!/usr/bin/env python3
"""
查找豆包可用的模型
"""

import requests
import json

API_KEY = "fbffb5c8-6497-47b7-b165-a2d3a25769c2"
BASE_URL = "https://ark.cn-beijing.volces.com"

def test_models_list():
    """测试获取模型列表"""
    endpoints = [
        "/api/v3/models",
        "/api/v1/models", 
        "/api/v2/models",
        "/api/models",
        "/v1/models",
        "/v3/models"
    ]
    
    print("尝试获取模型列表...")
    
    for endpoint in endpoints:
        url = BASE_URL + endpoint
        headers = {"Authorization": f"Bearer {API_KEY}"}
        
        try:
            print(f"尝试: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ 成功获取模型列表!")
                models = response.json()
                
                if isinstance(models, dict) and "data" in models:
                    model_list = models["data"]
                elif isinstance(models, list):
                    model_list = models
                else:
                    model_list = [models]
                
                print(f"找到 {len(model_list)} 个模型:")
                for model in model_list[:10]:  # 只显示前10个
                    if isinstance(model, dict):
                        print(f"  - {model.get('id', '未知')}: {model.get('object', '')}")
                    else:
                        print(f"  - {model}")
                
                return model_list
            else:
                print(f"❌ {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ 异常: {e}")
    
    return None

def test_common_doubao_models():
    """测试常见的豆包模型名称"""
    print("\n测试常见豆包模型名称...")
    
    common_models = [
        # 火山引擎豆包常见模型
        "doubao-pro-32k",
        "doubao-pro",
        "doubao-lite",
        "doubao-seed",
        "seed-32k",
        "seed-lite",
        "seed-pro",
        "doubao-1.5-pro-32k",
        "doubao-1.5-lite",
        "doubao-1.5-pro",
        
        # 可能的版本
        "doubao-v1",
        "doubao-v2",
        "seed-v1",
        "seed-v2",
        
        # 简写
        "db-pro",
        "db-lite",
        "db-seed",
    ]
    
    working_models = []
    
    for model in common_models:
        url = BASE_URL + "/api/v3/chat/completions"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "hello"}],
            "max_tokens": 5
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {model}: 可用")
                working_models.append(model)
            elif "does not exist" in response.text:
                print(f"❌ {model}: 不存在")
            elif "not have access" in response.text:
                print(f"⚠️  {model}: 无权限")
            else:
                print(f"❌ {model}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {model}: 异常 - {e}")
    
    return working_models

def create_openclaw_config(model_name):
    """创建OpenClaw配置"""
    config = {
        "providers": {
            "doubao": {
                "baseUrl": BASE_URL + "/api/v3",
                "apiKey": API_KEY,
                "api": "openai-completions",
                "models": [
                    {
                        "id": model_name,
                        "name": f"豆包 {model_name}",
                        "reasoning": False,
                        "input": ["text"],
                        "cost": {
                            "input": 0.000,  # 需要实际价格
                            "output": 0.000,
                            "cacheRead": 0,
                            "cacheWrite": 0
                        },
                        "contextWindow": 32000,
                        "maxTokens": 4000,
                        "supportsJson": True,
                        "supportsTools": False,
                        "supportsVision": False,
                        "supportsAudio": False
                    }
                ]
            }
        }
    }
    
    return config

def main():
    print("查找豆包可用模型")
    print("="*60)
    
    # 1. 尝试获取模型列表
    models = test_models_list()
    
    # 2. 如果获取不到列表，测试常见模型
    if not models:
        print("\n无法获取模型列表，测试常见模型名称...")
        working_models = test_common_doubao_models()
        
        if working_models:
            print(f"\n✅ 找到可用模型: {working_models}")
            
            # 使用第一个可用模型
            model_name = working_models[0]
            print(f"\n使用模型: {model_name}")
            
            # 创建配置
            config = create_openclaw_config(model_name)
            
            print("\n📝 OpenClaw配置:")
            print(json.dumps(config, indent=2, ensure_ascii=False))
            
            # 保存配置
            config_path = "/root/.openclaw/workspace/data/doubao_config.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"\n配置已保存到: {config_path}")
            
            # 测试实际调用
            print(f"\n测试实际调用...")
            url = BASE_URL + "/api/v3/chat/completions"
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": "你好，请简单介绍一下自己"}],
                "max_tokens": 100
            }
            
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    print(f"✅ 调用成功!")
                    print(f"响应: {content[:200]}...")
                    
                    # 保存测试结果
                    test_result = {
                        "model": model_name,
                        "success": True,
                        "response": content,
                        "usage": result.get("usage", {})
                    }
                    
                    result_path = "/root/.openclaw/workspace/data/doubao_test_result.json"
                    with open(result_path, 'w', encoding='utf-8') as f:
                        json.dump(test_result, f, indent=2, ensure_ascii=False)
                    
                    print(f"\n测试结果已保存到: {result_path}")
                else:
                    print(f"❌ 调用失败: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"❌ 调用异常: {e}")
                
        else:
            print("\n❌ 未找到可用模型")
            print("\n建议:")
            print("1. 检查API Key是否正确")
            print("2. 查看火山引擎控制台获取正确的模型名称")
            print("3. 确认服务已开通")
    else:
        print(f"\n✅ 成功获取模型列表，共 {len(models)} 个模型")

if __name__ == "__main__":
    main()