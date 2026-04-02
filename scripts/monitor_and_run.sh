#!/bin/bash
# 持续监控并运行策略
cd /root/.openclaw/workspace

LOG_FILE="data/polymarket/runtime/monitor.log"

while true; do
    ts=$(date '+%Y-%m-%d %H:%M')
    echo "=== $ts 检查 ===" >> "$LOG_FILE"
    
    # 检查是否有recent市场
    python3 scripts/pm_paper_loop.py \
        --strategy strategies/test1_br_copy.json \
        --tag "monitor_$(date +%H%M%S)" \
        --scan-pages 10 2>&1 | grep -E "orders_generated|recent" >> "$LOG_FILE"
    
    sleep 300  # 5分钟检查一次
done
