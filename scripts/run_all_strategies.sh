#!/bin/bash
# 循环运行7个测试策略
cd /root/.openclaw/workspace

STRATEGIES=(
    "test1_br_copy"
    "test2_follow_br"
    "test3_combined"
    "test_market_regime"
    "test_market_with_stats"
    "market_regime_strategy"
    "test_follow_br"
)

for strat in "${STRATEGIES[@]}"; do
    echo "=== 运行 $strat ==="
    tag="${strat}_$(date +%H%M%S)"
    python3 scripts/pm_paper_loop.py \
        --strategy "strategies/${strat}.json" \
        --tag "$tag" \
        --scan-pages 50 \
        --cache-age-sec 60 2>&1 | tail -5
    echo ""
    sleep 2
done
