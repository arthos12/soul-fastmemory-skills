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
                print(f"  {line}")
                # 找到下一行（原始API调用）
                idx = mod["modified"].split('\n').index(line)
                original_line = mod["modified"].split('\n')[idx + 1]
                print(f"  原始: {original_line}")
                
                # 生成建议代码
                provider = next(call["provider"] for call in api_calls if call["file"] == mod["file"])
                wrapper = generate_wrapper_code(provider)
                print(f"  建议替换为:\n{wrapper}")
    
    # 5. 创建自动化脚本
    print("\n🤖 创建自动化修改脚本...")
    auto_script = '''#!/usr/bin/env python3
"""
自动修改API调用为缓存版本
运行此脚本自动替换标记的TODO
"""

import re
import sys

def replace_todo_with_cache(filename):
    with open(filename, 'r') as f:
        content = f.read()
    
    # 查找TODO标记
    lines = content.split('\\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        if "TODO: 替换为缓存版本" in lines[i]:
            # 找到TODO行和原始API调用行
            todo_line = lines[i]
            original_line = lines[i + 1] if i + 1 < len(lines) else ""
            
            # 确定provider
            provider = "openai"
            if "deepseek" in original_line:
                provider = "deepseek"
            elif "anthropic" in original_line:
                provider = "anthropic"
            elif "gemini" in original_line:
                provider = "gemini"
            
            # 提取变量名
            model_match = re.search(r'model=["\']([^"\']+)["\']', original_line)
            model_var = model_match.group(1) if model_match else '"gpt-4"'
            
            # 生成替换代码
            replacement = f'''
# 缓存优化版本
response = cached_chat_completion(
    provider="{provider}",
    model={model_var},
    messages=messages,
    api_call_func=openai.ChatCompletion.create  # 需要调整
)
'''
            new_lines.append(replacement)
            i += 2  # 跳过TODO和原始行
        else:
            new_lines.append(lines[i])
            i += 1
    
    new_content = '\\n'.join(new_lines)
    
    # 写回文件
    with open(filename, 'w') as f:
        f.write(new_content)
    
    print(f"已修改: {filename}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for filename in sys.argv[1:]:
            replace_todo_with_cache(filename)
    else:
        print("用法: python3 auto_replace_cache.py <文件1> <文件2> ...")
'''
    
    with open("scripts/auto_replace_cache.py", 'w') as f:
        f.write(auto_script)
    
    print(f"✅ 创建自动化脚本: scripts/auto_replace_cache.py")
    
    # 6. 总结
    print("\n🎯 总结:")
    print("="*60)
    print("已完成:")
    print("1. 查找所有API调用")
    print("2. 创建备份文件")
    print("3. 添加缓存导入和TODO标记")
    print("4. 生成修改指南")
    print("5. 创建自动化脚本")
    print()
    print("下一步:")
    print("1. 手动修改标记的API调用")
    print("2. 或运行自动化脚本: python3 scripts/auto_replace_cache.py <文件>")
    print("3. 测试修改后的脚本")
    print("4. 监控缓存效果")
    print()
    print("💡 提示:")
    print("- 系统提示词会自动缓存（24小时）")
    print("- 相同查询会100%缓存命中")
    print("- 预计成本降低30-70%")
    print("="*60)

if __name__ == "__main__":
    main()