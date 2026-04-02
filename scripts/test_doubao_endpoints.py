#!/usr/bin/env python3
"""
测试豆包API的不同端点
"""

import requests
import json

# 豆包API Key
API_KEY = "fbffb5c8-6497-47b7-b165-a2d3a25769c2"

# 可能的端点列表
ENDPOINTS = [
    "https://ark.cn-beijing.volces.com/api/v3",
    "https://ark.cn-beijing.volces.com/api/v1",
    "https://ark.cn-beijing.volces.com/api/v2", 
    "https://ark.cn-beijing.volces.com/api/chat",
    "https://ark.cn-beijing.volces.com/api",
    "https://dashscope.aliyuncs.com/api/v1",  # 阿里云通义
    "https://api.volcengine.com/ark/v1",  # 火山引擎
]

# 可能的模型名称
MODEL_NAMES = [
    "doubao-seed-2.0-lite",
    "doubao-seed-lite",
    "doubao-lite",
    "seed-2.0-lite",
    "doubao-pro",
    "doubao",
    "qwen-max",  # 通义千问
    "qwen-plus",
]

def test_endpoint(endpoint, model_name):
    """测试单个端点"""
    url = f"{endpoint}/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": "你好"}
        ],
        "max_tokens": 10
    }
    
    try:
        print(f"测试: {endpoint} | 模型: {model_name}")
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ 成功! 状态码: {response.status_code}")
            result = response.json()
            print(f"   响应: {result.get('choices', [{}])[0].get('message', {}).get('content', '无内容')[:50]}")
            return True, endpoint, model_name, result
        else:
            print(f"❌ 失败: {response.status_code} - {response.text[:100]}")
            return False, endpoint, model_name, response.text
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False, endpoint, model_name, str(e)

def main():
    print("测试豆包API端点")
    print("="*60)
    
    successful_tests = []
    
    for endpoint in ENDPOINTS:
        for model_name in MODEL_NAMES:
            success, ep, model, result = test_endpoint(endpoint, model_name)
            if success:
                successful_tests.append({
                    "endpoint": ep,
                    "model": model,
                    "result": result
                })
                # 找到成功就继续测试其他模型
                continue
    
    print("\n" + "="*60)
    print("测试总结:")
    
    if successful_tests:
        print(f"✅ 找到 {len(successful_tests)} 个可用配置:")
        for i, test in enumerate(successful_tests, 1):
            print(f"{i}. 端点: {test['endpoint']}")
            print(f"   模型: {test['model']}")
            
            # 提取使用信息
            if isinstance(test['result'], dict):
                usage = test['result'].get('usage', {})
                print(f"   Tokens: {usage}")
    else:
        print("❌ 未找到可用配置")
        
        # 尝试直接调用模型列表接口
        print("\n尝试调用模型列表接口...")
        for endpoint in ENDPOINTS:
            url = f"{endpoint}/models"
            headers = {"Authorization": f"Bearer {API_KEY}"}
            
            try:
                response = requests.get(url, headers=headers, timeout=10)
                print(f"{endpoint}/models -> {response.status_code}")
                if response.status_code == 200:
                    print(f"响应: {response.text[:200]}")
            except Exception as e:
                print(f"{endpoint}/models -> 异常: {e}")

if __name__ == "__main__":
    main()