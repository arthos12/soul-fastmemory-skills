#!/bin/bash
# session_startup.sh - 每次session启动时自动运行
# 在new session或session切换时自动触发

bash /root/.openclaw/workspace/scripts/capability_check.sh

# 如果有缺口，输出恢复建议
if [ $? -ne 0 ]; then
    echo "⚠️ 能力有缺口，从SESSION_HANDOFF.md恢复"
fi
