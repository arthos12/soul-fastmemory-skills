#!/usr/bin/env python3
"""
测试豆包API使用AK/SK认证
"""

import requests
import json
import time
import hashlib
import hmac
import base64
from datetime import datetime
from urllib.parse import urlparse

class DoubaoAKSKTester:
    """豆包AK/SK认证测试器"""
    
    def __init__(self, access_key_id, secret_access_key):
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.base_url = "https://ark.cn-beijing.volces.com"
        
        # 解码SecretAccessKey (看起来是base64编码)
        try:
            self.secret_key = base64.b64decode(secret_access_key).decode('utf-8')
            print(f"SecretKey解码成功: {self.secret_key[:10]}...")
        except:
            print("SecretKey可能是原始字符串，直接使用")
            self.secret_key = secret_access_key
    
    def test_simple_auth(self):
        """测试简单认证方式"""
        print("\n1. 测试简单认证方式...")
        
        # 尝试直接使用AK/SK作为Bearer Token
        test_cases = [
            {
                "name": "Bearer with AccessKey",
                "auth": f"Bearer {self.access_key_id}",
                "endpoint": "/api/v3/chat/completions"
            },
            {
                "name": "Bearer with SecretKey", 
                "auth": f"Bearer {self.secret_key}",
                "endpoint": "/api/v3/chat/completions"
            },
            {
                "name": "X-API-Key with AccessKey",
                "headers": {"X-API-Key": self.access_key_id},
                "endpoint": "/api/v3/chat/completions"
            },
            {
                "name": "Authorization with AccessKey",
                "headers": {"Authorization": self.access_key_id},
                "endpoint": "/api/v3/chat/completions"
            }
        ]
        
        test_model = "doubao-lite-128k-240428"
        
        for test in test_cases:
            print(f"\n测试: {test['name']}")
            
            url = self.base_url + test["endpoint"]
            headers = {"Content-Type": "application/json"}
            
            if "auth" in test:
                headers["Authorization"] = test["auth"]
            elif "headers" in test:
                headers.update(test["headers"])
            
            payload = {
                "model": test_model,
                "messages": [{"role": "user", "content": "hello"}],
                "max_tokens": 5
            }
            
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=10)
                print(f"  状态码: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"  ✅ 成功!")
                    result = response.json()
                    print(f"  响应: {result.get('choices', [{}])[0].get('message', {}).get('content', '')}")
                    return True, test["name"], test_model
                else:
                    print(f"  响应: {response.text[:100]}")
                    
            except Exception as e:
                print(f"  异常: {e}")
        
        return False, None, None
    
    def test_volcengine_signature(self):
        """测试火山引擎签名认证"""
        print("\n2. 测试火山引擎签名认证...")
        
        # 火山引擎签名算法参考文档
        # https://www.volcengine.com/docs/6459/75268
        
        # 尝试使用火山引擎Python SDK的方式
        try:
            # 测试使用简单的日期签名
            import hashlib
            import hmac
            
            # 创建简单的签名
            service = "ark"
            region = "cn-beijing"
            action = "ChatCompletions"
            version = "2023-08-01"
            
            # 构建规范请求
            http_request_method = "POST"
            canonical_uri = "/"
            canonical_querystring = ""
            canonical_headers = "content-type:application/json\nhost:ark.cn-beijing.volces.com\n"
            signed_headers = "content-type;host"
            
            # 需要实际的请求体哈希
            payload = json.dumps({
                "model": "doubao-lite-128k-240428",
                "messages": [{"role": "user", "content": "hello"}],
                "max_tokens": 5
            })
            payload_hash = hashlib.sha256(payload.encode()).hexdigest()
            
            canonical_request = f"{http_request_method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
            
            # 创建待签字符串
            algorithm = "HMAC-SHA256"
            request_date = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            credential_scope = f"{request_date[:8]}/{region}/{service}/request"
            
            string_to_sign = f"{algorithm}\n{request_date}\n{credential_scope}\n" + \
                           hashlib.sha256(canonical_request.encode()).hexdigest()
            
            # 计算签名
            k_date = hmac.new(f"Volc{self.secret_key}".encode(), request_date[:8].encode(), hashlib.sha256).digest()
            k_region = hmac.new(k_date, region.encode(), hashlib.sha256).digest()
            k_service = hmac.new(k_region, service.encode(), hashlib.sha256).digest()
            k_signing = hmac.new(k_service, b"request", hashlib.sha256).digest()
            signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()
            
            # 构建授权头
            authorization_header = f"{algorithm} Credential={self.access_key_id}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
            
            print(f"生成的签名: {signature[:20]}...")
            print(f"授权头: {authorization_header[:50]}...")
            
            # 测试调用
            url = f"{self.base_url}/api/v3/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Host": "ark.cn-beijing.volces.com",
                "X-Date": request_date,
                "Authorization": authorization_header
            }
            
            response = requests.post(url, headers=headers, data=payload, timeout=10)
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ 签名认证成功!")
                return True, "volcengine_signature", "doubao-lite-128k-240428"
            else:
                print(f"  响应: {response.text[:200]}")
                
        except Exception as e:
            print(f"  签名计算异常: {e}")
        
        return False, None, None
    
    def test_with_sdk(self):
        """测试使用火山引擎SDK"""
        print("\n3. 尝试使用火山引擎SDK...")
        
        try:
            # 尝试导入火山引擎SDK
            import subprocess
            import sys
            
            # 检查是否已安装volcengine SDK
            try:
                import volcengine
                print("  ✅ volcengine SDK已安装")
            except ImportError:
                print("  ⚠️  volcengine SDK未安装，尝试安装...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "volcengine"])
                import volcengine
                print("  ✅ volcengine SDK安装成功")
            
            # 尝试使用豆包服务
            from volcengine.ark.ark_service import ArkService
            
            ark = ArkService()
            ark.set_ak(self.access_key_id)
            ark.set_sk(self.secret_key)
            
            # 设置区域
            ark.set_host('ark.cn-beijing.volces.com')
            
            # 尝试调用
            req = {
                "model": "doubao-lite-128k-240428",
                "messages": [
                    {
                        "role": "user",
                        "content": "hello"
                    }
                ],
                "max_tokens": 10
            }
            
            resp = ark.chat(req)
            print(f"  ✅ SDK调用成功!")
            print(f"  响应: {resp}")
            return True, "volcengine_sdk", "doubao-lite-128k-240428"
            
        except Exception as e:
            print(f"  SDK调用异常: {e}")
            return False, None, None
    
    def test_different_endpoints(self):
        """测试不同的端点"""
        print("\n4. 测试不同的端点...")
        
        endpoints = [
            "/api/v3/chat/completions",
            "/api/v1/chat/completions", 
            "/api/v2/chat/completions",
            "/chat/completions",
            "/v1/chat/completions",
            "/v3/chat/completions",
        ]
        
        # 尝试使用AccessKey作为Bearer Token
        headers = {
            "Authorization": f"Bearer {self.access_key_id}",
            "Content-Type": "application/json"
        }
        
        test_model = "doubao-lite-128k-240428"
        
        for endpoint in endpoints:
            url = self.base_url + endpoint
            
            payload = {
                "model": test_model,
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 5
            }
            
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=5)
                print(f"  端点 {endpoint}: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"    ✅ 成功!")
                    return True, endpoint, test_model
                elif response.status_code == 404:
                    continue
                else:
                    print(f"    响应: {response.text[:100]}")
                    
            except Exception as e:
                print(f"  端点 {endpoint}: 异常 - {e}")
        
        return False, None, None
    
    def find_working_model(self):
        """查找可用的模型"""
        print("\n5. 查找可用的模型名称...")
        
        endpoint = "/api/v3/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.access_key_id}",
            "Content-Type": "application/json"
        }
        
        model_candidates = [
            # 从模型列表中看到的
            "doubao-lite-128k-240428",
            "doubao-pro-128k-240515",
            "doubao-lite-32k-240428",
            "doubao-pro-4k-240515",
            "doubao-lite-4k-240328",
            
            # 常见简写
            "doubao-lite",
            "doubao-pro",
            "doubao",
            "seed-lite",
            "seed-pro",
            "seed",
            
            # 其他格式
            "Doubao-Lite",
            "Doubao-Pro",
        ]
        
        for model in model_candidates:
            url = self.base_url + endpoint
            
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
                    result = response.json()
                    print(f"    响应: {result.get('choices', [{}])[0].get('message', {}).get('content', '')}")
                    return True, endpoint, model
                elif "does not exist" in response.text:
                    continue
                elif "not have access" in response.text:
                    print(f"    ⚠️  无权限，但模型可能存在: {model}")
                    
            except Exception as e:
                print(f"  模型 '{model}': 异常 - {e}")
        
        return False, None, None

