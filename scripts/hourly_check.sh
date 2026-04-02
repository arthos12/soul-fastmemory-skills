#!/bin/bash
cd /root/.openclaw/workspace
echo "$(date '+%Y-%m-%d %H:%M') - 开始分析" >> /tmp/hourly.log
python3 scripts/daily_analyzer.py >> /tmp/hourly.log 2>&1
echo "$(date '+%Y-%m-%d %H:%M') - 完成" >> /tmp/hourly.log
