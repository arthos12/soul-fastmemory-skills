#!/usr/bin/env python3
"""Runner保活机制"""
import subprocess, time, json
from pathlib import Path
from datetime import datetime

STATE_FILE = Path("data/polymarket/runtime/runner_state.json")
MAX_RETRIES = 3
COOLDOWN = 300  # 5分钟

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"retry": 0, "last": None, "paused": False}

def save_state(s):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(s))

def is_running():
    r = subprocess.run("ps aux | grep pm_auto | grep -v grep", 
                     shell=True, capture_output=True)
    return bool(r.stdout)

def start_runner():
    subprocess.run("pkill -f pm_auto_runner", shell=True)
    time.sleep(1)
    subprocess.Popen(
        "bash scripts/pm_auto_runner.sh strategies/br_v4_5min_low.json 300 >> /tmp/runner.log 2>&1",
        shell=True
    )
    print(f"  → 已启动Runner")

def main():
    state = load_state()
    
    print(f"\n[{datetime.now().strftime('%H:%M')}] Runner保活")
    
    if state.get("paused"):
        print("  已暂停保活")
        return
    
    if is_running():
        print("  ✅ 运行正常")
        state["retry"] = 0
        save_state(state)
        return
    
    # 未运行
    print("  ⚠️ 未运行")
    
    if state.get("last"):
        last = datetime.fromisoformat(state["last"])
        if (datetime.now() - last).seconds < COOLDOWN:
            print("  冷却中...")
            return
    
    # 重试
    if state["retry"] < MAX_RETRIES:
        start_runner()
        state["retry"] += 1
        state["last"] = datetime.now().isoformat()
        print(f"  重试 {state['retry']}/{MAX_RETRIES}")
    else:
        print(f"  连续{MAX_RETRIES}次失败，暂停")
        state["paused"] = True
        save_state(state)