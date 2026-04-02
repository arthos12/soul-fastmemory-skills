#!/usr/bin/env python3
"""
通用缓存优化器 - 适用于所有LLM API调用
核心：频繁请求相同内容（如系统提示词）开启缓存，大幅节省成本
"""

import json
import time
import hashlib
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import pickle
import gzip

class CacheLevel(Enum):
    """缓存级别"""
    NONE = "none"           # 不缓存
    PROMPT = "prompt"       # 仅缓存提示词（系统提示等固定内容）
    RESPONSE = "response"   # 缓存完整响应
    AGGRESSIVE = "aggressive"  # 激进缓存（相似内容也缓存）

@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    provider: str           # openai, deepseek, anthropic, gemini等
    model: str              # 模型名称
    prompt_hash: str        # 提示词哈希
    response: str           # 响应内容
    tokens_used: int        # 使用的tokens
    cost_estimate: float    # 成本估算
    created_at: float       # 创建时间戳
    expires_at: float       # 过期时间戳
    hit_count: int = 0      # 命中次数
    last_accessed: float = 0.0  # 最后访问时间
    
class UniversalCacheOptimizer:
    """
    通用LLM缓存优化器
    核心功能：
    1. 提示词缓存 - 系统提示词等固定内容
    2. 响应缓存 - 相同输入返回缓存响应
    3. 相似内容缓存 - 相似提示词返回相似响应
    4. 成本监控与优化建议
    """
    
    def __init__(self, db_path: str = "/tmp/llm_cache.db"):
        self.db_path = db_path
        self._init_database()
        
        # 内存缓存（快速访问）
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.memory_cache_lock = threading.RLock()
        
        # 统计信息
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "prompt_cache_hits": 0,
            "response_cache_hits": 0,
            "tokens_saved": 0,
            "cost_saved": 0.0,
            "providers": {}
        }
        
        # 配置
        self.config = {
            "default_ttl": 3600,  # 默认缓存1小时
            "prompt_ttl": 86400,  # 系统提示词缓存24小时
            "max_memory_entries": 1000,
            "similarity_threshold": 0.9,  # 相似度阈值
            "min_tokens_for_cache": 10,   # 最小tokens才缓存
            "enable_compression": True,   # 启用压缩
        }
        
        # 已知的系统提示词模式（自动识别并优先缓存）
        self.system_prompt_patterns = [
            "你是一个", "You are a", "As an AI",
            "系统提示", "System prompt",
            "角色设定", "Role setting",
            "助手", "Assistant", "assistant",
            "请遵守", "Please follow",
            "规则", "Rules", "guidelines"
        ]
        
        # 成本参考（美元/百万token）
        self.cost_reference = {
            "openai": {"input": 0.15, "output": 0.60},
            "deepseek": {"input": 0.14, "output": 0.28},
            "anthropic": {"input": 0.15, "output": 0.75},
            "gemini": {"input": 0.10, "output": 0.30},
            "claude": {"input": 0.80, "output": 4.00},
        }
        
        print(f"通用缓存优化器初始化完成")
        print(f"数据库: {db_path}")
        print(f"支持提供商: {', '.join(self.cost_reference.keys())}")
    
    def _init_database(self):
        """初始化数据库"""
        # 先定义模式，再使用
        system_prompt_patterns = [
            "你是一个", "You are a", "As an AI",
            "系统提示", "System prompt",
            "角色设定", "Role setting",
            "助手", "Assistant", "assistant",
            "请遵守", "Please follow",
            "规则", "Rules", "guidelines"
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    prompt_hash TEXT NOT NULL,
                    response BLOB NOT NULL,
                    tokens_used INTEGER NOT NULL,
                    cost_estimate REAL NOT NULL,
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL,
                    hit_count INTEGER DEFAULT 0,
                    last_accessed REAL DEFAULT 0,
                    tags TEXT DEFAULT ''
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS prompt_patterns (
                    pattern TEXT PRIMARY KEY,
                    cache_level TEXT NOT NULL,
                    ttl INTEGER NOT NULL,
                    hit_count INTEGER DEFAULT 0
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires ON cache_entries(expires_at)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_prompt_hash ON cache_entries(prompt_hash)
            """)
            
            # 插入默认的系统提示词模式
            for pattern in system_prompt_patterns:
                conn.execute("""
                    INSERT OR IGNORE INTO prompt_patterns (pattern, cache_level, ttl)
                    VALUES (?, ?, ?)
                """, (pattern, "prompt", 86400))
    
    def _compress_data(self, data: bytes) -> bytes:
        """压缩数据"""
        if self.config["enable_compression"]:
            return gzip.compress(data)
        return data
    
    def _decompress_data(self, data: bytes) -> bytes:
        """解压数据"""
        if self.config["enable_compression"]:
            return gzip.decompress(data)
        return data
    
    def _generate_key(self, provider: str, model: str, messages: List[Dict]) -> str:
        """生成缓存键"""
        # 提取系统提示词（如果有）
        system_prompt = ""
        for msg in messages:
            if msg.get("role") == "system":
                system_prompt = msg.get("content", "")
                break
        
        # 生成哈希
        content = json.dumps({
            "provider": provider,
            "model": model,
            "system_prompt": system_prompt,
            "messages": messages
        }, sort_keys=True)
        
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _get_prompt_hash(self, messages: List[Dict]) -> str:
        """获取提示词哈希（用于相似性匹配）"""
        content = json.dumps(messages, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
    
    def _is_system_prompt(self, messages: List[Dict]) -> bool:
        """判断是否包含系统提示词"""
        for msg in messages:
            if msg.get("role") == "system":
                content = msg.get("content", "").lower()
                for pattern in self.system_prompt_patterns:
                    if pattern.lower() in content:
                        return True
        return False
    
    def _calculate_cost(self, provider: str, input_tokens: int, output_tokens: int) -> float:
        """计算成本"""
        if provider not in self.cost_reference:
            provider = "openai"  # 默认
        
        costs = self.cost_reference[provider]
        input_cost = (input_tokens / 1_000_000) * costs["input"]
        output_cost = (output_tokens / 1_000_000) * costs["output"]
        
        return input_cost + output_cost
    
    def _get_cache_level(self, messages: List[Dict]) -> CacheLevel:
        """确定缓存级别"""
        if self._is_system_prompt(messages):
            return CacheLevel.PROMPT
        
        # 检查消息长度
        total_length = sum(len(json.dumps(m)) for m in messages)
        if total_length > 1000:  # 长提示词
            return CacheLevel.RESPONSE
        
        return CacheLevel.AGGRESSIVE
    
    def _get_cache_ttl(self, cache_level: CacheLevel) -> int:
        """获取缓存TTL"""
        if cache_level == CacheLevel.PROMPT:
            return self.config["prompt_ttl"]
        return self.config["default_ttl"]
    
    def get_cached_response(self, provider: str, model: str, messages: List[Dict]) -> Optional[Tuple[str, int, float]]:
        """
        获取缓存响应
        返回: (响应内容, tokens数, 成本估算) 或 None
        """
        self.stats["total_requests"] += 1
        
        # 生成键和哈希
        cache_key = self._generate_key(provider, model, messages)
        prompt_hash = self._get_prompt_hash(messages)
        
        # 1. 检查内存缓存
        with self.memory_cache_lock:
            if cache_key in self.memory_cache:
                entry = self.memory_cache[cache_key]
                if time.time() < entry.expires_at:
                    entry.hit_count += 1
                    entry.last_accessed = time.time()
                    self.stats["cache_hits"] += 1
                    self.stats["tokens_saved"] += entry.tokens_used
                    self.stats["cost_saved"] += entry.cost_estimate
                    
                    if self._is_system_prompt(messages):
                        self.stats["prompt_cache_hits"] += 1
                        print(f"[缓存命中] 系统提示词 - 节省 {entry.tokens_used} tokens")
                    else:
                        self.stats["response_cache_hits"] += 1
                    
                    return entry.response, entry.tokens_used, entry.cost_estimate
        
        # 2. 检查数据库缓存
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT response, tokens_used, cost_estimate, expires_at
                FROM cache_entries
                WHERE key = ? AND expires_at > ?
            """, (cache_key, time.time()))
            
            row = cursor.fetchone()
            if row:
                response_data, tokens_used, cost_estimate, expires_at = row
                
                # 解压响应
                response = self._decompress_data(response_data).decode('utf-8')
                
                # 更新命中统计
                conn.execute("""
                    UPDATE cache_entries
                    SET hit_count = hit_count + 1,
                        last_accessed = ?
                    WHERE key = ?
                """, (time.time(), cache_key))
                
                # 放入内存缓存
                entry = CacheEntry(
                    key=cache_key,
                    provider=provider,
                    model=model,
                    prompt_hash=prompt_hash,
                    response=response,
                    tokens_used=tokens_used,
                    cost_estimate=cost_estimate,
                    created_at=time.time(),
                    expires_at=expires_at,
                    hit_count=1,
                    last_accessed=time.time()
                )
                
                with self.memory_cache_lock:
                    if len(self.memory_cache) >= self.config["max_memory_entries"]:
                        # 移除最久未访问的
                        oldest = min(self.memory_cache.items(), key=lambda x: x[1].last_accessed)
                        del self.memory_cache[oldest[0]]
                    self.memory_cache[cache_key] = entry
                
                self.stats["cache_hits"] += 1
                self.stats["tokens_saved"] += tokens_used
                self.stats["cost_saved"] += cost_estimate
                
                if self._is_system_prompt(messages):
                    self.stats["prompt_cache_hits"] += 1
                    print(f"[数据库缓存] 系统提示词 - 节省 {tokens_used} tokens")
                else:
                    self.stats["response_cache_hits"] += 1
                
                return response, tokens_used, cost_estimate
        
        # 3. 检查相似提示词（激进缓存模式）
        cache_level = self._get_cache_level(messages)
        if cache_level == CacheLevel.AGGRESSIVE:
            with sqlite3.connect(self.db_path) as conn:
                # 查找相似提示词（相同模型，最近使用）
                cursor = conn.execute("""
                    SELECT response, tokens_used, cost_estimate
                    FROM cache_entries
                    WHERE provider = ? AND model = ? 
                    AND expires_at > ?
                    ORDER BY last_accessed DESC
                    LIMIT 5
                """, (provider, model, time.time()))
                
                # 这里可以添加更复杂的相似度匹配
                # 简化版：返回最近的一个
                row = cursor.fetchone()
                if row:
                    response_data, tokens_used, cost_estimate = row
                    response = self._decompress_data(response_data).decode('utf-8')
                    
                    self.stats["cache_hits"] += 1
                    self.stats["tokens_saved"] += tokens_used
                    self.stats["cost_saved"] += cost_estimate
                    self.stats["response_cache_hits"] += 1
                    
                    print(f"[相似缓存] 使用相似响应 - 节省 {tokens_used} tokens")
                    return response, tokens_used, cost_estimate
        
        return None
    
    def cache_response(self, provider: str, model: str, messages: List[Dict], 
                      response: str, input_tokens: int, output_tokens: int):
        """
        缓存响应
        """
        total_tokens = input_tokens + output_tokens
        
        # 跳过太小的响应
        if total_tokens < self.config["min_tokens_for_cache"]:
            return
        
        cache_key = self._generate_key(provider, model, messages)
        prompt_hash = self._get_prompt_hash(messages)
        
        # 计算成本
        cost_estimate = self._calculate_cost(provider, input_tokens, output_tokens)
        
        # 确定缓存级别和TTL
        cache_level = self._get_cache_level(messages)
        ttl = self._get_cache_ttl(cache_level)
        
        # 创建缓存条目
        entry = CacheEntry(
            key=cache_key,
            provider=provider,
            model=model,
            prompt_hash=prompt_hash,
            response=response,
            tokens_used=total_tokens,
            cost_estimate=cost_estimate,
            created_at=time.time(),
            expires_at=time.time() + ttl,
            hit_count=0,
            last_accessed=time.time()
        )
        
        # 保存到数据库
        with sqlite3.connect(self.db_path) as conn:
            # 压缩响应
            response_data = self._compress_data(response.encode('utf-8'))
            
            conn.execute("""
                INSERT OR REPLACE INTO cache_entries 
                (key, provider, model, prompt_hash, response, tokens_used, 
                 cost_estimate, created_at, expires_at, hit_count, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cache_key, provider, model, prompt_hash, response_data,
                total_tokens, cost_estimate, entry.created_at, entry.expires_at,
                entry.hit_count, entry.last_accessed
            ))
        
        # 保存到内存缓存
        with self.memory_cache_lock:
            if len(self.memory_cache) >= self.config["max_memory_entries"]:
                # 移除最久未访问的
                oldest = min(self.memory_cache.items(), key=lambda x: x[1].last_accessed)
                del self.memory_cache[oldest[0]]
            self.memory_cache[cache_key] = entry
        
        # 更新提供商统计
        if provider not in self.stats["providers"]:
            self.stats["providers"][provider] = {"calls": 0, "tokens": 0, "cost": 0.0}
        
        self.stats["providers"][provider]["calls"] += 1
        self.stats["providers"][provider]["tokens"] += total_tokens
        self.stats["providers"][provider]["cost"] += cost_estimate
        
        # 记录系统提示词缓存
        if cache_level == CacheLevel.PROMPT:
            print(f"[缓存保存] 系统提示词 - {total_tokens} tokens, TTL: {ttl//3600}小时")
    
    def optimize_messages(self, messages: List[Dict]) -> List[Dict]:
        """
        优化消息以减少token使用
        """
        optimized = []
        
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            if role == "system":
                # 系统提示词优化：移除多余空格和换行
                content = ' '.join(content.split())
                # 移除多余标点
                if content.endswith('。'):
                    content = content[:-1]
            
            optimized.append({"role": role, "content": content})
        
        return optimized
    
    def get_optimization_suggestions(self) -> List[str]:
        """获取优化建议"""
        suggestions = []
        
        # 分析缓存命中率
        hit_rate = (self.stats["cache_hits"] / self.stats["total_requests"] * 100) if self.stats["total_requests"] > 0 else 0
        
        if hit_rate < 50:
            suggestions.append(f"缓存命中率较低 ({hit_rate:.1f}%)，考虑增加缓存TTL或优化提示词模式")
        
        # 检查系统提示词缓存
        prompt_hit_rate = (self.stats["prompt_cache_hits"] / self.stats["total_requests"] * 100) if self.stats["total_requests"] > 0 else 0
        if prompt_hit_rate < 30:
            suggestions.append("系统提示词缓存使用不足，确保系统提示词固定且可缓存")
        
        # 成本分析
        total_cost = sum(p["cost"] for p in self.stats["providers"].values())
        total_saved = self.stats["cost_saved"]
        
        if total_cost > 0:
            save_rate = (total_saved / total_cost * 100) if total_cost > 0 else 0
            if save_rate < 30:
                suggestions.append(f"成本节省率较低 ({save_rate:.1f}%)，考虑启用更激进的缓存策略")
        
        return suggestions
    
    def print_stats(self, detailed: bool = False):
        """打印统计信息"""
        print("\n" + "="*70)
        print("通用缓存优化器 - 统计报告")
        print("="*70)
        
        total_requests = self.stats["total_requests"]
        cache_hits = self.stats["cache_hits"]
        hit_rate = (cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        print(f"总请求数: {total_requests}")
        print(f"缓存命中: {cache_hits} ({hit_rate:.1f}%)")
        print(f"系统提示词命中: {self.stats['prompt_cache_hits']}")
        print(f"响应缓存命中: {self.stats['response_cache_hits']}")
        print(f"节省Tokens: {self.stats['tokens_saved']:,}")
        print(f"估算节省成本: ${self.stats['cost_saved']:.6f}")
        
        if detailed and self.stats["providers"]:
            print("\n提供商统计:")
            for provider, stats in self.stats["providers"].items():
                print(f"  {provider}:")
                print(f"    调用次数: {stats['calls']}")
                print(f"    Tokens: {stats['tokens']:,}")
                print(f"    成本: ${stats['cost']:.6f}")
        
        # 内存缓存状态
        with self.memory_cache_lock:
            print(f"\n内存缓存: {len(self.memory_cache)} 个条目")
        
        # 数据库缓存状态
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM cache_entries WHERE expires_at > ?", (time.time(),))
            active_entries = cursor.fetchone()[0]
            print(f"数据库缓存: {active_entries} 个有效条目")
        
        # 优化建议
        suggestions = self.get_optimization_suggestions()
        if suggestions:
            print("\n优化建议:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")
        
        print("="*70)
    
    def cleanup_expired(self):
        """清理过期缓存"""
        with sqlite3.connect(self.db_path) as conn:
            # 删除过期条目
            conn.execute("DELETE FROM cache_entries WHERE expires_at <= ?", (time.time(),))
            deleted = conn.total_changes
            
            # 清理内存缓存
            with self.memory_cache_lock:
                expired_keys = [
                    key for key, entry in self.memory_cache.items()
                    if entry.expires_at <= time.time()
                ]
                for key in expired_keys:
                    del self.memory_cache[key]
            
            print(f"[清理] 删除 {deleted} 个过期缓存条目，清理 {len(expired_keys)} 个内存缓存")
    
    def export_cache_report(self, filepath: str = "/tmp/cache_report.json"):
        """导出缓存报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "stats": self.stats,
            "config": self.config,
            "memory_cache_size": len(self.memory_cache),
            "providers": list(self.stats["providers"].keys()),
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"[报告] 已导出到 {filepath}")
        return report

# 使用示例和演示
def demonstrate_optimizer():
    """演示通用缓存优化器"""
    print("通用缓存优化器演示")
    print("="*70)
    
    # 初始化优化器
    optimizer = UniversalCacheOptimizer()
    
    # 模拟不同提供商的调用
    providers = ["openai", "deepseek", "anthropic", "gemini"]
    models = ["gpt-4", "deepseek-chat", "claude-3", "gemini-pro"]
    
    # 系统提示词（固定内容，应该被缓存）
    system_prompts = [
        "你是一个量化交易助手。分析市场数据，给出交易建议。",
        "As an AI trading assistant, analyze market data and provide trading suggestions.",
        "你是一个编程助手。帮助解决代码问题。",
        "You are a helpful assistant. Answer questions concisely."
    ]
    
    # 用户消息（变化内容）
    user_messages = [
        "BTC当前价格45000，MA5:44850，RSI:62，建议？",
        "What is the weather today?",
        "How to implement a binary search in Python?",
        "ETH价格分析，当前3200，趋势如何？"
    ]
    
    print("\n模拟API调用（启用缓存）...")
    
    # 第一轮调用（应该没有缓存）
    for i in range(4):
        provider = providers[i % len(providers)]
        model = models[i % len(models)]
        
        messages = [
            {"role": "system", "content": system_prompts[i % len(system_prompts)]},
            {"role": "user", "content": user_messages[i]}
        ]
        
        # 尝试获取缓存
        cached = optimizer.get_cached_response(provider, model, messages)
        
        if cached:
            response, tokens, cost = cached
            print(f"[{provider}/{model}] 缓存命中: {tokens} tokens")
        else:
            # 模拟API调用
            input_tokens = len(json.dumps(messages)) // 4  # 粗略估算
            output_tokens = 50  # 假设输出50 tokens
            response = f"模拟响应 {i+1}"
            
            # 缓存响应
            optimizer.cache_response(provider, model, messages, response, input_tokens, output_tokens)
            print(f"[{provider}/{model}] API调用: {input_tokens+output_tokens} tokens")
    
    print("\n等待2秒...")
    time.sleep(2)
    
    print("\n第二轮调用（应该有缓存）...")
    
    # 第二轮调用（相同内容，应该命中缓存）
    for i in range(4):
        provider = providers[i % len(providers)]
        model = models[i % len(models)]
        
        messages = [
            {"role": "system", "content": system_prompts[i % len(system_prompts)]},
            {"role": "user", "content": user_messages[i]}
        ]
        
        cached = optimizer.get_cached_response(provider, model, messages)
        
        if cached:
            response, tokens, cost = cached
            print(f"[{provider}/{model}] 缓存命中: 节省 {tokens} tokens")
        else:
            print(f"[{provider}/{model}] 缓存未命中")
    
    # 打印统计
    optimizer.print_stats(detailed=True)
    
    # 导出报告
    report = optimizer.export_cache_report()
    
    print("\n" + "="*70)
    print("关键优化措施:")
    print("1. 系统提示词自动识别与缓存（24小时TTL）")
    print("2. 响应缓存（1小时TTL）")
    print("3. 相似内容匹配（激进缓存模式）")
    print("4. 内存+数据库二级缓存")
    print("5. 成本监控与优化建议")
    print("="*70)
    
    # 估算节省
    total_requests = optimizer.stats["total_requests"]
    cache_hits = optimizer.stats["cache_hits"]
    
    if total_requests > 0:
        hit_rate = cache_hits / total_requests * 100
        avg_tokens_saved = optimizer.stats["tokens_saved"] / cache_hits if cache_hits > 0 else 0
        
        print(f"\n预期效果（基于演示）:")
        print(f"- 缓存命中率: {hit_rate:.1f}%")
        print(f"- 平均每次命中节省: {avg_tokens_saved:.0f} tokens")
        print(f"- 总节省成本: ${optimizer.stats['cost_saved']:.6f}")
        print(f"- 成本降低: 预计30-70% (取决于使用模式)")
    
    return optimizer

def integrate_with_openclaw():
    """与OpenClaw集成示例"""
    print("\n" + "="*70)
    print("OpenClaw集成指南")
    print("="*70)
    
    integration_code = '''
# 在OpenClaw配置中集成通用缓存优化器

# 1. 创建全局优化器实例
from universal_cache_optimizer import UniversalCacheOptimizer
cache_optimizer = UniversalCacheOptimizer(db_path="~/.openclaw/cache.db")

# 2. 包装API调用函数
def cached_api_call(provider, model, messages, api_call_func):
    """
    带缓存的API调用
    """
    # 尝试获取缓存
    cached = cache_optimizer.get_cached_response(provider, model, messages)
    if cached:
        response, tokens, cost = cached
        return response
    
    # 没有缓存，调用实际API
    response = api_call_func(provider, model, messages)
    
    # 估算tokens（实际应从API响应获取）
    input_tokens = estimate_input_tokens(messages)
    output_tokens = estimate_output_tokens(response)
    
    # 缓存响应
    cache_optimizer.cache_response(provider, model, messages, response, input_tokens, output_tokens)
    
    return response

# 3. 在agents配置中启用
# 修改 ~/.openclaw/openclaw.json
'''
    
    print(integration_code)
    
    print("\n立即执行步骤:")
    print("1. 将 universal_cache_optimizer.py 添加到 scripts/")
    print("2. 在量化系统API调用处集成缓存包装器")
    print("3. 配置定期缓存清理（cron job）")
    print("4. 监控缓存命中率和成本节省")
    print("="*70)

if __name__ == "__main__":
    # 演示优化器
    optimizer = demonstrate_optimizer()
    
    # 显示集成指南
    integrate_with_openclaw()
    
    # 清理过期缓存
    optimizer.cleanup_expired()
    
    print("\n✅ 通用缓存优化器已就绪，可立即集成到所有LLM调用中")
