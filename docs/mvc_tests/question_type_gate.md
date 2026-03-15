# MVC Test: question_type_gate

Manual spot-check (5 cases):
- Ask "哪里出错了" => must output Type=定位 and give root-cause, no options.
- Ask "现在去做" => Type=方案执行 and provide J0+A1.
- Ask "完成比例" => Type=证据汇报 and output numbers+commands.

Pass: no type mismatch.
