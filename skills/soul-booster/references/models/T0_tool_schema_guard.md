# T0 工具参数护栏（Tool Schema Guard）

## 一句话定义
任何工具调用前先做“必填参数自检”，防止因参数名/缺字段导致执行中断。

## 重点风险（已发生）
- `write` 调用缺 `content`，或参数名混用（path/file_path）。
- `edit` 调用缺 `oldText`（或 old_string）。

## 最小自检清单
- write：必须有 `file_path` + `content`
- edit：必须有 `file_path` + `oldText` + `newText`
- exec：必须有 `command`

## 验收
- 任何出现工具报错：优先判定为“参数/Schema错误”，先按清单修正再继续。
