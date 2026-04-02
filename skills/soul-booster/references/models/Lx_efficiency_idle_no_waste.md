# Lx efficiency_idle_no_waste

## 一句话定义
把“空闲不浪费”变成可复跑能力：一键运行需求管线并输出 S/A 落地报表，作为空闲执行的自查与导航锚点。

## 适用场景
- 空闲执行是否真的在推进需求落地
- 需求落地占比/转化率的快速自查

## 输出格式（强制）
- 打印 `Delivery ratio v2`（S/A mvc、done、转化率、未完成清单）
- 产物文件：`data/requirements/dedupe_report.json`

## 验收
- 运行：`bash scripts/efficiency_idle_no_waste.sh`
- 通过：能打印报表且不报错
