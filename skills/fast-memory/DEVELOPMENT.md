# fast-memory 开发文档

## 结构
- `SKILL.md`：主规则入口
- `INSTALL.md`：安装后默认应用方式
- `references/需求文档.md`：完整需求逻辑
- `references/test_plan.md`：测试方案

## 设计目标
- 不丢重要信息
- 快速恢复最近主线
- 分层保存
- 动态增量保存
- 保持速度、稳定性、简洁性

## 核心存储层
1. `MEMORY.md`：长期规则
2. `LAST_SESSION.md`：最近主线快速恢复层
3. `SESSION_HANDOFF.md`：当前步骤 / 下一步 / blocker
4. `memory/YYYY-MM-DD.md`：当天细节
5. recent full-session buffer：兜底原始层

## 开发原则
- 先理解内容，再分类保存
- 高价值内容完整保存
- 低价值噪音不保存
- `LAST_SESSION.md` 不是可选装饰，而是默认快恢复层
- 动态保存要保恢复，不要拖慢日常使用

## 测试要求
每次重要更新后，至少检查：
- new session 恢复是否正常
- 动态保存是否命中
- 分类是否准确
- 是否引入明显性能负担
