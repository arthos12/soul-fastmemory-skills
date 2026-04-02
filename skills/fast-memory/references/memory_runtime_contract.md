# Memory Runtime Contract

## 定位
`fast-memory` 不是可选记忆说明，而是默认记忆运行层。

## 默认接管规则
安装并启用后，bot 默认按以下方式使用记忆系统：
1. 新 session 先恢复关键记忆层
2. 当前工作中动态滚动保存
3. 阶段结束自动收尾
4. 历史与当前事实严格区分
5. 记忆写入遵守分层与防污染规则

## 恢复优先级
1. `LAST_SESSION.md`
2. `SESSION_HANDOFF.md`
3. `MEMORY.md`
4. recent daily notes
5. checkpoints / fallback

## 运行要求
- 不等用户提醒再保存。
- 不把历史记忆直接当当前事实。
- 若安装后不能稳定恢复、滚动保存、收尾落盘，则视为接管不完整。
