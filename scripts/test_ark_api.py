#!/usr/bin/env python3
"""
测试方舟API
"""

import requests
import json

ARK_API_KEY = "fbffb5c8-6497-47b7-b165-a2d3a25769c2"
BASE_URL = "https://ark.cn-beijing.volces.com"

def test_ark_models():
    """测试方舟模型列表"""
    print("1. 获取方舟模型列表...")
    
    url = f"{BASE_URL}/api/v3/models"
    headers = {"Authorization": f"Bearer {ARK_API_KEY}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            models = response.json()
            print(f"  ✅ 成功获取模型列表")
            
            if isinstance(models, dict) and "data" in models:
                model_list = models["data"]
                print(f"  找到 {len(model_list)} 个模型")
                
                # 显示模型信息
                for model in model_list[:10]:
                    model_id = model.get("id", "")
                    print(f"    - {model_id}")
                    
                    # 检查是否是豆包相关模型
                    if "doubao" in model_id.lower() or "seed" in model_id.lower():
                        print(f"      ⭐ 可能是豆包模型")
                
                return model_list
            else:
                print(f"  响应格式: {type(models)}")
                print(f"  响应内容: {json.dumps(models, indent=2)[:500]}")
        else:
            print(f"  错误: {response.text[:200]}")
            
    except Exception as e:
        print(f"  异常: {e}")
    
    return []

def test_ark_chat_completion():
    """测试方舟聊天补全"""
    print("\n2. 测试方舟聊天补全...")
    
    # 先获取模型列表
    models = test_ark_models()
    if not models:
        print("  ⚠️  无法获取模型列表，尝试常见模型")
        models = [{"id": "doubao-lite-128k-240428"}]
    
    # 测试每个模型
    for model_info in models[:5]:  # 只测试前5个
        model_id = model_info.get("id", "")
        if not model_id:
            continue
        
        print(f"\n  测试模型: {model_id}")
        
        url = f"{BASE_URL}/api/v3/chat/completions"
        headers = {
            "Authorization": f"Bearer {ARK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model_id,
            "messages": [
                {
                    "role": "user",
                    "content": "你好，请简单介绍一下自己"
                }
            ],
            "max_tokens": 50,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            print(f"    状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"    ✅ 调用成功!")
                print(f"    响应: {result.get('choices', [{}])[0].get('message', {}).get('content', '')[:100]}...")
                
                # 检查使用情况
                if "usage" in result:
                    usage = result["usage"]
                    print(f"    Token使用: 输入{usage.get('prompt_tokens', 0)}, 输出{usage.get('completion_tokens', 0)}")
                
                return True, model_id, result
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get("error", {}).get("message", response.text[:100])
                print(f"    ❌ 错误: {error_msg}")
                
        except Exception as e:
            print(f"    异常: {e}")
    
    return False, None, None

def test_ark_different_endpoints():
    """测试不同的端点"""
    print("\n3. 测试不同的API端点...")
    
    endpoints = [
        "/api/v3/chat/completions",
        "/api/v1/chat/completions",
        "/v1/chat/completions",
        "/chat/completions",
        "/api/chat/completions",
    ]
    
    test_model = "doubao-lite-128k-240428"
    
    for endpoint in endpoints:
        print(f"\n  测试端点: {endpoint}")
        
        url = BASE_URL + endpoint
        headers = {
            "Authorization": f"Bearer {ARK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": test_model,
            "messages": [{"role": "user", "content": "test"}],
            "max_tokens": 5
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=5)
            print(f"    状态码: {response.status_code}")
            
            if response.status_code == 200:
                print(f"    ✅ 端点可用!")
                return True, endpoint, test_model
            elif response.status_code == 404:
                print(f"    ❌ 端点不存在")
            else:
                print(f"    响应: {response.text[:100]}")
                
        except Exception as e:
            print(f"    异常: {e}")
    
    return False, None, None

def test_ark_capabilities():
    """测试方舟能力"""
    print("\n4. 测试方舟API能力...")
    
    # 先找到一个可用的模型
    models = test_ark_models()
    if not models:
        print("  ⚠️  无法测试，没有可用模型")
        return
    
    # 使用第一个模型
    model_id = models[0].get("id", "")
    if not model_id:
        print("  ⚠️  没有有效的模型ID")
        return
    
    print(f"\n  使用模型: {model_id}")
    
    url = f"{BASE_URL}/api/v3/chat/completions"
    headers = {
        "Authorization": f"Bearer {ARK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 测试不同任务
    tests = [
        {
            "name": "简单问答",
            "prompt": "中国的首都是哪里？",
            "expected": "北京"
        },
        {
            "name": "数学计算",
            "prompt": "123 + 456 等于多少？",
            "expected": "579"
        },
        {
            "name": "逻辑推理",
            "prompt": "如果所有猫都会爬树，Tom是一只猫，那么Tom会爬树吗？",
            "expected": "会"
        }
    ]
    
    for test in tests:
        print(f"\n    测试: {test['name']}")
        
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": test["prompt"]}],
            "max_tokens": 50,
            "temperature": 0.3
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # 检查是否包含预期关键词
                if test["expected"].lower() in content.lower():
                    print(f"      ✅ 通过")
                else:
                    print(f"      ⚠️  响应: {content[:50]}...")
            else:
                print(f"      ❌ 失败: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ 异常: {e}")

def create_openclaw_config(model_id):
    """创建OpenClaw配置"""
    print(f"\n5. 创建OpenClaw配置...")
    
    config = {
        "providers": {
            "ark": {
                "baseUrl": BASE_URL + "/api/v3",
                "apiKey": ARK_API_KEY,
                "api": "openai-completions",
                "models": [
                    {
                        "id": model_id,
                        "name": f"方舟 {model_id}",
                        "reasoning": False,
                        "input": ["text"],
                        "cost": {
                            "input": 0.000,  # 需要实际价格
                            "output": 0.000,
                            "cacheRead": 0,
                            "cacheWrite": 0
                        },
                        "contextWindow": 128000,
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
    
    config_json = json.dumps(config, indent=2, ensure_ascii=False)
    
    print(f"  OpenClaw配置模板:")
    print("  " + "="*50)
    for line in config_json.split('\n'):
        print(f"  {line}")
    print("  " + "="*50)
    
    # 保存配置
    config_path = "/root/.openclaw/workspace/data/ark_config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"\n  配置已保存到: {config_path}")
    
    return config

def main():
    print("方舟API测试")
    print("="*60)
    print(f"API Key: {ARK_API_KEY}")
    print(f"端点: {BASE_URL}")
    print("="*60)
    
    # 1. 测试模型列表
    models = test_ark_models()
    
    # 2. 测试聊天补全
    success, model_id, result = test_ark_chat_completion()
    
    if success:
        print(f"\n✅ 方舟API测试成功!")
        print(f"   模型: {model_id}")
        print(f"   响应示例: {result.get('choices', [{}])[0].get('message', {}).get('content', '')[:100]}...")
        
        # 3. 创建OpenClaw配置
        config = create_openclaw_config(model_id)
        
        print(f"\n🎯 下一步:")
        print(f"1. 添加配置到OpenClaw:")
        print(f"   openclaw config set models.providers.ark '{json.dumps(config['providers']['ark'])}'")
        print(f"2. 在TG中切换模型:")
        print(f"   /model ark/{model_id}")
        print(f"3. 测试使用效果")
        
    else:
        # 3. 测试不同端点
        success, endpoint, model_id = test_ark_different_endpoints()
        
        if success:
            print(f"\n✅ 找到可用端点!")
            print(f"   端点: {endpoint}")
            print(f"   模型: {model_id}")
        else:
            # 4. 测试能力
            test_ark_capabilities()
            
            print(f"\n❌ 方舟API测试失败")
            print(f"\n可能原因:")
            print(f"1. API Key权限不足")
            print(f"2. 服务未开通")
            print(f"3. 需要特定的模型名称")
            print(f"4. 需要其他认证方式")
            
            print(f"\n建议:")
            print(f"1. 检查方舟控制台服务状态")
            print(f"2. 查看API文档获取正确用法")
            print(f"3. 联系技术支持")

if __name__ == "__main__":
    main()