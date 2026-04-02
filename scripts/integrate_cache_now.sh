#!/bin/bash
# 立即集成通用缓存优化器

echo "🚀 通用缓存优化器 - 立即集成执行"
echo "=========================================="

# 1. 检查必要文件
echo "📁 检查文件..."
if [ -f "scripts/universal_cache_optimizer.py" ]; then
    echo "✅ universal_cache_optimizer.py 存在"
else
    echo "❌ universal_cache_optimizer.py 不存在"
    exit 1
fi

# 2. 创建集成包装器
echo "🔧 创建API调用包装器..."
cat > scripts/cached_api_wrapper.py << 'EOF'
#!/usr/bin/env python3
"""
OpenClaw API调用缓存包装器
立即集成通用缓存优化，无需修改现有代码
"""

import json
import time
from typing import Dict, List, Optional, Any
from universal_cache_optimizer import UniversalCacheOptimizer

# 全局缓存优化器实例
_cache_optimizer = None

def get_cache_optimizer():
    """获取缓存优化器实例（单例）"""
    global _cache_optimizer
    if _cache_optimizer is None:
        _cache_optimizer = UniversalCacheOptimizer(db_path="/root/.openclaw/cache.db")
        print("[缓存优化器] 初始化完成")
    return _cache_optimizer

def estimate_tokens(text: str) -> int:
    """估算tokens数量（粗略）"""
    # 英文：1 token ≈ 4字符，中文：1 token ≈ 2字符
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    other_chars = len(text) - chinese_chars
    return chinese_chars // 2 + other_chars // 4

def cached_chat_completion(provider: str, model: str, messages: List[Dict], 
                          api_call_func, **kwargs) -> Optional[Dict]:
    """
    带缓存的聊天补全调用
    
    参数:
        provider: 提供商 (openai, deepseek, anthropic, gemini)
        model: 模型名称
        messages: 消息列表
        api_call_func: 实际的API调用函数
        **kwargs: 其他API参数
        
    返回:
        API响应字典 或 None
    """
    optimizer = get_cache_optimizer()
    
    # 1. 尝试获取缓存响应
    cached = optimizer.get_cached_response(provider, model, messages)
    if cached:
        response_text, tokens_used, cost_saved = cached
        print(f"[缓存命中] {provider}/{model} - 节省 {tokens_used} tokens")
        
        # 构造标准API响应格式
        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 0,  # 缓存命中，输入tokens为0
                "completion_tokens": tokens_used,
                "total_tokens": tokens_used
            },
            "model": model,
            "cached": True
        }
    
    # 2. 没有缓存，调用实际API
    print(f"[API调用] {provider}/{model}")
    try:
        response = api_call_func(messages=messages, model=model, **kwargs)
        
        # 3. 提取响应内容
        if provider == "openai" or provider == "deepseek":
            response_text = response.choices[0].message.content
            usage = response.usage
            input_tokens = usage.prompt_tokens
            output_tokens = usage.completion_tokens
        elif provider == "anthropic":
            response_text = response.content[0].text
            usage = response.usage
            input_tokens = usage.input_tokens
            output_tokens = usage.output_tokens
        elif provider == "gemini":
            response_text = response.text
            # Gemini不直接提供tokens，需要估算
            input_tokens = estimate_tokens(json.dumps(messages))
            output_tokens = estimate_tokens(response_text)
        else:
            # 默认处理
            response_text = str(response)
            input_tokens = estimate_tokens(json.dumps(messages))
            output_tokens = estimate_tokens(response_text)
        
        # 4. 缓存响应
        optimizer.cache_response(provider, model, messages, response_text, 
                                input_tokens, output_tokens)
        
        # 5. 返回响应
        if not isinstance(response, dict):
            # 转换为字典格式
            return {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": input_tokens,
                    "completion_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens
                },
                "model": model,
                "cached": False
            }
        
        return response
        
    except Exception as e:
        print(f"[API错误] {provider}/{model}: {e}")
        return None

def optimize_system_prompt(prompt: str) -> str:
    """优化系统提示词以减少token使用"""
    # 移除多余空格和换行
    prompt = ' '.join(prompt.split())
    
    # 简化常见模式
    replacements = {
        "你是一个量化交易助手。": "量化助手。",
        "你是一个编程助手。": "编程助手。",
        "你是一个AI助手。": "AI助手。",
        "请仔细分析并给出详细回答。": "分析并回答。",
        "请严格遵守以下规则：": "规则：",
        "请用中文回答。": "中文回答。",
    }
    
    for old, new in replacements.items():
        prompt = prompt.replace(old, new)
    
    return prompt

def batch_optimize_messages(messages: List[Dict]) -> List[Dict]:
    """批量优化消息"""
    optimizer = get_cache_optimizer()
    return optimizer.optimize_messages(messages)

def get_cache_stats() -> Dict:
    """获取缓存统计"""
    optimizer = get_cache_optimizer()
    optimizer.print_stats(detailed=True)
    
    # 导出报告
    report = optimizer.export_cache_report("/tmp/cache_report.json")
    return report

