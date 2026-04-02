#!/usr/bin/env python3
"""
测试豆包API的不同认证方式
"""

import requests
import json
import time
import hashlib
import hmac
import base64

API_KEY = "fbffb5c8-6497-47b7-b165-a2d3a25769c2"

def test_bearer_auth():
    """测试Bearer Token认证"""
    print("1. 测试Bearer Token认证...")
    
    endpoints = [
        "https://ark.cn-beijing.volces.com/api/v3",
        "https://ark.cn-beijing.volces.com/api/v1",
        "https://ark.cn-beijing.volces.com/api/v2",
    ]
    
    test_models = [
        "doubao-lite-128k-240428",
        "doubao-pro-128k-240515",
        "doubao-seed-lite",
        "doubao-seed-pro",
    ]
    
    for endpoint in endpoints:
        for model in test_models:
            url = f"{endpoint}/chat/completions"
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
                print(f"  {endpoint} | {model}: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"    ✅ 成功!")
                    return True, endpoint, model
                elif response.status_code == 404:
                    # 继续测试其他模型
                    continue
                else:
                    print(f"    ❌ {response.text[:100]}")
                    
            except Exception as e:
                print(f"  {endpoint} | {model}: 异常 - {e}")
    
    return False, None, None

def test_aksk_auth():
    """测试AK/SK认证（火山引擎常见方式）"""
    print("\n2. 测试AK/SK认证...")
    
    # 假设API_KEY就是AccessKey
    access_key = API_KEY
    secret_key = ""  # 需要Secret Key
    
    # 没有Secret Key，无法测试AK/SK
    print("  ⚠️  需要Secret Key才能测试AK/SK认证")
    return False, None, None

def test_x_api_key():
    """测试X-API-Key头部认证"""
    print("\n3. 测试X-API-Key认证...")
    
    endpoints = [
        "https://ark.cn-beijing.volces.com/api/v3",
        "https://ark.cn-beijing.volces.com/api/v1",
    ]
    
    headers_variants = [
        {"X-API-Key": API_KEY, "Content-Type": "application/json"},
        {"x-api-key": API_KEY, "Content-Type": "application/json"},
        {"api-key": API_KEY, "Content-Type": "application/json"},
        {"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
        {"Authorization": f"APIKey {API_KEY}", "Content-Type": "application/json"},
    ]
    
    test_model = "doubao-lite-128k-240428"
    
    for endpoint in endpoints:
        for headers in headers_variants:
            url = f"{endpoint}/chat/completions"
            
            payload = {
                "model": test_model,
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 5
            }
            
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=5)
                header_name = list(headers.keys())[0]
                print(f"  {endpoint} | {header_name}: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"    ✅ 成功!")
                    return True, endpoint, test_model
                    
            except Exception as e:
                print(f"  {endpoint} | {headers}: 异常 - {e}")
    
    return False, None, None

def test_different_models():
    """测试不同的模型名称格式"""
    print("\n4. 测试不同的模型名称格式...")
    
    endpoint = "https://ark.cn-beijing.volces.com/api/v3"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    model_variants = [
        # 完整格式
        "doubao-lite-128k-240428",
        "doubao-pro-128k-240515",
        
        # 简写格式
        "doubao-lite",
        "doubao-pro",
        "doubao",
        
        # seed格式
        "seed-lite",
        "seed-pro",
        "seed",
        
        # 其他可能格式
        "Doubao-Lite",
        "Doubao-Pro",
        "DOUBAO-LITE",
        
        # 版本格式
        "doubao-v1",
        "doubao-v2",
        "doubao-1.0",
        "doubao-2.0",
        
        # 上下文格式
        "doubao-128k",
        "doubao-32k",
        "doubao-4k",
    ]
    
    for model in model_variants:
        url = f"{endpoint}/chat/completions"
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 5
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=5)
            print(f"  模型 '{model}': {response.status_code}")
            
            if response.status_code == 200:
                print(f"    ✅ 找到可用模型: {model}")
                return True, endpoint, model
            elif "does not exist" in response.text:
                continue  # 继续测试
            elif "not have access" in response.text:
                print(f"    ⚠️  无权限，但模型可能存在: {model}")
                
        except Exception as e:
            print(f"  模型 '{model}': 异常 - {e}")
    
    return False, None, None

def test_service_status():
    """测试服务状态"""
    print("\n5. 测试服务状态...")
    
    # 测试根端点
    endpoints = [
        "https://ark.cn-beijing.volces.com",
        "https://ark.cn-beijing.volces.com/api/v3",
        "https://ark.cn-beijing.volces.com/api/v1",
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            print(f"  {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                print(f"    ✅ 服务正常")
            elif response.status_code == 401 or response.status_code == 403:
                print(f"    ⚠️  需要认证")
            else:
                print(f"   响应: {response.text[:100]}")
                
        except Exception as e:
            print(f"  {endpoint}: 异常 - {e}")

def main():
    print("豆包API认证方式测试")
    print("="*60)
    
    # 测试服务状态
    test_service_status()
    
    # 测试不同认证方式
    success = False
    endpoint = None
    model = None
    
    # 1. Bearer Token
    success, endpoint, model = test_bearer_auth()
    if success:
        print(f"\n✅ 使用Bearer Token认证成功!")
        print(f"   端点: {endpoint}")
        print(f"   模型: {model}")
        return
    
    # 2. AK/SK (需要Secret Key)
    success, endpoint, model = test_aksk_auth()
    
    # 3. X-API-Key
    success, endpoint, model = test_x_api_key()
    if success:
        print(f"\n✅ 使用X-API-Key认证成功!")
        print(f"   端点: {endpoint}")
        print(f"   模型: {model}")
        return
    
    # 4. 测试不同模型名称
    success, endpoint, model = test_different_models()
    if success:
        print(f"\n✅ 找到可用模型名称!")
        print(f"   端点: {endpoint}")
        print(f"   模型: {model}")
        return
    
    print("\n" + "="*60)
    print("❌ 所有认证方式测试失败")
    print("\n可能原因:")
    print("1. 服务未开通 - 需要在火山引擎控制台开通豆包服务")
    print("2. 权限不足 - API Key只有读取权限，没有调用权限")
    print("3. 需要AK/SK认证 - 需要AccessKey和SecretKey对")
    print("4. 需要其他认证方式 - 如签名认证")
    print("\n建议:")
    print("1. 检查火山引擎控制台豆包服务状态")
    print("2. 查看API文档获取正确的认证方式")
    print("3. 获取完整的AK/SK密钥对")
    print("4. 联系火山引擎技术支持")

if __name__ == "__main__":
    main()