#!/usr/bin/env python3
"""
火山引擎签名版本4算法实现
参考: https://www.volcengine.com/docs/6459/75268
"""

import hashlib
import hmac
import json
import base64
from datetime import datetime
from urllib.parse import urlparse, quote
import requests

class VolcengineSignerV4:
    """火山引擎签名版本4"""
    
    def __init__(self, access_key_id, secret_access_key):
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        
        # 解码SecretKey
        try:
            self.secret_key = base64.b64decode(secret_access_key).decode('utf-8')
        except:
            self.secret_key = secret_access_key
    
    def sha256_hash(self, data):
        """计算SHA256哈希"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha256(data).hexdigest()
    
    def hmac_sha256(self, key, data):
        """计算HMAC-SHA256"""
        if isinstance(key, str):
            key = key.encode('utf-8')
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hmac.new(key, data, hashlib.sha256).digest()
    
    def get_canonical_request(self, method, path, query_params, headers, payload_hash):
        """构建规范请求"""
        # 规范方法
        canonical_method = method.upper()
        
        # 规范URI
        canonical_uri = quote(path, safe='/~')
        
        # 规范查询字符串 (按参数名排序)
        canonical_querystring = ''
        if query_params:
            sorted_params = sorted(query_params.items(), key=lambda x: x[0])
            canonical_querystring = '&'.join(
                [f"{quote(k, safe='-_.~')}={quote(str(v), safe='-_.~')}" for k, v in sorted_params]
            )
        
        # 规范头部 (按头部名小写排序)
        canonical_headers = ''
        signed_headers = ''
        if headers:
            # 过滤并小写化头部名
            header_dict = {}
            for k, v in headers.items():
                if k.lower() in ['content-type', 'host', 'x-date']:
                    header_dict[k.lower()] = v.strip()
            
            # 按头部名排序
            sorted_headers = sorted(header_dict.items(), key=lambda x: x[0])
            
            canonical_headers = '\n'.join([f"{k}:{v}" for k, v in sorted_headers]) + '\n'
            signed_headers = ';'.join([k for k, _ in sorted_headers])
        
        # 构建规范请求
        canonical_request = f"{canonical_method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
        
        return canonical_request, signed_headers
    
    def get_string_to_sign(self, timestamp, credential_scope, canonical_request_hash):
        """构建待签名字符串"""
        algorithm = 'HMAC-SHA256'
        return f"{algorithm}\n{timestamp}\n{credential_scope}\n{canonical_request_hash}"
    
    def get_signing_key(self, date_stamp, region, service):
        """计算签名密钥"""
        k_date = self.hmac_sha256(f"Volc{self.secret_key}".encode('utf-8'), date_stamp)
        k_region = self.hmac_sha256(k_date, region)
        k_service = self.hmac_sha256(k_region, service)
        k_signing = self.hmac_sha256(k_service, b'request')
        return k_signing
    
    def sign_request(self, method, url, headers=None, body='', region='cn-beijing', service='ark'):
        """签名请求"""
        # 解析URL
        parsed_url = urlparse(url)
        path = parsed_url.path or '/'
        host = parsed_url.hostname
        
        # 获取当前时间
        now = datetime.utcnow()
        timestamp = now.strftime('%Y%m%dT%H%M%SZ')
        date_stamp = now.strftime('%Y%m%d')
        
        # 计算负载哈希
        if isinstance(body, dict):
            body_str = json.dumps(body)
        else:
            body_str = str(body)
        payload_hash = self.sha256_hash(body_str)
        
        # 确保必要的头部
        if headers is None:
            headers = {}
        
        headers['Host'] = host
        headers['X-Date'] = timestamp
        headers['Content-Type'] = headers.get('Content-Type', 'application/json')
        
        # 构建规范请求
        canonical_request, signed_headers = self.get_canonical_request(
            method, path, {}, headers, payload_hash
        )
        canonical_request_hash = self.sha256_hash(canonical_request)
        
        # 构建凭证范围
        credential_scope = f"{date_stamp}/{region}/{service}/request"
        
        # 构建待签名字符串
        string_to_sign = self.get_string_to_sign(timestamp, credential_scope, canonical_request_hash)
        
        # 计算签名密钥
        signing_key = self.get_signing_key(date_stamp, region, service)
        
        # 计算签名
        signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
        
        # 构建授权头
        authorization_header = f"HMAC-SHA256 Credential={self.access_key_id}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
        
        # 添加授权头
        headers['Authorization'] = authorization_header
        
        return headers, body_str

def test_doubao_api():
    """测试豆包API"""
    print("测试豆包API调用...")
    
    # AK/SK
    access_key_id = "AKLTYjFhMmNkMDc1MWFjNDNiYjkxZTBjMjFjZWE1Y2FkNTg"
    secret_access_key = "WVRFeU1tRTFObVZpTnpZd05EazJOR0V5T1RWaE56ZzBPRGcwWVRObU1UYw=="
    
    # 创建签名器
    signer = VolcengineSignerV4(access_key_id, secret_access_key)
    
    # API端点
    url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    
    # 请求体
    body = {
        "model": "doubao-lite-128k-240428",
        "messages": [
            {
                "role": "user",
                "content": "Hello, please introduce yourself."
            }
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    # 签名请求
    headers, body_str = signer.sign_request("POST", url, body=body)
    
    print(f"URL: {url}")
    print(f"Method: POST")
    print(f"\nHeaders:")
    for k, v in headers.items():
        print(f"  {k}: {v}")
    
    print(f"\nBody: {body_str[:100]}...")
    
    # 发送请求
    try:
        response = requests.post(url, headers=headers, data=body_str, timeout=30)
        print(f"\n响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 调用成功!")
            result = response.json()
            print(f"响应: {result.get('choices', [{}])[0].get('message', {}).get('content', '')}")
            print(f"使用情况: {result.get('usage', {})}")
        else:
            print(f"响应: {response.text[:500]}")
            
    except Exception as e:
        print(f"请求异常: {e}")

def test_simple_auth():
    """测试简单认证"""
    print("\n" + "="*60)
    print("测试简单认证方式...")
    
    # 尝试使用火山引擎可能接受的简单格式
    access_key_id = "AKLTYjFhMmNkMDc1MWFjNDNiYjkxZTBjMjFjZWE1Y2FkNTg"
    
    # 直接使用AccessKey作为Bearer Token
    url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    headers = {
        "Authorization": f"Bearer {access_key_id}",
        "Content-Type": "application/json"
    }
    
    body = {
        "model": "doubao-lite-128k-240428",
        "messages": [{"role": "user", "content": "test"}],
        "max_tokens": 10
    }
    
    try:
        response = requests.post(url, headers=headers, json=body, timeout=10)
        print(f"简单Bearer Token状态码: {response.status_code}")
        print(f"响应: {response.text[:200]}")
    except Exception as e:
        print(f"简单认证异常: {e}")

def main():
    print("火山引擎签名测试")
    print("="*60)
    
    # 测试简单认证
    test_simple_auth()
    
    # 测试完整签名
    print("\n" + "="*60)
    print("测试完整签名算法...")
    test_doubao_api()

if __name__ == "__main__":
    main()