def cleanup_cache():
    """清理过期缓存"""
    optimizer = get_cache_optimizer()
    optimizer.cleanup_expired()

# 使用示例
if __name__ == "__main__":
    print("缓存包装器测试...")
    
    # 模拟API调用函数
    def mock_api_call(messages, model, **kwargs):
        print(f"模拟调用: {model}")
        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "这是模拟响应"
                }
            }]
        }
    
    # 测试调用
    messages = [
        {"role": "system", "content": "你是一个量化交易助手。"},
        {"role": "user", "content": "BTC价格分析"}
    ]
    
    result = cached_chat_completion(
        provider="openai",
        model="gpt-4",
        messages=messages,
        api_call_func=mock_api_call
    )
    
    print(f"结果: {result}")
EOF

echo "✅ 创建 cached_api_wrapper.py 完成"

# 3. 创建OpenClaw配置修改
echo "⚙️ 创建OpenClaw配置修改指南..."
cat > docs/openclaw_cache_integration.md << 'EOF'
# OpenClaw缓存集成指南

## 目标
将通用缓存优化器集成到OpenClaw中，减少所有LLM调用的成本。

## 集成方式

### 方式一：包装现有调用（推荐）
修改现有API调用代码，使用缓存包装器：

```python
# 原代码
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=messages
)

# 新代码
from cached_api_wrapper import cached_chat_completion

response = cached_chat_completion(
    provider="openai",
    model="gpt-4",
    messages=messages,
    api_call_func=openai.ChatCompletion.create
)
```

### 方式二：修改OpenClaw配置
修改 `~/.openclaw/openclaw.json`：

```json
{
  "agents": {
    "defaults": {
      "cache": {
        "enabled": true,
        "db_path": "/root/.openclaw/cache.db",
        "default_ttl": 3600,
        "prompt_ttl": 86400
      }
    }
  }
}
```

### 方式三：中间件模式
创建OpenClaw中间件：

```python
# ~/.openclaw/workspace/middleware/cache_middleware.py
from openclaw.types import Message, Response
from cached_api_wrapper import cached_chat_completion

async def cache_middleware(message: Message, next_fn) -> Response:
    # 检查是否应该缓存
    if should_cache(message):
        # 使用缓存调用
        response = cached_chat_completion(...)
        return response
    
    # 正常流程
    return await next_fn(message)
```

## 立即执行步骤

### 1. 测试集成
```bash
# 测试缓存包装器
python3 scripts/cached_api_wrapper.py

# 测试通用优化器
python3 scripts/universal_cache_optimizer.py
```

### 2. 修改量化脚本
查找所有使用LLM API的脚本，添加缓存：

```bash
# 查找所有Python脚本中的API调用
grep -r "openai\|deepseek\|anthropic\|gemini" scripts/ --include="*.py"

# 逐个修改，添加缓存包装
```

### 3. 部署监控
```bash
# 创建监控脚本
cat > scripts/monitor_cache.py << 'MONITOR'
#!/usr/bin/env python3
from cached_api_wrapper import get_cache_stats

# 每小时运行一次
stats = get_cache_stats()
print(f"缓存统计: {stats}")
MONITOR

# 添加到cron
echo "0 * * * * cd /root/.openclaw/workspace && python3 scripts/monitor_cache.py" >> /tmp/cron_cache
```

### 4. 验证效果
1. 运行量化系统一段时间
2. 检查缓存命中率
3. 对比成本变化
4. 调整缓存策略

## 预期效果

### 成本节省
| 使用模式 | 预期节省 |
|----------|----------|
| 高频相同查询 | 90-100% |
| 系统提示词 | 90%+ |
| 相似查询 | 50-80% |
| 总体 | 30-70% |

### 性能影响
- **首次调用**: 略有延迟（需要计算和缓存）
- **后续调用**: 显著加速（内存缓存）
- **存储需求**: 每百万tokens约10-50MB

## 故障排除

### 常见问题
1. **缓存不生效**
   - 检查数据库权限
   - 检查消息哈希计算
   - 检查TTL设置

2. **内存使用过高**
   - 调整 `max_memory_entries`
   - 启用压缩
   - 定期清理

3. **响应过时**
   - 调整TTL
   - 关键数据绕过缓存
   - 添加版本标识

### 监控指标
1. 缓存命中率 (>50% 目标)
2. Tokens节省量
3. 成本节省估算
4. 平均响应时间

## 高级配置

### 动态TTL
根据内容类型设置不同TTL：
- 系统提示词: 24小时
- 价格数据: 5分钟
- 技术分析: 1小时
- 新闻事件: 15分钟

### 条件缓存
```python
def should_cache(messages):
    # 不缓存敏感信息
    if contains_sensitive_info(messages):
        return False
    
    # 不缓存实时数据
    if is_realtime_data(messages):
        return False
    
    # 缓存其他内容
    return True
```

### 分布式缓存
对于多实例部署：
```python
# 使用Redis作为共享缓存
optimizer = UniversalCacheOptimizer(
    db_path="redis://localhost:6379/0"
)
```

