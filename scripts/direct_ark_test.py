#!/usr/bin/env python3
"""
直接测试方舟API
"""

import requests
import json

def test_direct():
    """直接测试"""
    api_key = "fbffb5c8-6497-47b7-b165-a2d3a25769c2"
    
    # 根据常见模式，可能有两种情况：
    # 1. 端点: https://ark.cn-beijing.volces.com/api/seed/v3
    # 2. 或者: https://ark.cn-beijing.volces.com/api/v3 (但用seed模型)
    
    test_cases = [
        {
            "name": "Seed专用端点",
            "base_url": "https://ark.cn-beijing.volces.com/api/seed/v3",
            "model": "doubao-seed-2-0-lite"
        },
        {
            "name": "通用端点 + Seed模型",
            "base_url": "https://ark.cn-beijing.volces.com/api/v3",
            "model": "doubao-seed-2-0-lite"
        },
        {
            "name": "通用端点 + 普通模型",
            "base_url": "https://ark.cn-beijing.volces.com/api/v3",
            "model": "doubao-lite-128k-240428"
        }
    ]
    
    for test in test_cases:
        print(f"\n测试: {test['name']}")
        print(f"端点: {test['base_url']}")
        print(f"模型: {test['model']}")
        
        url = f"{test['base_url']}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": test["model"],
            "messages": [{"role": "user", "content": "hello"}],
            "max_tokens": 10
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 成功!")
                print(f"响应: {result.get('choices', [{}])[0].get('message', {}).get('content', '')}")
                return True, test
            else:
                print(f"响应: {response.text[:150]}")
                
        except Exception as e:
            print(f"异常: {e}")
    
    return False, None

if __name__ == "__main__":
    print("直接测试方舟API")
    print("="*60)
    
    success, config = test_direct()
    
    if success:
        print(f"\n✅ 测试成功!")
        print(f"使用配置: {config}")
    else:
        print(f"\n❌ 所有测试失败")
        print(f"\n建议检查:")
        print(f"1. API Key权限")
        print(f"2. 服务开通状态")
        print(f"3. 网络连接")
        print(f"4. 端点地址准确性")