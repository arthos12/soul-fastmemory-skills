#!/usr/bin/env python3
"""
DeepSeek成本优化 - 立即落地实施
基于DeepSeek最新建议：提示词缓存 + 上下文精简 + V3.2极低成本
"""

import json
import time
import hashlib
from typing import Dict, List, Optional
import requests

class DeepSeekOptimizer:
    """DeepSeek成本优化器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1"
        
        # 本地缓存（弥补API缓存可能未启用）
        self.prompt_cache: Dict[str, dict] = {}
        self.response_cache: Dict[str, str] = {}
        
        # 统计信息
        self.stats = {
            "total_calls": 0,
            "cached_calls": 0,
            "total_tokens": 0,
            "estimated_savings": 0.0
        }
        
        # 优化配置
        self.config = {
            "model": "deepseek-chat",  # 假设为V3.2
            "max_tokens": 50,  # 限制输出长度
            "temperature": 0.1,  # 低随机性
            "cache_ttl": 300,  # 5分钟缓存
            "min_price_change": 0.5,  # 价格变动>0.5%才分析
            "cooldown_seconds": 60,  # 调用冷却时间
        }
        
        # 精简的系统提示词（固定，可缓存）
        self.system_prompts = {
            "quant_simple": "量化助手。输入:价格,指标。输出:action(buy/sell/hold)+reason(<20字)。",
            "quant_detailed": "量化分析。输入:数据。输出:JSON{action,reason,confidence}。",
            "signal_check": "信号检查。输入:指标。输出:YES/NO。",
        }
        
        # 最后调用时间记录
        self.last_call_time: Dict[str, float] = {}
    
    def generate_cache_key(self, messages: List[dict]) -> str:
        """生成缓存键"""
        content = json.dumps(messages, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
    
    def should_call_api(self, symbol: str, price_change: float = 0.0) -> bool:
        """判断是否应该调用API（条件触发）"""
        current_time = time.time()
        
        # 1. 调用冷却检查
        if current_time - self.last_call_time.get(symbol, 0) < self.config["cooldown_seconds"]:
            print(f"[{symbol}] 冷却中，跳过")
            return False
        
        # 2. 价格变动检查（高频信号过滤）
        if price_change < self.config["min_price_change"]:
            print(f"[{symbol}] 价格变动{price_change:.2f}% < {self.config['min_price_change']}%，跳过")
            return False
        
        return True
    
    def optimize_messages(self, symbol: str, data: dict, prompt_type: str = "quant_simple") -> List[dict]:
        """优化消息结构，减少token使用"""
        
        # 使用精简的系统提示词
        system_content = self.system_prompts.get(prompt_type, self.system_prompts["quant_simple"])
        
        # 压缩用户输入（技术指标替代原始数据）
        if prompt_type == "quant_simple":
            # 简单格式：只发送关键指标
            user_content = f"{symbol}:{data.get('price',0)},MA5:{data.get('ma5',0)},RSI:{data.get('rsi',50)}"
            if data.get('bb_break'):
                user_content += f",突破:{data['bb_break']}"
        else:
            # 详细格式但仍压缩
            user_content = json.dumps({
                "symbol": symbol,
                "price": data.get("price"),
                "indicators": {
                    "ma5": data.get("ma5"),
                    "ma20": data.get("ma20"),
                    "rsi": data.get("rsi"),
                    "volume_change": data.get("volume_change"),
                },
                "signals": {
                    "bb_break": data.get("bb_break"),
                    "trend": data.get("trend"),
                }
            }, ensure_ascii=False)
        
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]
    
    def call_api_optimized(self, symbol: str, data: dict, prompt_type: str = "quant_simple") -> Optional[str]:
        """优化后的API调用"""
        
        # 1. 条件检查
        price_change = abs(data.get("price_change", 0))
        if not self.should_call_api(symbol, price_change):
            return None
        
        # 2. 优化消息结构
        messages = self.optimize_messages(symbol, data, prompt_type)
        
        # 3. 检查本地缓存
        cache_key = self.generate_cache_key(messages)
        if cache_key in self.response_cache:
            print(f"[{symbol}] 使用本地缓存结果")
            self.stats["cached_calls"] += 1
            # 估算节省：假设每次调用平均60 tokens
            self.stats["estimated_savings"] += 60 * 0.000001  # 粗略估算
            return self.response_cache[cache_key]
        
        # 4. 准备API调用
        payload = {
            "model": self.config["model"],
            "messages": messages,
            "max_tokens": self.config["max_tokens"],
            "temperature": self.config["temperature"],
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        # 5. 调用API
        try:
            print(f"[{symbol}] 调用API...")
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                self.stats["total_calls"] += 1
                
                # 记录token使用
                usage = result.get("usage", {})
                tokens = usage.get("total_tokens", 0)
                self.stats["total_tokens"] += tokens
                
                # 检查API缓存命中
                cache_hit = usage.get("prompt_cache_hit_tokens", 0)
                if cache_hit > 0:
                    print(f"[{symbol}] API缓存命中: {cache_hit} tokens")
                
                # 获取响应内容
                content = result["choices"][0]["message"]["content"]
                
                # 更新本地缓存
                self.response_cache[cache_key] = content
                self.last_call_time[symbol] = time.time()
                
                # 设置缓存过期
                def clear_cache():
                    if cache_key in self.response_cache:
                        del self.response_cache[cache_key]
                # 实际应用中可以使用定时器，这里简化
                
                return content
            else:
                print(f"[{symbol}] API错误: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[{symbol}] 调用异常: {e}")
            return None
    
    def batch_analyze(self, symbols_data: Dict[str, dict]) -> Dict[str, str]:
        """批量分析多个币种（合并请求优化）"""
        results = {}
        
        # 简单实现：实际可以合并到一个请求中
        # 这里先按顺序处理，但使用优化策略
        for symbol, data in symbols_data.items():
            # 根据数据类型选择提示词
            if data.get("complex_analysis", False):
                prompt_type = "quant_detailed"
            else:
                prompt_type = "quant_simple"
            
            result = self.call_api_optimized(symbol, data, prompt_type)
            if result:
                results[symbol] = result
        
        return results
    
    def print_stats(self):
        """打印统计信息"""
        print("\n" + "="*60)
        print("DeepSeek优化统计")
        print("="*60)
        print(f"总API调用次数: {self.stats['total_calls']}")
        print(f"本地缓存命中: {self.stats['cached_calls']}")
        print(f"总Tokens使用: {self.stats['total_tokens']}")
        
        # 估算成本
        # DeepSeek价格参考：输入$0.14/百万，输出$0.28/百万
        # 假设平均50%输入，50%输出
        input_cost = (self.stats['total_tokens'] * 0.5) / 1_000_000 * 0.14
        output_cost = (self.stats['total_tokens'] * 0.5) / 1_000_000 * 0.28
        total_cost = input_cost + output_cost
        
        print(f"估算成本: ${total_cost:.6f}")
        print(f"估算节省: ${self.stats['estimated_savings']:.6f} (本地缓存)")
        
        # 与未优化对比估算
        # 假设未优化：每次调用100 tokens，无缓存，高频调用
        unoptimized_calls = self.stats['total_calls'] + self.stats['cached_calls']
        unoptimized_tokens = unoptimized_calls * 100
        unoptimized_cost = (unoptimized_tokens / 1_000_000) * 0.21  # 平均价
        
        savings_percent = (1 - total_cost / unoptimized_cost) * 100 if unoptimized_cost > 0 else 0
        print(f"与未优化对比节省: {savings_percent:.1f}%")
        print("="*60)

def simulate_market_data():
    """模拟市场数据"""
    return {
        "BTC": {
            "price": 45000.0,
            "ma5": 44850.0,
            "ma20": 44600.0,
            "rsi": 62.0,
            "volume_change": 0.3,
            "bb_break": "upper",
            "price_change": 1.2,  # 价格变动1.2%
            "trend": "bullish",
            "complex_analysis": False,
        },
        "ETH": {
            "price": 3200.0,
            "ma5": 3180.0,
            "ma20": 3150.0,
            "rsi": 58.0,
            "volume_change": 0.1,
            "bb_break": None,
            "price_change": 0.3,  # 价格变动0.3%，可能被过滤
            "trend": "neutral",
            "complex_analysis": False,
        },
        "SOL": {
            "price": 110.0,
            "ma5": 108.0,
            "ma20": 105.0,
            "rsi": 72.0,  # 超买
            "volume_change": 0.8,
            "bb_break": "upper",
            "price_change": 2.5,  # 价格变动2.5%
            "trend": "bullish",
            "complex_analysis": True,  # 需要详细分析
        }
    }

def main():
    """主演示函数"""
    print("DeepSeek成本优化 - 立即落地实施")
    print("基于: 提示词缓存 + 上下文精简 + V3.2极低成本")
    print("="*60)
    
    # 注意：实际使用需要有效的API key
    # 这里使用示例key，实际会失败但展示流程
    optimizer = DeepSeekOptimizer(api_key="sk-4f508f0198ac4d1ebbc068a78695c3a5")
    
    # 模拟市场数据
    market_data = simulate_market_data()
    
    print("\n第一次批量分析:")
    results1 = optimizer.batch_analyze(market_data)
    for symbol, result in results1.items():
        print(f"  {symbol}: {result[:50]}...")
    
    print("\n等待10秒...")
    time.sleep(10)
    
    print("\n第二次批量分析（部分可能被过滤或缓存）:")
    # 更新一些数据
    market_data["BTC"]["price_change"] = 0.2  # 变动变小，可能被过滤
    market_data["ETH"]["price_change"] = 1.5  # 变动变大，可能通过
    market_data["SOL"]["price_change"] = 0.1  # 变动变小，可能被过滤
    
    results2 = optimizer.batch_analyze(market_data)
    for symbol, result in results2.items():
        print(f"  {symbol}: {result[:50]}...")
    
    # 打印统计
    optimizer.print_stats()
    
    print("\n优化措施总结:")
    print("1. 条件触发: 价格变动>0.5%才分析")
    print("2. 调用冷却: 60秒内不重复调用同一币种")
    print("3. 本地缓存: 相同输入缓存结果")
    print("4. 消息压缩: 技术指标替代原始数据")
    print("5. 输出限制: max_tokens=50")
    print("6. 提示词精简: 固定格式系统提示")
    print("\n预期效果: 成本降低50-90%")

if __name__ == "__main__":
    main()