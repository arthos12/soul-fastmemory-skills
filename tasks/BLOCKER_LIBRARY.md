# BLOCKER_LIBRARY

## Active root blocker

### BLK-R-S-P0-001 卡点处理能力未固化
- Type: R
- Severity: S
- Priority: P0
- Status: OPEN
- Symptom:
  - 识别卡点后停在说明层
  - 不自动把清卡点升为当前最高优先级
  - 需要 Jim 追问才继续推进
- Impact:
  - 主线推进被反复中断
  - 任务无法稳定打通
  - 出现头痛医头脚痛医脚
- Required behavior:
  1. 主线一旦被卡点阻断，卡点自动升格为当前唯一最高优先级
  2. 禁止只解释卡点，不执行清卡点动作
  3. 未打通前，不切换到非关键展开
  4. 只有打通 / 明确失败边界 / 需要 Jim 拍板，才允许回报
- Current sub-blockers under this root:
  - BLK-E-A-P0-002 PM 短周期市场分类器过弱，导致可下单池为空
  - BLK-E-A-P0-003 BoneReader 仅到 profile 聚合层，未打到 market/activity 明细层

### BLK-E-A-P0-002 PM 短周期市场分类器过弱
- Type: E
- Severity: A
- Priority: P0
- Status: OPEN
- Goal:
  - 产出可下单短周期 crypto PM 市场池
- Next action:
  - 扩展 market scan + 页面读取，直接抓真实短周期 up/down / above/below 市场

### BLK-E-A-P0-003 BoneReader 明细层未打通
- Type: E
- Severity: A
- Priority: P0
- Status: OPEN
- Goal:
  - 拿到 market/activity/positions 更细数据层
- Next action:
  - 用 openclaw browser 做页面交互、滚动、tab 切换与请求抓取
