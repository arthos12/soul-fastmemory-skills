#!/usr/bin/env python3
"""
最终Seed模型测试
"""

import requests
import json
import sys

# 最终正确配置
API_KEY = "fbffb5c8-6497-47b7-b165-a2d3a25769c2"
BASE_URL = "https://ark.cn-beijing.volces.com/api/seed/v3"
MODEL = "doubao-seed-2-0-lite"

def test_seed_model():
    """测试Seed模型"""
    print("🎯 最终Seed模型测试")
    print("="*60)
    print(f"模型: {MODEL}")
    print(f"接入点: {BASE_URL}")
    print(f"API Key: {API_KEY[:8]}...{API_KEY[-4:]}")
    print("="*60)
    
    url = f"{BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "你好，请简单介绍一下自己，然后说'测试成功'"
            }
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    try:
        print("\n发送请求...")
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 调用成功!")
            print("\n响应内容:")
            print("-"*40)
            print(result.get("choices", [{}])[0].get("message", {}).get("content", ""))
            print("-"*40)
            
            # 显示使用情况
            usage = result.get("usage", {})
            if usage:
                print(f"\nToken使用:")
                print(f"  输入: {usage.get('prompt_tokens', 0)}")
                print(f"  输出: {usage.get('completion_tokens', 0)}")
                print(f"  总计: {usage.get('total_tokens', 0)}")
            
            return True, result
            
        else:
            print(f"\n❌ 请求失败")
            print(f"响应: {response.text[:200]}")
            
            try:
                error_data = response.json()
                if "error" in error_data:
                    print(f"错误代码: {error_data['error'].get('code', '未知')}")
                    print(f"错误信息: {error_data['error'].get('message', '未知')}")
            except:
                pass
                
            return False, response.text
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False, "Timeout"
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误")
        return False, "ConnectionError"
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False, str(e)

def update_openclaw_config():
    """更新OpenClaw配置"""
    print("\n" + "="*60)
    print("更新OpenClaw配置...")
    
    config = {
        "baseUrl": BASE_URL,
        "apiKey": API_KEY,
        "api": "openai-completions",
        "models": [
            {
                "id": MODEL,
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
    
    # 保存配置
    config_path = "/root/.openclaw/workspace/data/seed_final_config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 配置已保存到: {config_path}")
    
    # 显示配置命令
    config_json = json.dumps(config, ensure_ascii=False)
    print(f"\nOpenClaw配置命令:")
    print("-"*40)
    print(f"openclaw config set 'models.providers.volcengine' --json '{config_json}'")
    print("-"*40)
    
    return config

def main():
    # 1. 测试模型
    success, result = test_seed_model()
    
    if success:
        print("\n" + "="*60)
        print("🎉 Seed模型测试完全成功!")
        print("="*60)
        
        # 2. 更新配置
        config = update_openclaw_config()
        
        print(f"\n✅ 最终配置验证完成!")
        print(f"\n下一步:")
        print(f"1. 重启OpenClaw gateway")
        print(f"2. 在TG中使用命令: /model volcengine/doubao-seed-2-0-lite")
        print(f"3. 开始使用方舟Seed模型")
        
    else:
        print("\n" + "="*60)
        print("❌ Seed模型测试失败")
        print("="*60)
        
        print(f"\n可能原因:")
        print(f"1. 网络连接问题")
        print(f"2. 端点地址可能还需要调整")
        print(f"3. 服务临时不可用")
        
        print(f"\n建议:")
        print(f"1. 检查网络连接")
        print(f"2. 确认端点地址完全正确")
        print(f"3. 稍后重试")

if __name__ == "__main__":
    main()