def main():
    print("豆包AK/SK认证测试")
    print("="*60)
    
    # AK/SK信息
    access_key_id = "AKLTYjFhMmNkMDc1MWFjNDNiYjkxZTBjMjFjZWE1Y2FkNTg"
    secret_access_key = "WVRFeU1tRTFObVZpTnpZd05EazJOR0V5T1RWaE56ZzBPRGcwWVRObU1UYw=="
    
    print(f"AccessKey ID: {access_key_id}")
    print(f"SecretAccessKey: {secret_access_key[:20]}...")
    
    # 创建测试器
    tester = DoubaoAKSKTester(access_key_id, secret_access_key)
    
    # 1. 测试简单认证
    success, auth_method, model = tester.test_simple_auth()
    if success:
        print(f"\n✅ 使用 {auth_method} 认证成功!")
        print(f"   模型: {model}")
        return
    
    # 2. 测试火山引擎签名
    success, auth_method, model = tester.test_volcengine_signature()
    if success:
        print(f"\n✅ 使用 {auth_method} 认证成功!")
        print(f"   模型: {model}")
        return
    
    # 3. 测试SDK
    success, auth_method, model = tester.test_with_sdk()
    if success:
        print(f"\n✅ 使用 {auth_method} 认证成功!")
        print(f"   模型: {model}")
        return
    
    # 4. 测试不同端点
    success, endpoint, model = tester.test_different_endpoints()
    if success:
        print(f"\n✅ 端点 {endpoint} 可用!")
        print(f"   模型: {model}")
        return
    
    # 5. 查找可用模型
    success, endpoint, model = tester.find_working_model()
    if success:
        print(f"\n✅ 找到可用模型!")
        print(f"   端点: {endpoint}")
        print(f"   模型: {model}")
        return
    
    print("\n" + "="*60)
    print("❌ 所有测试方法都失败")
    print("\n建议:")
    print("1. 检查火山引擎控制台豆包服务状态")
    print("2. 确认AK/SK有调用权限")
    print("3. 查看具体的API调用示例")
    print("4. 可能需要开通服务或充值")

if __name__ == "__main__":
    main()