#!/usr/bin/env python3
"""
Token优化技术实现示例
基于DeepSeek建议的七个维度优化

此示例展示如何在实际量化系统中应用token优化策略
"""

import time
import json
from datetime import datetime
from typing import Dict, Optional

# 模拟缓存和调用记录
cache: Dict[str, dict] = {}
last_call_time: Dict[str, float] = {}
call_count = 0

def get_market_data(symbol: str) -> dict:
    """获取市场数据并计算技术指标（模拟）"""
    # 实际实现中，这里会调用交易所API
    # 返回计算后的技术指标，而不是原始K线数据
    return {
        "symbol": symbol,
        "price": 45000.0,
        "ma5": 44850.0,
        "ma20": 44600.0,
        "rsi": 62.0,
        "volume_change": 0.3,  # 较前5分钟均值+30%
        "bb_upper_break": True,  # 突破布林带上轨
        "timestamp": datetime.now().isoformat()
    }

def get_orderbook_summary(symbol: str) -> str:
    """压缩订单簿数据（DeepSeek建议一）"""
    # 实际实现中，这里会获取完整订单簿
    # 优化：只返回前3档和买卖压力比
    return f"{symbol}: 买一 45000 (2 BTC), 卖一 45005 (1.5 BTC), 买卖比 1.3"

def should_call_ai(symbol: str, data: dict) -> bool:
    """
    判断是否应该调用AI（DeepSeek建议三）
    条件触发而非定时轮询
    """
    current_time = time.time()
    
    # 1. 调用冷却时间检查（至少间隔60秒）
    if current_time - last_call_time.get(symbol, 0) < 60:
        print(f"[{symbol}] 调用冷却中，跳过")
        return False
    
    # 2. 价格波动检查（变动小于0.5%不调用）
    price_change = abs(data.get("price_change", 0))
    if price_change < 0.5:
        print(f"[{symbol}] 价格变动{price_change:.2f}% < 0.5%，跳过")
        return False
    
    # 3. 技术指标触发条件
    rsi = data.get("rsi", 50)
    if 30 <= rsi <= 70:  # RSI在正常区间
        print(f"[{symbol}] RSI={rsi}在正常区间，跳过")
        return False
    
    # 4. 突破信号检查
    if not data.get("bb_upper_break", False) and not data.get("bb_lower_break", False):
        print(f"[{symbol}] 无突破信号，跳过")
        return False
    
    return True

def construct_ai_prompt(symbols_data: list) -> str:
    """
    构造AI提示词（DeepSeek建议二）
    合并多个分析请求，明确输出格式
    """
    # 数据摘要
    summaries = []
    for data in symbols_data:
        summary = f"{data['symbol']}: {data['price']}, MA5:{data['ma5']}, RSI:{data['rsi']}"
        summaries.append(summary)
    
    # 明确约束的提示词
    prompt = f"""
请分析以下币种当前趋势，分别给出交易建议（buy/sell/hold）：

{chr(10).join(summaries)}

规则：
1. 每个币种只输出"buy"、"sell"、"hold"三选一
2. 原因控制在10字以内
3. 输出JSON格式：{{"BTC":"buy:突破阻力", "ETH":"hold:震荡区间", ...}}

请严格遵守输出格式。
"""
    return prompt.strip()

def simulate_ai_call(prompt: str) -> str:
    """模拟AI调用（实际会调用DeepSeek API）"""
    global call_count
    call_count += 1
    
    # 模拟AI响应
    response = {
        "BTC": "buy:突破布林带上轨",
        "ETH": "hold:RSI正常区间",
        "SOL": "sell:RSI超买"
    }
    
    print(f"[AI调用 #{call_count}] 输入tokens: ~{len(prompt)//4}, 输出tokens: ~50")
    return json.dumps(response)

def query_ai_with_optimization(symbols: list) -> dict:
    """优化后的AI查询函数"""
    results = {}
    symbols_to_analyze = []
    
    for symbol in symbols:
        # 1. 获取市场数据（已计算技术指标）
        data = get_market_data(symbol)
        
        # 2. 检查缓存（DeepSeek建议五）
        cache_key = f"{symbol}_{int(time.time()//60)}"  # 每分钟一个缓存键
        if cache_key in cache:
            print(f"[{symbol}] 使用缓存结果")
            results[symbol] = cache[cache_key]
            continue
        
        # 3. 判断是否应该调用AI
        if should_call_ai(symbol, data):
            symbols_to_analyze.append({"symbol": symbol, **data})
        else:
            results[symbol] = "hold:条件未触发"
    
    # 4. 合并请求分析（DeepSeek建议三）
    if symbols_to_analyze:
        # 构造优化后的提示词
        prompt = construct_ai_prompt(symbols_to_analyze)
        
        # 调用AI（实际实现中会设置max_tokens=50）
        ai_response = simulate_ai_call(prompt)
        
        try:
            ai_results = json.loads(ai_response)
            # 更新结果和缓存
            for symbol_data in symbols_to_analyze:
                symbol = symbol_data["symbol"]
                if symbol in ai_results:
                    results[symbol] = ai_results[symbol]
                    # 更新缓存
                    cache_key = f"{symbol}_{int(time.time()//60)}"
                    cache[cache_key] = ai_results[symbol]
                    last_call_time[symbol] = time.time()
        except:
            # 解析失败，使用默认结果
            for symbol_data in symbols_to_analyze:
                results[symbol_data["symbol"]] = "hold:分析失败"
    
    return results

def main():
    """主函数：演示优化效果"""
    print("=" * 60)
    print("Token优化示例 - 基于DeepSeek建议")
    print("=" * 60)
    
    symbols = ["BTC", "ETH", "SOL", "BNB", "XRP"]
    
    print(f"\n分析币种: {', '.join(symbols)}")
    print(f"当前时间: {datetime.now().strftime('%H:%M:%S')}")
    print("-" * 60)
    
    # 第一次调用
    print("\n[第1次调用]")
    results1 = query_ai_with_optimization(symbols)
    for symbol, advice in results1.items():
        print(f"  {symbol}: {advice}")
    
    # 模拟时间流逝
    time.sleep(30)
    
    # 第二次调用（部分可能使用缓存或跳过）
    print(f"\n[第2次调用 - 30秒后]")
    results2 = query_ai_with_optimization(symbols)
    for symbol, advice in results2.items():
        print(f"  {symbol}: {advice}")
    
    # 第三次调用（冷却时间检查）
    print(f"\n[第3次调用 - 立即再次调用]")
    results3 = query_ai_with_optimization(symbols)
    for symbol, advice in results3.items():
        print(f"  {symbol}: {advice}")
    
    print("\n" + "=" * 60)
    print("优化效果总结:")
    print(f"- 总AI调用次数: {call_count}次（未优化可能需要{len(symbols)*3}=15次）")
    print(f"- 缓存命中: {len(cache)}次")
    print(f"- 调用跳过: 通过条件判断减少不必要调用")
    print(f"- Token节省: 预计减少50-90%")
    print("=" * 60)

if __name__ == "__main__":
    main()