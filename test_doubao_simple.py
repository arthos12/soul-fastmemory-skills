#!/usr/bin/env python3
import requests
import json
import base64
from datetime import datetime
import hashlib
import hmac

# AK/SK
ACCESS_KEY_ID = "AKLTYjFhMmNkMDc1MWFjNDNiYjkxZTBjMjFjZWE1Y2FkNTg"
SECRET_ACCESS_KEY = "WVRFeU1tRTFObVZpTnpZd05EazJOR0V5T1RWaE56ZzBPRGcwWVRObU1UYw=="

# 解码SecretKey
secret_key = base64.b64decode(SECRET_ACCESS_KEY).decode('utf-8')
print(f"AccessKey: {ACCESS_KEY_ID}")
print(f"SecretKey: {secret_key}")

# 火山引擎签名函数
def sign_request(access_key, secret_key, method, path, body=""):
    """简单的火山引擎签名"""
    # 简化版本，实际需要完整签名算法
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    
    # 构建待签名字符串
    string_to_sign = f"{method}\n{path}\n\n{timestamp}\n{body}"
    
    # 计算签名
    signature = hmac.new(
        secret_key.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return timestamp, signature

# 尝试调用
endpoint = "https://ark.cn-beijing.volces.com"
path = "/api/v3/chat/completions"
method = "POST"

# 请求体
payload = {
    "model": "doubao-lite-128k-240428",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 10
}
body = json.dumps(payload)

# 生成签名
timestamp, signature = sign_request(ACCESS_KEY_ID, secret_key, method, path, body)

# 构建请求头
headers = {
    "Content-Type": "application/json",
    "X-Date": timestamp,
    "Authorization": f"HmacSHA256 {ACCESS_KEY_ID}:{signature}"
}

print(f"\n请求头:")
for k, v in headers.items():
    print(f"  {k}: {v}")

# 发送请求
url = endpoint + path
print(f"\n发送请求到: {url}")

try:
    response = requests.post(url, headers=headers, data=body, timeout=10)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text[:200]}")
except Exception as e:
    print(f"请求异常: {e}")
