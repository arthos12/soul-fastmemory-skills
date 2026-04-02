# Logic / Understanding Retest — 2026-03-14

## Real target
不是泛泛地“提高逻辑和理解”，而是降低这类重复失败：
- 把真实问题答偏
- 把症状当根因
- 规则写了但没进恢复链
- 保存了信息却没保存到可恢复层

## Recent weakness classification

### Weakness A
- Problem: session 切换后能力波动明显
- Failure type: save / recovery failure
- Why not classify as pure understanding failure:
  - 我已经理解到你要的是“运行层能力不要丢”，不是普通记忆恢复。
  - 但理解之后没有稳定落到快恢复链和触发链，所以主要失败在恢复闭环。

### Weakness B
- Problem: “空闲主动推进”说得出来，但行为上未完全稳定恢复
- Failure type: rule adoption failure + save / recovery failure
- Root issue:
  - 规则存在
  - 但默认工作状态未被强制恢复

### Weakness C
- Problem: 容易在复杂问题上先给大段解释，再落地修复
- Failure type: judgment / prioritization failure
- Root issue:
  - 解释冲到了执行前面
  - 先修结构再短答的顺序有时仍不够稳定

## Leverage fixes selected
1. **恢复层优先修复**
   - 因为它能同时改善：session 恢复、空闲推进显现、行为连续性
2. **审计先于自夸**
   - 用 `idle_progress_audit.md` 检查真实状态，而不是靠口头判断
3. **因果链表达固定化**
   - 每次重要修复都要求：问题 → 根因 → 干预 → 预期改善
4. **把解释后置**
   - 先执行修复，再汇报结构和原因

## Expected improvement
- 对“你到底现在有没有这项能力”这类问题，先实时核验，再给结论
- 对“为什么又出问题”这类问题，优先给根因分型，而不是只描述现象
- 对“执行”指令，优先直接落盘/修改，而不是继续讨论方案

## Next retest target
1. `/new` + `加载数据` 后，检查是否能短答恢复当前主线与下一步
2. 下次再遇到“有没有保存”“当前是否生效”类问题时，先实时查文件/状态再回答
3. 在不牺牲严谨的前提下，进一步压缩首答长度，先给结论再给结构