## 支持与维护

### 定期维护
1. 每日检查缓存命中率
2. 每周清理过期缓存
3. 每月优化缓存策略

### 更新日志
- 2026-03-20: 创建通用缓存优化器
- 2026-03-20: 创建OpenClaw集成指南

## 参考资料
1. [通用缓存优化器代码](scripts/universal_cache_optimizer.py)
2. [API缓存包装器](scripts/cached_api_wrapper.py)
3. [缓存统计报告](/tmp/cache_report.json)
EOF

echo "✅ 创建 openclaw_cache_integration.md 完成"

# 4. 创建立即执行脚本
echo "🎯 创建立即执行脚本..."
cat > scripts/execute_cache_integration.py << 'EOF'
#!/usr/bin/env python3
"""
立即执行缓存集成
自动修改现有脚本，添加缓存支持
"""

import os
import re
import sys
from pathlib import Path

def find_api_calls(directory="scripts"):
    """查找所有API调用"""
    api_patterns = [
        (r"openai\.ChatCompletion\.create", "openai"),
        (r"deepseek\.ChatCompletion\.create", "deepseek"),
        (r"anthropic\.messages\.create", "anthropic"),
        (r"gemini\.generate_content", "gemini"),
        (r"requests\.post.*api\.deepseek\.com", "deepseek"),
        (r"requests\.post.*api\.openai\.com", "openai"),
    ]
    
    results = []
    
    for filepath in Path(directory).rglob("*.py"):
        try:
            content = filepath.read_text()
            for pattern, provider in api_patterns:
                if re.search(pattern, content):
                    results.append({
                        "file": str(filepath),
                        "provider": provider,
                        "pattern": pattern
                    })
                    break  # 每个文件只记录一次
        except:
            continue
    
    return results

def generate_wrapper_code(provider, model_var="model", messages_var="messages"):
    """生成包装器代码"""
    wrapper_templates = {
        "openai": f'''
# 缓存优化版本
from cached_api_wrapper import cached_chat_completion

response = cached_chat_completion(
    provider="openai",
    model={model_var},
    messages={messages_var},
    api_call_func=openai.ChatCompletion.create
)
''',
        "deepseek": f'''
# 缓存优化版本
from cached_api_wrapper import cached_chat_completion

response = cached_chat_completion(
    provider="deepseek",
    model={model_var},
    messages={messages_var},
    api_call_func=deepseek.ChatCompletion.create
)
''',
        "default": f'''
# 缓存优化版本
from cached_api_wrapper import cached_chat_completion

# 需要根据实际API调用调整
response = cached_chat_completion(
    provider="{provider}",
    model={model_var},
    messages={messages_var},
    api_call_func=actual_api_function  # 替换为实际函数
)
'''
    }
    
    return wrapper_templates.get(provider, wrapper_templates["default"])

def main():
    print("立即执行缓存集成")
    print("="*60)
    
    # 1. 查找API调用
    print("🔍 查找API调用...")
    api_calls = find_api_calls()
    
    if not api_calls:
        print("未找到API调用")
        return
    
    print(f"找到 {len(api_calls)} 个API调用:")
    for call in api_calls:
        print(f"  - {call['file']} ({call['provider']})")
    
    # 2. 创建修改计划
    print("\n📝 创建修改计划...")
    modifications = []
    
    for call in api_calls:
        filepath = call["file"]
        
        # 读取文件内容
        with open(filepath, 'r') as f:
            content = f.read()
        
        # 查找导入语句位置
        import_match = re.search(r'^(import|from)', content, re.MULTILINE)
        import_pos = import_match.end() if import_match else 0
        
        # 生成新内容
        new_content = content[:import_pos] + \
                     '\n# 缓存优化导入\nfrom cached_api_wrapper import cached_chat_completion\n' + \
                     content[import_pos:]
        
        # 添加注释标记需要修改的API调用
        modified_content = new_content.replace(
            call["pattern"],
            f"# TODO: 替换为缓存版本\n# {call['pattern']}"
        )
        
        modifications.append({
            "file": filepath,
            "original": content,
            "modified": modified_content,
            "backup": f"{filepath}.backup"
        })
    
    # 3. 执行修改
    print("\n⚡ 执行修改...")
    for mod in modifications:
        print(f"处理: {mod['file']}")
        
        # 创建备份
        with open(mod["backup"], 'w') as f:
            f.write(mod["original"])
        print(f"  备份: {mod['backup']}")
        
        # 写入修改
        with open(mod["file"], 'w') as f:
            f.write(mod["modified"])
        print(f"  修改: 添加缓存导入和TODO标记")
    
    # 4. 生成修改指南
    print("\n📋 修改指南:")
    print("="*60)
    for mod in modifications:
        print(f"\n文件: {mod['file']}")
        print("需要手动修改的API调用:")
        
        # 提取TODO行
        for line in mod["modified"].split('\n'):
            if "TODO: 替换为缓存版本" in line:
                print(f"