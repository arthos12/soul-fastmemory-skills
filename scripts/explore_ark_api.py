#!/usr/bin/env python3
"""
探索方舟大模型专用API
"""

import requests
import json

ARK_API_KEY = "fbffb5c8-6497-47b7-b165-a2d3a25769c2"

def explore_endpoints():
    """探索可能的端点"""
    print("探索方舟API端点...")
    
    base_urls = [
        "https://ark.cn-beijing.volces.com",
        "https://ark.volcengine.com",
        "https://api.volcengine.com/ark",
    ]
    
    paths = [
        "/api/v1/chat/completions",
        "/v1/chat/completions",
        "/chat/completions",
        "/api/completions",
        "/completions",
        "/ark/v1/chat/completions",
        "/ark/api/v1/chat/completions",
    ]
    
    headers = {"Authorization": f"Bearer {ARK_API_KEY}"}
    
    for base_url in base_urls:
        for path in paths:
            url = base_url + path
            
            # 简单测试
            print(f"\n测试: {url}")
            
            payload = {
                "model": "doubao-lite-128k-240428",
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 5
            }
            
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=5)
                print(f"  状态码: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"  ✅ 可能找到正确端点!")
                    result = response.json()
                    print(f"  响应: {result}")
                    return url
                elif response.status_code == 404:
                    print(f"  ❌ 端点不存在")
                elif response.status_code == 401:
                    print(f"  ⚠️  需要认证")
                else:
                    print(f"  响应: {response.text[:100]}")
                    
            except requests.exceptions.ConnectionError:
                print(f"  ❌ 连接失败")
            except Exception as e:
                print(f"  ❌ 异常: {e}")
    
    return None

def test_ark_specific_models():
    """测试方舟特定模型"""
    print("\n测试方舟特定模型名称...")
    
    url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    headers = {"Authorization": f"Bearer {ARK_API_KEY}", "Content-Type": "application/json"}
    
    # 方舟可能使用的模型名称
    ark_models = [
        # 完整方舟格式
        "ark-doubao-lite",
        "ark-doubao-pro",
        "ark-seed-lite",
        "ark-seed-pro",
        
        # 简写
        "ark-lite",
        "ark-pro",
        "ark",
        
        # 服务前缀
        "volc-ark-doubao",
        "volc-ark-seed",
        
        # 版本号
        "doubao-v1",
        "doubao-v2",
        "seed-v1",
        "seed-v2",
        
        # 可能的产品名称
        "volcengine-ark",
        "volc-ark",
    ]
    
    for model in ark_models:
        print(f"\n测试模型: {model}")
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "hello"}],
            "max_tokens": 5
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=5)
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ 找到可用模型!")
                result = response.json()
                print(f"  响应: {result.get('choices', [{}])[0].get('message', {}).get('content', '')}")
                return model
            elif "does not exist" in response.text:
                continue
            else:
                print(f"  响应: {response.text[:100]}")
                
        except Exception as e:
            print(f"  异常: {e}")
    
    return None

def check_ark_documentation():
    """检查方舟文档"""
    print("\n尝试查找方舟文档...")
    
    # 尝试访问可能的文档页面
    doc_urls = [
        "https://www.volcengine.com/docs/82379",  # 方舟文档
        "https://ark.volcengine.com/docs",
        "https://api.volcengine.com/api-docs/ark",
    ]
    
    for url in doc_urls:
        print(f"\n尝试: {url}")
        try:
            response = requests.get(url, timeout=5)
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                # 检查页面内容
                content = response.text.lower()
                if "ark" in content or "方舟" in content or "doubao" in content:
                    print(f"  ✅ 可能找到文档页面")
                    # 提取标题
                    import re
                    title_match = re.search(r'<title>(.*?)</title>', response.text, re.IGNORECASE)
                    if title_match:
                        print(f"  标题: {title_match.group(1)}")
                else:
                    print(f"  页面内容不相关")
            else:
                print(f"  页面不可访问")
                
        except Exception as e:
            print(f"  异常: {e}")

def test_with_aksk():
    """使用火山引擎AK/SK测试方舟"""
    print("\n使用火山引擎AK/SK测试方舟...")
    
    access_key_id = "AKLTYjFhMmNkMDc1MWFjNDNiYjkxZTBjMjFjZWE1Y2FkNTg"
    secret_access_key = "WVRFeU1tRTFObVZpTnpZd05EazJOR0V5T1RWaE56ZzBPRGcwWVRObU1UYw=="
    
    # 解码SecretKey
    import base64
    try:
        secret_key = base64.b64decode(secret_access_key).decode('utf-8')
        print(f"解码后的SecretKey: {secret_key}")
    except:
        secret_key = secret_access_key
        print(f"使用原始SecretKey: {secret_key[:20]}...")
    
    # 尝试使用AK/SK调用方舟
    url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    
    # 火山引擎可能需要的头部
    headers_variants = [
        {"X-Volc-AccessKey": access_key_id, "X-Volc-SecretKey": secret_key},
        {"X-Volcengine-AccessKey": access_key_id, "X-Volcengine-SecretKey": secret_key},
        {"Authorization": f"Volc {access_key_id}:{secret_key}"},
    ]
    
    for headers in headers_variants:
        headers["Content-Type"] = "application/json"
        
        print(f"\n测试头部: {list(headers.keys())[0]}")
        
        payload = {
            "model": "doubao-lite-128k-240428",
            "messages": [{"role": "user", "content": "test"}],
            "max_tokens": 5
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=5)
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ AK/SK认证成功!")
                return True
            else:
                print(f"  响应: {response.text[:100]}")
                
        except Exception as e:
            print(f"  异常: {e}")
    
    return False

def main():
    print("探索方舟大模型专用API")
    print("="*60)
    print(f"方舟专用API Key: {ARK_API_KEY}")
    print("="*60)
    
    # 1. 探索端点
    endpoint = explore_endpoints()
    if endpoint:
        print(f"\n✅ 找到可能端点: {endpoint}")
        return
    
    # 2. 测试特定模型
    model = test_ark_specific_models()
    if model:
        print(f"\n✅ 找到可用模型: {model}")
        return
    
    # 3. 检查文档
    check_ark_documentation()
    
    # 4. 使用AK/SK测试
    success = test_with_aksk()
    if success:
        print(f"\n✅ 使用火山引擎AK/SK成功!")
        return
    
    print("\n" + "="*60)
    print("❌ 方舟API探索失败")
    print("\n建议:")
    print("1. 查看火山引擎控制台方舟服务页面")
    print("2. 获取具体的API调用示例")
    print("3. 确认服务开通状态")
    print("4. 检查API Key权限")

if __name__ == "__main__":
    main()