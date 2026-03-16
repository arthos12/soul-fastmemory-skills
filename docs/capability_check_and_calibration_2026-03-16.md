# Capability Check and Calibration — 2026-03-16

## Goal
Check which core capabilities are currently stable, degraded, or partially lost, and define the calibration action so they stop drifting or disappearing across sessions.

## Status Scale
- PASS: capability is active and can be called out and used reliably
- WEAK: capability exists but is not reliably triggered
- LOST/PARTIAL: capability existed before, but current session failed to surface or apply it when needed

## Current Audit

| Capability | Status | Evidence / symptom | Current judgment | Calibration action |
|---|---|---|---|---|
| Session startup restore | PASS | 本轮已按要求回读 SOUL/USER/daily/MEMORY | 启动链目前可用 | 继续保持强制启动顺序 |
| 问题搜集能力 | PASS | 已能把问题搜集写成常驻机制 | 基础能力在 | 保持关键节点扫描 |
| 新/重复/更新 问题识别 | PASS | 本轮已补进 SELF_OPERATIONS/MEMORY | 已恢复 | 后续每条问题都按该分类更新 |
| 问题判级 S/A/B/C + P0/P1/P2/P3 | WEAK | 这轮需要 Jim 提醒后才调出 | 能力未丢，但触发不稳 | 默认在正式问题项中强制输出判级 |
| 根问题优先识别 | WEAK | 能看到很多问题，但锁主问题慢 | 当前核心短板 | 新增 R/E/V/M/Q 类型层，强制先判根问题 |
| 解释后附方案 | WEAK | 多次出现解释没带方案 | 已被 Jim 连续指出 | 解释型输出固定模板：原因→方案→动作→执行 |
| 解释/方案后立即执行 | WEAK | 说了“后面会写规则”，未当轮执行 | 执行触发不够硬 | 方案型输出默认直达执行，不停留在承诺层 |
| 完整方案生成 | WEAK | 能给方案，但容易先出解释/半成品 | 有能力，稳定性不足 | 固定完整方案 7 要素模板 + 二审闸门 |
| 可过性前置审查 | WEAK | 方案经常先产出再返工 | 审查触发不稳 | 方案发出前必过 4 问：能解/能走/能过/更优 |
| 执行层畅通 | PASS/WEAK | 相比之前更好，但仍可能停在方案层 | 未完全稳定 | 继续执行“问题→方案→需求→执行→验证” |
| 恢复旧能力/旧规则调用 | LOST/PARTIAL | 旧判级法、旧恢复链需 Jim 提醒 | 明显存在调用掉线 | 做能力检查表 + 快恢复索引 |
| 快恢复层写入意识 | WEAK | 有 daily 和记忆，但关键能力未必进快恢复层 | 保存链仍不稳 | 重要能力变更同时写 memory + fast recovery/task docs |
| 主线持续推进 | PASS/WEAK | 已建立规则，但仍会被解释拖慢 | 方向对，执行密度不足 | 每轮回复后默认恢复主线下一步 |

## Current Highest-Risk Capability Gaps
1. 根问题优先识别（R 类能力）
2. 旧能力即时调用恢复
3. 解释型输出自动附方案并立即执行
4. 完整方案一次成型能力
5. 快恢复层同步，防止下次又“知道过但调不出来”

## New Calibration Rules
1. Formal problem items must always include: `type + severity + priority + next action`
2. Explanation replies must always include: `cause + solution + immediate action`
3. If a reply contains a solution, execution starts in the same turn unless blocked by permission/risk
4. Any capability that was known before but failed to trigger in-session counts as a recovery defect, not as “just forgot to mention it”
5. Important capability repairs must sync into at least two layers: long-term memory + executable operations doc

## Immediate Calibration Targets
- Restore stable use of problem grading with type layer: `R/E/V/M/Q + S/A/B/C + P0/P1/P2/P3`
- Restore stable root-problem lock before broad analysis
- Restore explanation→solution→execution default chain
- Restore capability-recovery awareness: if Jim has to remind me of an old working mechanism, mark as capability drift

## Current Main Judgment
The biggest current loss is not raw intelligence or planning ability.
The biggest loss is **stable capability retrieval and triggering**: some good mechanisms still exist in memory/files, but are not reliably surfaced at the right moment.

## Acceptance Criteria
This calibration is only considered effective if in subsequent turns I can:
1. classify problems as new/repeat/update without reminder
2. grade them with type/severity/priority without reminder
3. answer explanations with solution + execution in same turn
4. lock root problem faster before expanding into broad analysis
5. stop needing Jim to re-supply previously established mechanisms
