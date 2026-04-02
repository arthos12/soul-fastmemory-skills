#!/usr/bin/env python3
"""
测试火山引擎认证方式
"""

import requests
import json
import base64

# AK/SK信息
ACCESS_KEY_ID = "AKLTYjFhMmNkMDc1MWFjNDNiYjkxZTBjMjFjZWE1Y2FkNTg"
SECRET_ACCESS_KEY = "WVRFeU1tRTFObVZpTnpZd05EazJOR0V5T1RWaE56ZzBPRGcwWVRObU1UYw=="

# 解码SecretKey
try:
    SECRET_KEY = base64.b64decode(SECRET_ACCESS_KEY).decode('utf-8')
    print(f"解码后的SecretKey: {SECRET_KEY}")
except:
    SECRET_KEY = SECRET_ACCESS_KEY
    print(f"使用原始SecretKey: {SECRET_KEY[:20]}...")

def test_auth_variants():
    """测试不同的认证变体"""
    print("\n测试不同的认证方式...")
    
    variants = [
        # Bearer Token变体
        {"name": "Bearer with AccessKey", "headers": {"Authorization": f"Bearer {ACCESS_KEY_ID}"}},
        {"name": "Bearer with SecretKey", "headers": {"Authorization": f"Bearer {SECRET_KEY}"}},
        
        # X-头部变体
        {"name": "X-API-Key AccessKey", "headers": {"X-API-Key": ACCESS_KEY_ID}},
        {"name": "X-API-Key SecretKey", "headers": {"X-API-Key": SECRET_KEY}},
        
        # Authorization变体
        {"name": "Authorization AccessKey", "headers": {"Authorization": ACCESS_KEY_ID}},
        {"name": "Authorization SecretKey", "headers": {"Authorization": SECRET_KEY}},
        
        # 火山引擎特定头部
        {"name": "X-Volc-AccessKey", "headers": {"X-Volc-AccessKey": ACCESS_KEY_ID}},
        {"name": "X-Volc-AK", "headers": {"X-Volc-AK": ACCESS_KEY_ID}},
        {"name": "X-Volcengine-AK", "headers": {"X-Volcengine-AK": ACCESS_KEY_ID}},
        
        # 组合头部
        {"name": "X-AK + X-SK", "headers": {"X-AK": ACCESS_KEY_ID, "X-SK": SECRET_KEY}},
        {"name": "AccessKey + SecretKey", "headers": {"AccessKey": ACCESS_KEY_ID, "SecretKey": SECRET_KEY}},
    ]
    
    endpoint = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    model = "doubao-lite-128k-240428"
    
    for variant in variants:
        print(f"\n测试: {variant['name']}")
        
        headers = {"Content-Type": "application/json"}
        headers.update(variant["headers"])
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "test"}],
            "max_tokens": 5
        }
        
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=10)
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ 成功!")
                result = response.json()
                print(f"  响应: {result.get('choices', [{}])[0].get('message', {}).get('content', '')}")
                return True, variant["name"], model
            else:
                print(f"  响应: {response.text[:100]}")
                
        except Exception as e:
            print(f"  异常: {e}")
    
    return False, None, None

def test_different_models():
    """测试不同的模型"""
    print("\n测试不同的模型名称...")
    
    endpoint = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    headers = {"Authorization": f"Bearer {ACCESS_KEY_ID}", "Content-Type": "application/json"}
    
    models = [
        # 完整格式
        "doubao-lite-128k-240428",
        "doubao-pro-128k-240515",
        "doubao-lite-32k-240428",
        "doubao-pro-4k-240515",
        "doubao-lite-4k-240328",
        
        # 服务可能使用的名称
        "doubao_1.5_lite",
        "doubao_1.5_pro",
        "doubao-1.5-lite",
        "doubao-1.5-pro",
        
        # 简写
        "doubao-lite",
        "doubao-pro",
        "doubao",
        
        # seed系列
        "seed-lite",
        "seed-pro",
        "seed",
        
        # 尝试通用名称
        "chat",
        "completion",
        "text-generation",
    ]
    
    for model in models:
        print(f"\n测试模型: {model}")
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 5
        }
        
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=5)
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ 成功!")
                result = response.json()
                print(f"  响应: {result.get('choices', [{}])[0].get('message', {}).get('content', '')}")
                return True, model
            elif "does not exist" in response.text:
                print(f"  ❌ 模型不存在")
            elif "not have access" in response.text:
                print(f"  ⚠️  无权限")
            else:
                print(f"  响应: {response.text[:100]}")
                
        except Exception as e:
            print(f"  异常: {e}")
    
    return False, None

def test_service_info():
    """测试服务信息"""
    print("\n获取服务信息...")
    
    # 尝试获取模型列表
    endpoints = [
        "https://ark.cn-beijing.volces.com/api/v3/models",
        "https://ark.cn-beijing.volces.com/api/v1/models",
    ]
    
    headers_variants = [
        {"Authorization": f"Bearer {ACCESS_KEY_ID}"},
        {"X-API-Key": ACCESS_KEY_ID},
        {"Authorization": ACCESS_KEY_ID},
    ]
    
    for endpoint in endpoints:
        for headers in headers_variants:
            print(f"\n测试: {endpoint}")
            print(f"头部: {list(headers.keys())[0]}")
            
            try:
                response = requests.get(endpoint, headers=headers, timeout=10)
                print(f"  状态码: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"  ✅ 成功获取模型列表!")
                    try:
                        models = response.json()
                        if isinstance(models, dict) and "data" in models:
                            model_list = models["data"]
                            print(f"  找到 {len(model_list)} 个模型")
                            for model in model_list[:5]:
                                print(f"    - {model.get('id', '未知')}")
                        else:
                            print(f"  响应: {response.text[:200]}")
                    except:
                        print(f"  响应: {response.text[:200]}")
                    break
                else:
                    print(f"  响应: {response.text[:100]}")
                    
            except Exception as e:
                print(f"  异常: {e}")

def main():
    print("火山引擎认证测试")
    print("="*60)
    print(f"AccessKey ID: {ACCESS_KEY_ID}")
    print(f"SecretAccessKey: {SECRET_ACCESS_KEY[:20]}...")
    
    # 测试服务信息
    test_service_info()
    
    # 测试认证变体
    success, auth_method, model = test_auth_variants()
    if success:
        print(f"\n✅ 认证成功!")
        print(f"   方法: {auth_method}")
        print(f"   模型: {model}")
        return
    
    # 测试不同模型
    success, model = test_different_models()
    if success:
        print(f"\n✅ 找到可用模型!")
        print(f"   模型: {model}")
        return
    
    print("\n" + "="*60)
    print("❌ 所有测试失败")
    print("\n可能原因:")
    print("1. 需要火山引擎签名认证 (复杂签名算法)")
    print("2. 服务未开通或权限不足")
    print("3. 需要特定的SDK调用")
    print("4. AK/SK格式不正确")
    
    print("\n建议:")
    print("1. 查看火山引擎豆包API文档")
    print("2. 使用火山引擎官方SDK")
    print("3. 检查控制台服务状态")
    print("4. 联系技术支持")

if __name__ == "__main__":
    main()