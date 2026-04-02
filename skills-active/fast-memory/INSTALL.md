# fast-memory 安装后如何直接应用

安装后，agent 应直接按以下默认规则使用本 skill：

## 新会话恢复
1. 先读 `LAST_SESSION.md`
2. 再读 `SESSION_HANDOFF.md`
3. 再读 `MEMORY.md`
4. 再补最近 daily note / checkpoint
5. 不够时回查 recent full-session buffer

## 保存
先分类，再按重要级别决定保存完整度。

### 快速保存（默认）
只要出现以下任一情况，应至少更新 `SESSION_HANDOFF.md`：
- 用户表达结束这轮 / 先收尾 / 保存一下 / 记一下
- 会话可能即将 reset / 中断
- 已经形成明确结论、下一步、阻塞或关键文件

当最近主线已经明确，或高价值近端上下文足够清晰时，**还应同时刷新 `LAST_SESSION.md`**。

### 完整收尾
当一轮工作相对完整结束时，默认执行：
1. 更新 `LAST_SESSION.md`
2. 更新 `SESSION_HANDOFF.md`
3. 按需更新 `memory/YYYY-MM-DD.md`
4. 只有长期有效规则才写入 `MEMORY.md`

## 默认参数
- recent full-session buffer = 3
- constrained mode = 1
- hot retention = 3 天
- structured first, full-session fallback second
- high importance = high completeness

## 关键执行约束
- `LAST_SESSION.md` 不是可选装饰层，而是最近主线快速恢复层
- `SESSION_HANDOFF.md` 用于最小可恢复交接
- `MEMORY.md` 必须保持薄，只存长期有效规则
- daily note 记录当天细节，不替代 `LAST_SESSION.md`
- 若 `LAST_SESSION.md` 长期缺失，应视为执行闭环不完整

## 生命周期
- 最近 session 完整保留
- 超过 3 天转入提炼后存储
- 数据过大时进行二次提炼
- 原始老 session 在完成转移后才删除
