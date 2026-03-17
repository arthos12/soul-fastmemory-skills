# Polymarket Paper Trading - Software Verification Plan

目标：验证回填逻辑、数据解析与下单选边的准确性。确保“软件没写错”，从而能有效验证策略。

## 1. 核心验证项
- **双向测试 (Dual-Side Test)**：同一市场同时下涨/跌（Yes/No），验证到期后是否必然出现一赢一输且被程序正确识别。
- **回填逻辑 (Backfill Integrity)**：验证 5 分钟短周期市场到期后，程序是否能自动识别 realized 状态并计算 PnL。
- **数据一致性 (Data Consistency)**：验证 `limitPrice`、`picked side`、`marketId` 是否在整个生命周期中保持一致，无 0 价或错位。
- **去重检查 (Deduplication)**：验证跨轮次是否重复下同一市场，确保统计样本的独立性。

## 2. 验收标准
- 双向测试：必须有 1 个 WinFlag=True，1 个 WinFlag=False。
- realized 识别：5 分钟到期后，kind 必须从 m2m 变为 realized。
- 价格校验：limitPrice 必须 > 0，且符合对应 side 的当时价格。

## 3. 故障触发
- 若双向测试出现全输或全赢 -> 判定为结果解析逻辑故障。
- 若 10 分钟后仍全是 m2m -> 判定为到期识别逻辑故障。
- 若跨轮重复率 > 30% -> 判定为样本生成逻辑故障。
