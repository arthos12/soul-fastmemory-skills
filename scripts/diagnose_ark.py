#!/usr/bin/env python3
"""
诊断方舟API问题
"""

import requests
import json
import time

API_KEY = "fbffb5c8-6497-47b7-b165-a2d3a25769c2"

def diagnose():
    print("🔍 诊断方舟API问题")
    print("="*60)
    
    # 测试1: 检查网络连接
    print("\n1. 检查网络连接...")
    try:
        response = requests.get("https://ark.cn-beijing.volces.com", timeout=5)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ 服务可访问 (401表示需要认证)")
        else:
            print(f"   响应: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 连接失败: {e}")
        return
    
    # 测试2: 检查模型列表读取权限
    print("\n2. 检查模型列表读取权限...")
    try:
        url = "https://ark.cn-beijing.volces.com/api/v3/models"
        headers = {"Authorization": f"Bearer {API_KEY}"}
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "data" in data:
                models = data["data"]
                print(f"   ✅ 可读取模型列表 ({len(models)} 个模型)")
                
                # 查找seed相关模型
                seed_models = [m for m in models if "seed" in m.get("id", "").lower()]
                print(f"   Seed相关模型: {len(seed_models)} 个")
                for model in seed_models[:3]:
                    print(f"     - {model.get('id')}")
            else:
                print(f"   响应格式: {data}")
        else:
            print(f"   响应: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ 读取失败: {e}")
    
    # 测试3: 测试Seed端点
    print("\n3. 测试Seed端点...")
    endpoints = [
        "https://ark.cn-beijing.volces.com/api/seed/v3/chat/completions",
        "https://ark.cn-beijing.volces.com/seed/v3/chat/completions",
        "https://ark.cn-beijing.volces.com/api/seed/chat/completions",
    ]
    
    for url in endpoints:
        print(f"\n   测试端点: {url}")
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "doubao-seed-2-0-lite",
            "messages": [{"role": "user", "content": "test"}],
            "max_tokens": 5
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            print(f"     状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("     ✅ 调用成功!")
                data = response.json()
                print(f"     响应: {data.get('choices', [{}])[0].get('message', {}).get('content', '')}")
                return True, url
            elif response.status_code == 404:
                print("     ❌ 404 - 端点不存在")
            elif response.status_code == 401:
                print("     ❌ 401 - 认证失败")
                print(f"     响应: {response.text[:100]}")
            else:
                print(f"     响应: {response.text[:100]}")
                
        except requests.exceptions.Timeout:
            print("     ⏱️  请求超时")
        except Exception as e:
            print(f"     ❌ 异常: {e}")
    
    # 测试4: 检查API Key格式
    print("\n4. 检查API Key...")
    print(f"   Key: {API_KEY}")
    print(f"   长度: {len(API_KEY)} 字符")
    print(f"   格式: {'UUID格式' if len(API_KEY) == 36 and '-' in API_KEY else '其他格式'}")
    
    # 测试5: 尝试其他认证方式
    print("\n5. 尝试其他认证方式...")
    auth_variants = [
        {"Authorization": f"Bearer {API_KEY}"},
        {"Authorization": f"bearer {API_KEY}"},
        {"X-API-Key": API_KEY},
        {"api-key": API_KEY},
    ]
    
    url = "https://ark.cn-beijing.volces.com/api/seed/v3/chat/completions"
    payload = {
        "model": "doubao-seed-2-0-lite",
        "messages": [{"role": "user", "content": "test"}],
        "max_tokens": 5
    }
    
    for auth in auth_variants:
        headers = {"Content-Type": "application/json"}
        headers.update(auth)
        
        auth_type = list(auth.keys())[0]
        print(f"\n   测试认证: {auth_type}")
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=5)
            print(f"     状态码: {response.status_code}")
            if response.status_code != 404:
                print(f"     响应: {response.text[:100]}")
        except Exception as e:
            print(f"     异常: {e}")
    
    return False, None

def main():
    print("方舟API诊断报告")
    print("="*60)
    
    success, endpoint = diagnose()
    
    if success:
        print(f"\n✅ 诊断完成 - 找到可用端点: {endpoint}")
        print(f"\n下一步:")
        print(f"1. 更新OpenClaw配置使用此端点")
        print(f"2. 重启OpenClaw gateway")
        print(f"3. 测试模型调用")
    else:
        print(f"\n❌ 诊断完成 - 所有测试失败")
        print(f"\n问题分析:")
        print(f"1. API Key可能只有读取权限")
        print(f"2. Seed服务可能未开通")
        print(f"3. 端点地址可能不正确")
        print(f"4. 网络或服务临时问题")
        
        print(f"\n建议:")
        print(f"1. 检查方舟控制台服务状态")
        print(f"2. 确认API Key有调用权限")
        print(f"3. 联系技术支持")
        print(f"4. 稍后重试")

if __name__ == "__main__":
    main()