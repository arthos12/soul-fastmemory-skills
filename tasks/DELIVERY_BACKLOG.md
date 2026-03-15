# DELIVERY_BACKLOG.md (Single Source of Truth)

目标：把“我们聊过的需求”全部变成可复用能力与可验收产物。

落地分两阶段：
- [m] = MVC骨架（三件套：模型卡片+脚本+最小测试），脚本可能还是stub
- [x] = 可运行落地（脚本能跑出数据/结果；不是只生成骨架）

规则：
1) 任何新需求必须先进入本清单（否则视为没开始做）。
2) 空闲时间优先把 [m] 推到 [x]（提高真正完成率），而不是无限新增 [m]。
3) 每次推进必须能给证据：文件清单+复跑命令。

## P0（最高优先）：需求清单完整性 + 转化率
- [x] requirement_intake_and_dedupe - 新需求采集/去重/依赖关系/主次标注（把聊天内容收进清单）  # done_at=2026-03-15T14:50:18Z artifacts=scripts/requirement_pipeline.sh,scripts/req_add.py,scripts/req_triage.py,scripts/req_sync_backlog.py,scripts/req_dedupe.py,data/requirements/dedupe_report.json
- [x] delivery_ratio_report_v2 - 落地占比报表：新增/完成/净增/依赖链（你要看的那套）  # done_at=2026-03-15T15:00:59Z artifacts=scripts/delivery_ratio_report_v2.py

## P1（高优先）：核心能力落地（我们聊过但没真正做完）
- [m] lobster_watch - Lobster 0xecc…4444：一键拉取价格/量/买卖/流动性，写入csv/jsonl  # done_at=2026-03-15T15:01:00Z artifacts=scripts/lobster_watch.sh  # downgraded_from_x=stub_detected
- [m] gold_silver_watch - 黄金白银：一键拉取价格/趋势proxy，写入csv/jsonl  # done_at=2026-03-15T15:01:01Z artifacts=scripts/gold_silver_watch.sh  # downgraded_from_x=stub_detected
- [m] a_share_data_demo - A股：选1个稳定数据源，做最小demo拉指数/行业  # done_at=2026-03-15T15:01:01Z artifacts=scripts/a_share_data_demo.sh  # downgraded_from_x=stub_detected
- [m] polymarket_brier_scaffold - 结算后Brier score：写脚手架与数据结构  # done_at=2026-03-15T15:01:02Z artifacts=scripts/polymarket_brier_scaffold.sh  # downgraded_from_x=stub_detected
- [m] model_audit_auto_log - 模型库应用审计：每次batch记录使用模型+场景+指标  # done_at=2026-03-15T15:01:03Z artifacts=scripts/model_audit_auto_log.sh  # downgraded_from_x=stub_detected

## P2（中优先）：你明确提过但还没落地/没补齐的
- [m] test_requirement_add_x - test requirement: add X  # mvc_at=2026-03-15T13:21:40Z  # done_at=2026-03-15T15:02:47Z artifacts=scripts/test_requirement_add_x.sh  # downgraded_from_x=stub_detected
- [m] polymarket_guide_research_pipeline - 不依赖Brave key的Polymarket攻略/信息源抓取与整理（含X/Twitter替代路径）  # mvc_at=2026-03-15T13:18:39Z  # done_at=2026-03-15T15:02:48Z artifacts=scripts/polymarket_guide_research_pipeline.sh  # downgraded_from_x=stub_detected
- [m] brave_search_fix_or_replace - Brave Search 缺key的修复或替代搜索链（避免卡死）  # mvc_at=2026-03-15T13:18:39Z  # done_at=2026-03-15T15:02:48Z artifacts=scripts/brave_search_fix_or_replace.sh  # downgraded_from_x=stub_detected
- [m] long_opportunity_alert_template - >50%机会提醒模板（触发/失效/风险/收益逻辑/阶段）  # mvc_at=2026-03-15T13:18:39Z  # done_at=2026-03-15T15:03:05Z artifacts=scripts/long_opportunity_alert_template.sh  # downgraded_from_x=stub_detected

## Done log
- 说明：Done 必须写 [x] 并附 done_at + 产物清单（文件路径）。
