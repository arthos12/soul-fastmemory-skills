#!/usr/bin/env python3
"""
测试豆包seed 2.0 Lite模型连通性
"""

import requests
import json
import os
from typing import Dict, Any

class DoubaoModelTester:
    """豆包模型测试器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://ark.cn-beijing.volces.com/api/v3"
        self.model_name = "doubao-seed-2.0-lite"
        
        # 请求头
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """测试连接"""
        print(f"测试豆包模型连接: {self.model_name}")
        print(f"API Key: {self.api_key[:8]}...{self.api_key[-4:]}")
        
        # 测试端点
        test_url = f"{self.base_url}/chat/completions"
        
        # 测试请求
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": "你好，请回复'测试成功'"}
            ],
            "max_tokens": 50,
            "temperature": 0.7
        }
        
        try:
            print(f"发送请求到: {test_url}")
            response = requests.post(
                test_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 连接成功!")
                print(f"模型响应: {result.get('choices', [{}])[0].get('message', {}).get('content', '无内容')}")
                
                # 提取使用信息
                usage = result.get("usage", {})
                print(f"Token使用: {usage}")
                
                return {
                    "success": True,
                    "model": self.model_name,
                    "response": result,
                    "usage": usage
                }
            else:
                print(f"❌ 连接失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "status_code": response.status_code
                }
                
        except requests.exceptions.Timeout:
            error_msg = "请求超时"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
            
        except requests.exceptions.ConnectionError:
            error_msg = "连接错误"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
            
        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
    
    def test_model_capabilities(self) -> Dict[str, Any]:
        """测试模型能力"""
        print(f"\n测试豆包模型能力...")
        
        tests = [
            {
                "name": "简单问答",
                "prompt": "中国的首都是哪里？",
                "expected_keywords": ["北京"]
            },
            {
                "name": "数学计算", 
                "prompt": "计算 123 + 456 等于多少？",
                "expected_keywords": ["579"]
            },
            {
                "name": "逻辑推理",
                "prompt": "如果所有猫都会爬树，Tom是一只猫，那么Tom会爬树吗？",
                "expected_keywords": ["会", "爬树"]
            }
        ]
        
        results = []
        
        for test in tests:
            print(f"\n测试: {test['name']}")
            print(f"提示: {test['prompt']}")
            
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "user", "content": test["prompt"]}
                ],
                "max_tokens": 100,
                "temperature": 0.3
            }
            
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    
                    # 检查是否包含预期关键词
                    contains_keyword = any(keyword in content for keyword in test["expected_keywords"])
                    
                    test_result = {
                        "name": test["name"],
                        "success": contains_keyword,
                        "response": content[:100] + "..." if len(content) > 100 else content,
                        "tokens": result.get("usage", {}).get("total_tokens", 0)
                    }
                    
                    if contains_keyword:
                        print(f"✅ 通过")
                    else:
                        print(f"⚠️  未检测到关键词，响应: {content[:50]}...")
                    
                else:
                    test_result = {
                        "name": test["name"],
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "response": response.text[:100]
                    }
                    print(f"❌ 失败: {response.status_code}")
                    
            except Exception as e:
                test_result = {
                    "name": test["name"],
                    "success": False,
                    "error": str(e)
                }
                print(f"❌ 异常: {e}")
            
            results.append(test_result)
        
        # 统计结果
        passed = sum(1 for r in results if r["success"])
        total = len(results)
        
        print(f"\n📊 能力测试结果: {passed}/{total} 通过")
        
        return {
            "results": results,
            "passed": passed,
            "total": total,
            "success_rate": passed / total if total > 0 else 0
        }
    
    def create_openclaw_config(self) -> str:
        """创建OpenClaw配置"""
        config = {
            "providers": {
                "doubao": {
                    "baseUrl": self.base_url,
                    "apiKey": self.api_key,
                    "api": "openai-completions",
                    "models": [
                        {
                            "id": self.model_name,
                            "name": "豆包seed 2.0 Lite",
                            "reasoning": False,
                            "input": ["text"],
                            "cost": {
                                "input": 0.000,  # 需要实际价格
                                "output": 0.000,
                                "cacheRead": 0,
                                "cacheWrite": 0
                            },
                            "contextWindow": 32000,
                            "maxTokens": 4000,
                            "supportsJson": True,
                            "supportsTools": False,
                            "supportsVision": False,
                            "supportsAudio": False
                        }
                    ]
                }
            }
        }
        
        config_json = json.dumps(config, indent=2, ensure_ascii=False)
        
        print(f"\n📝 OpenClaw配置模板:")
        print("="*60)
        print(config_json)
        print("="*60)
        
        return config_json
    
    def save_test_report(self, connection_result: Dict, capability_result: Dict):
        """保存测试报告"""
        report = {
            "timestamp": requests.utils.get_datetime_format(),
            "model": self.model_name,
            "api_key_preview": f"{self.api_key[:8]}...{self.api_key[-4:]}",
            "connection_test": connection_result,
            "capability_test": capability_result,
            "recommendation": {
                "can_use": connection_result.get("success", False),
                "suggested_use": "低成本日常对话、简单分析" if capability_result.get("success_rate", 0) > 0.5 else "需要进一步测试",
                "estimated_cost": "未知，需要查看官方定价"
            }
        }
        
        report_path = "/root/.openclaw/workspace/data/doubao_test_report.json"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 测试报告已保存到: {report_path}")
        
        return report_path

def main():
    """主函数"""
    print("豆包seed 2.0 Lite模型测试")
    print("="*60)
    
    # API Key
    api_key = "fbffb5c8-6497-47b7-b165-a2d3a25769c2"
    
    # 创建测试器
    tester = DoubaoModelTester(api_key)
    
    # 1. 测试连接
    print("\n1. 测试模型连接...")
    connection_result = tester.test_connection()
    
    if not connection_result.get("success", False):
        print("❌ 连接测试失败，停止后续测试")
        return
    
    # 2. 测试能力
    print("\n2. 测试模型能力...")
    capability_result = tester.test_model_capabilities()
    
    # 3. 创建配置
    print("\n3. 生成OpenClaw配置...")
    config_json = tester.create_openclaw_config()
    
    # 4. 保存报告
    print("\n4. 保存测试报告...")
    report_path = tester.save_test_report(connection_result, capability_result)
    
    # 5. 总结
    print("\n" + "="*60)
    print("✅ 豆包模型测试完成")
    print(f"连接状态: {'成功' if connection_result['success'] else '失败'}")
    print(f"能力测试: {capability_result.get('passed', 0)}/{capability_result.get('total', 0)} 通过")
    
    if connection_result["success"]:
        print("\n📋 下一步:")
        print("1. 在TG中手动切换模型到豆包")
        print("2. 使用命令: /model doubao/doubao-seed-2.0-lite")
        print("3. 测试实际使用效果")
        print("4. 监控token使用和成本")
    
    print("="*60)

if __name__ == "__main__":
    main()