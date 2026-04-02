#!/usr/bin/env python3
"""
多模型配置与测试
立即设置多模型支持，测试各模型可用性
"""

import os
import json
import requests
from typing import Dict, List, Optional

class MultiModelSetup:
    """多模型配置管理器"""
    
    def __init__(self):
        self.config_path = os.path.expanduser("~/.openclaw/multi_model_config.json")
        self.test_results = {}
        
        # 默认配置
        self.default_config = {
            "providers": {
                "openai": {
                    "api_key": os.getenv("OPENAI_API_KEY", ""),
                    "base_url": "https://api.openai.com/v1",
                    "models": ["gpt-4", "gpt-4-turbo", "o1-mini", "o1-preview"],
                    "enabled": True
                },
                "deepseek": {
                    "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
                    "base_url": "https://api.deepseek.com/v1",
                    "models": ["deepseek-chat", "deepseek-reasoner"],
                    "enabled": True
                },
                "anthropic": {
                    "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
                    "base_url": "https://api.anthropic.com/v1",
                    "models": ["claude-3-sonnet", "claude-3-haiku"],
                    "enabled": True
                },
                "gemini": {
                    "api_key": os.getenv("GEMINI_API_KEY", ""),
                    "base_url": "https://generativelanguage.googleapis.com/v1",
                    "models": ["gemini-1.5-pro"],
                    "enabled": True
                }
            },
            "routing_strategy": {
                "cost_priority": {
                    "simple": "deepseek-chat",
                    "medium": "claude-3-haiku", 
                    "complex": "gpt-4-turbo"
                },
                "quality_priority": {
                    "simple": "claude-3-haiku",
                    "medium": "gpt-4",
                    "complex": "claude-3-sonnet"
                },
                "speed_priority": {
                    "simple": "gemini-1.5-pro",
                    "medium": "deepseek-chat",
                    "complex": "claude-3-haiku"
                }
            },
            "cost_limits": {
                "daily": 10.0,  # 每日10美元
                "monthly": 300.0,  # 每月300美元
                "per_call_warning": 0.10  # 单次调用超过0.1美元警告
            }
        }
    
    def load_config(self) -> Dict:
        """加载配置"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return self.default_config
    
    def save_config(self, config: Dict):
        """保存配置"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"配置已保存到: {self.config_path}")
    
    def test_provider(self, provider: str, config: Dict) -> bool:
        """测试提供商可用性"""
        api_key = config.get("api_key", "")
        base_url = config.get("base_url", "")
        
        if not api_key:
            print(f"[{provider}] 无API密钥，跳过测试")
            return False
        
        test_cases = {
            "openai": {
                "url": f"{base_url}/models",
                "headers": {"Authorization": f"Bearer {api_key}"}
            },
            "deepseek": {
                "url": f"{base_url}/models",
                "headers": {"Authorization": f"Bearer {api_key}"}
            },
            "anthropic": {
                "url": f"{base_url}/models",
                "headers": {
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01"
                }
            },
            "gemini": {
                "url": f"{base_url}/models/gemini-1.5-pro?key={api_key}",
                "headers": {}
            }
        }
        
        test_case = test_cases.get(provider)
        if not test_case:
            print(f"[{provider}] 无测试配置")
            return False
        
        try:
            print(f"[{provider}] 测试连接...")
            response = requests.get(test_case["url"], headers=test_case["headers"], timeout=10)
            
            if response.status_code == 200:
                print(f"[{provider}] ✅ 连接成功")
                return True
            else:
                print(f"[{provider}] ❌ 连接失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[{provider}] ❌ 测试异常: {e}")
            return False
    
    def test_all_providers(self):
        """测试所有提供商"""
        config = self.load_config()
        print("测试多模型提供商...")
        print("="*50)
        
        results = {}
        for provider, provider_config in config["providers"].items():
            if provider_config.get("enabled", True):
                success = self.test_provider(provider, provider_config)
                results[provider] = {
                    "success": success,
                    "has_key": bool(provider_config.get("api_key", "")),
                    "enabled": provider_config.get("enabled", True)
                }
        
        # 保存测试结果
        self.test_results = results
        
        # 打印总结
        print("\n" + "="*50)
        print("测试总结:")
        for provider, result in results.items():
            status = "✅ 可用" if result["success"] else "❌ 不可用"
            key_status = "有密钥" if result["has_key"] else "无密钥"
            print(f"  {provider}: {status} ({key_status})")
        
        available = sum(1 for r in results.values() if r["success"])
        print(f"\n可用提供商: {available}/{len(results)}")
        
        return results
    
    def create_model_router(self):
        """创建模型路由器"""
        router_code = '''
#!/usr/bin/env python3
"""
多模型智能路由器
根据任务类型、成本、性能选择最佳模型
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime

class MultiModelRouter:
    """多模型智能路由器"""
    
    def __init__(self, config_path="~/.openclaw/multi_model_config.json"):
        self.config_path = os.path.expanduser(config_path)
        self.config = self._load_config()
        
        # 成本表（美元/百万token）
        self.cost_table = {
            "openai/gpt-4": {"input": 0.03, "output": 0.06},
            "openai/gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "openai/o1-mini": {"input": 0.11, "output": 0.44},
            "deepseek/deepseek-chat": {"input": 0.14, "output": 0.28},
            "deepseek/deepseek-reasoner": {"input": 0.28, "output": 1.12},
            "anthropic/claude-3-sonnet": {"input": 0.03, "output": 0.15},
            "anthropic/claude-3-haiku": {"input": 0.025, "output": 0.125},
            "gemini/gemini-1.5-pro": {"input": 0.00125, "output": 0.005}
        }
        
        # 性能特征
        self.performance_profiles = {
            "reasoning": ["claude-3-sonnet", "deepseek-reasoner", "gpt-4"],
            "speed": ["gemini-1.5-pro", "claude-3-haiku", "deepseek-chat"],
            "cost": ["gemini-1.5-pro", "deepseek-chat", "claude-3-haiku"],
            "quality": ["gpt-4", "claude-3-sonnet", "deepseek-reasoner"]
        }
        
        # 使用统计
        self.usage_stats = {
            "total_calls": 0,
            "total_cost": 0.0,
            "by_model": {},
            "by_task": {}
        }
    
    def _load_config(self) -> Dict:
        """加载配置"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {}
    
    def select_model(self, task_type: str, complexity: str = "medium", 
                    priority: str = "balanced") -> str:
        """
        选择最佳模型
        
        参数:
            task_type: 任务类型 (analysis, prediction, summary, etc.)
            complexity: 复杂度 (simple, medium, complex)
            priority: 优先级 (cost, speed, quality, balanced)
        
        返回:
            模型标识符
        """
        # 获取可用模型
        available_models = self._get_available_models()
        if not available_models:
            return "deepseek-chat"  # 默认
        
        # 根据优先级选择策略
        if priority == "cost":
            # 成本优先：选择最便宜的
            candidates = self.performance_profiles["cost"]
        elif priority == "speed":
            # 速度优先：选择最快的
            candidates = self.performance_profiles["speed"]
        elif priority == "quality":
            # 质量优先：选择最好的
            candidates = self.performance_profiles["quality"]
        else:
            # 平衡：根据复杂度选择
            if complexity == "simple":
                candidates = self.performance_profiles["cost"]
            elif complexity == "complex":
                candidates = self.performance_profiles["quality"]
            else:
                candidates = self.performance_profiles["speed"]
        
        # 过滤可用模型
        available_candidates = [m for m in candidates if m in available_models]
        
        if not available_candidates:
            # 没有候选，返回第一个可用模型
            return available_models[0]
        
        # 选择第一个可用候选
        selected = available_candidates[0]
        
        # 记录使用
        self._record_usage(selected, task_type)
        
        return selected
    
    def _get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        available = []
        providers = self.config.get("providers", {})
        
        for provider, config in providers.items():
            if config.get("enabled", True) and config.get("api_key"):
                models = config.get("models", [])
                available.extend([f"{provider}/{model}" for model in models])
        
        return available
    
    def _record_usage(self, model: str, task_type: str):
        """记录使用情况"""
        self.usage_stats["total_calls"] += 1
        
        # 按模型统计
        if model not in self.usage_stats["by_model"]:
            self.usage_stats["by_model"][model] = 0
        self.usage_stats["by_model"][model] += 1
        
        # 按任务统计
        if task_type not in self.usage_stats["by_task"]:
            self.usage_stats["by_task"][task_type] = 0
        self.usage_stats["by_task"][task_type] += 1
    
    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """估算成本"""
        if model not in self.cost_table:
            return 0.0
        
        costs = self.cost_table[model]
        input_cost = (input_tokens / 1_000_000) * costs["input"]
        output_cost = (output_tokens / 1_000_000) * costs["output"]
        
        total = input_cost + output_cost
        self.usage_stats["total_cost"] += total
        
        return total
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_calls": self.usage_stats["total_calls"],
            "total_cost": round(self.usage_stats["total_cost"], 6),
            "by_model": self.usage_stats["by_model"],
            "by_task": self.usage_stats["by_task"],
            "available_models": self._get_available_models()
        }
    
    def print_stats(self):
        """打印统计信息"""
        stats = self.get_stats()
        print("多模型路由器统计:")
        print("="*50)
        print(f"总调用次数: {stats['total_calls']}")
        print(f"总成本: ${stats['total_cost']:.6f}")
        print(f"可用模型: {len(stats['available_models'])} 个")
        
        if stats['by_model']:
            print("\n按模型使用:")
            for model, count in stats['by_model'].items():
                print(f"  {model}: {count} 次")
        
        if stats['by_task']:
            print("\n按任务使用:")
            for task, count in stats['by_task'].items():
                print(f"  {task}: {count} 次")
        print("="*50)

# 使用示例
if __name__ == "__main__":
    router = MultiModelRouter()
    
    # 示例选择
    tasks = [
        ("price_analysis", "simple", "cost"),
        ("market_prediction", "medium", "balanced"),
        ("risk_assessment", "complex", "quality"),
        ("quick_check", "simple", "speed")
    ]
    
    print("模型选择示例:")
    for task_type, complexity, priority in tasks:
        model = router.select_model(task_type, complexity, priority)
        cost = router.estimate_cost(model, 100, 50)  # 估算100输入+50输出tokens
        print(f"任务: {task_type} ({complexity}, {priority}) -> 模型: {model}, 估算成本: ${cost:.6f}")
    
    router.print_stats()
'''
        
        router_path = os.path.join(os.path.dirname(__file__), "multi_model_router.py")
        with open(router_path, 'w') as f:
            f.write(router_code)
        
        print(f"模型路由器已创建: {router_path}")
        return router_path
    
    def integrate_with_quant_system(self):
        """与量化系统集成"""
        integration_code = '''
# 量化系统多模型集成示例
# 在现有量化脚本中添加以下代码

from multi_model_router import MultiModelRouter
from cached_api_wrapper import cached_chat_completion

class QuantModelEnhancer:
    """量化模型增强器"""
    
    def __init__(self):
        self.router = MultiModelRouter()
        self.task_mapping = {
            "market_analysis": ("analysis", "medium", "balanced"),
            "price_prediction": ("prediction", "complex", "quality"),
            "risk_assessment": ("risk", "complex", "quality"),
            "signal_verification": ("verification", "simple", "speed"),
            "portfolio_optimization": ("optimization", "complex", "quality"),
            "news_sentiment": ("sentiment", "medium", "speed")
        }
    
    def enhance_with_llm(self, market_data: Dict, task_type: str) -> Optional[Dict]:
        """使用LLM增强量化分析"""
        
        # 1. 选择模型
        if task_type not in self.task_mapping:
            return None
        
        task_profile = self.task_mapping[task_type]
        model = self.router.select_model(*task_profile)
        
        # 2. 准备提示词
        prompt = self._create_prompt(market_data, task_type)
        
        # 3. 调用API（带缓存）
        try:
            # 提取提供商和模型
            if "/" in model:
                provider, model_name = model.split("/", 1)
            else:
                provider = "deepseek"
                model_name = model
            
            # 使用缓存调用
            response = cached_chat_completion(
                provider=provider,
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )
            
            if response:
                # 4. 解析响应
                result = self._parse_response(response, task_type)
                
                # 5. 记录使用
                self.router.estimate_cost(model, len(prompt)//4, len(response)//4)
                
                return result
                
        except Exception as e:
            print(f"LLM增强失败: {e}")
        
        return None
    
    def _create_prompt(self, data: Dict, task_type: str) -> str:
        """创建提示词"""
        prompts = {
            "market_analysis": f"""
分析以下市场数据，给出交易建议：
{json.dumps(data, indent=2)}

请输出JSON格式：{{"action": "buy/sell/hold", "confidence": 0-1, "reason": "..."}}
""",
            "price_prediction": f"""
基于以下数据预测价格走势：
{json.dumps(data, indent=2)}

请输出JSON格式：{{"direction": "up/down/sideways", "confidence": 0-1, "timeframe": "..."}}
""",
            "risk_assessment": f"""
评估以下交易风险：
{json.dumps(data, indent=2)}

请输出JSON格式：{{"risk_level": "low/medium/high", "factors": [...], "suggestions": "..."}}
"""
        }
        
        return prompts.get(task_type, str(data))
    
    def _parse_response(self, response: str, task_type: str) -> Dict:
        """解析响应"""
        try:
            # 尝试解析JSON
            import json
            return json.loads(response)
        except:
            # 返回原始响应
            return {"raw_response": response, "task_type": task_type}
    
    def