#!/bin/bash
# capability_check.sh - Bot能力完整性自动检查
# 每次session开始时自动运行

echo "=== Bot能力完整性检查 ==="
echo ""

PASS=0
FAIL=0

check_file() {
    if [ -f "$1" ]; then
        echo "✅ $1"
        PASS=$((PASS+1))
    else
        echo "❌ $1 - 缺失"
        FAIL=$((FAIL+1))
    fi
}

check_rule() {
    if grep -q "$2" "$1" 2>/dev/null; then
        echo "✅ $3"
        PASS=$((PASS+1))
    else
        echo "❌ $3 - 未找到"
        FAIL=$((FAIL+1))
    fi
}

echo "--- 核心文件检查 ---"
check_file "/root/.openclaw/workspace/AGENTS.md"
check_file "/root/.openclaw/workspace/MEMORY.md"
check_file "/root/.openclaw/workspace/ability_card_core.md"
check_file "/root/.openclaw/workspace/SESSION_HANDOFF.md"
check_file "/root/.openclaw/workspace/memory/sell_discipline.md"
check_file "/root/.openclaw/workspace/memory/investment_principles_munger_dalio.md"
check_file "/root/.openclaw/workspace/memory/cognitive_framework_munger_musk.md"
check_file "/root/.openclaw/workspace/skills/soul-booster/references/brain_safety.md"

echo ""
echo "--- 关键规则检查 ---"
check_rule "/root/.openclaw/workspace/AGENTS.md" "四件套" "逻辑四件套（AGENTS.md）"
check_rule "/root/.openclaw/workspace/AGENTS.md" "自主执行原则" "自主执行原则（AGENTS.md）"
check_rule "/root/.openclaw/workspace/AGENTS.md" "U→L→P" "U→L→P链路（AGENTS.md）"
check_rule "/root/.openclaw/workspace/ability_card_core.md" "溯因" "溯因推理能力卡"
check_rule "/root/.openclaw/workspace/ability_card_core.md" "逆向" "逆向推理能力卡"
check_rule "/root/.openclaw/workspace/ability_card_core.md" "演绎" "演绎推理能力卡"
check_rule "/root/.openclaw/workspace/ability_card_core.md" "系统论" "系统论能力卡"
check_rule "/root/.openclaw/workspace/ability_card_core.md" "DeepSeek" "DeepSeek清单化"
check_rule "/root/.openclaw/workspace/ability_card_core.md" "Claude精准" "Claude精准化"
check_rule "/root/.openclaw/workspace/ability_card_core.md" "自主执行" "自主执行规则"
check_rule "/root/.openclaw/workspace/skills/soul-booster/references/brain_safety.md" "能力断层" "能力断层检查"

echo ""
echo "=== 检查结果 ==="
echo "通过: $PASS"
echo "失败: $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "✅ 所有能力完整"
    exit 0
else
    echo "⚠️ 有 $FAIL 项缺失，请从 SESSION_HANDOFF.md 恢复"
    exit 1
fi
