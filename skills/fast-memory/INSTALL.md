# fast-memory 安装后如何直接应用

安装后，这个 skill 就应作为默认记忆工作流直接生效。
agent 在涉及 session 恢复、保存、handoff、记忆分层、冷数据降级时，应直接按本 skill 执行。

## 新会话恢复
1. 先读 `LAST_SESSION.md`
2. 再读 `SESSION_HANDOFF.md`
3. 再读 `MEMORY.md`
4. 再补最近 daily note / checkpoint
5. 不够时回查 recent full-session buffer

## 保存
先分类，再按重要级别决定保存完整度。

## 默认参数
- recent full-session buffer = 3
- constrained mode = 1
- hot retention = 3 天
- structured first, full-session fallback second
- high importance = high completeness

## 生命周期
- 最近 session 完整保留
- 超过 3 天转入提炼后存储
- 数据过大时进行二次提炼
- 原始老 session 在完成转移后才删除
