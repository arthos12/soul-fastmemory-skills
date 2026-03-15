# C0 对话需求捕获闸门（Conversation Requirement Capture Gate）

## 一句话定义
当用户在一条消息里列出多项“问题/需求/验收口径”时，必须立刻把它们结构化写入需求系统（Inbox→Triage），并用人话回执“我收到了几条”。

## 触发条件（任一命中就触发）
- 出现关键词：`问题` / `故障` / `不对` / `跑偏` / `你应该` / `需要` / `必须` / `验收` / `口径` / `效率=`
- 或出现列表结构（换行、顿号/分号密集）。

## 强制动作（必须执行）
1) 把该消息拆成 1..N 条需求，写入 `tasks/REQUIREMENTS_INBOX.jsonl`
2) 立刻运行 `python3 scripts/req_triage.py --limit 50`
3) 立刻生成 latest 视图：`python3 scripts/req_latest.py`
4) 对用户回一句人话：
   - “我已把你这段拆成 N 条 S/A 需求入库，接下来按优先级推进。”

## 禁止
- 只在聊天里复述，不入库
- 让用户重复说第二遍

## 验收
- 用户一次性列出多项问题后，`REQUIREMENTS_INBOX.jsonl` 与 `REQUIREMENTS_TRIAGED.jsonl` 在 1 分钟内出现新增记录。
