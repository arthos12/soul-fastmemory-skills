# 策略分析报告系统

## 快速导航

### 当前迭代
- [ITERATION_LOG.md](./ITERATION_LOG.md) - 迭代日志
- [INDEX.md](./INDEX.md) - 统一索引

### 历史迭代
- [iterations/v1/](./iterations/v1/) - v1迭代

### 模板
- [templates/](./templates/) - 标准化模板

---

## 目录结构
```
strategy_analysis/
├── README.md           # 项目概览
├── ITERATION_LOG.md    # 迭代日志
├── INDEX.md            # 统一索引
├── templates/          # 模板
│   ├── analysis_template.md
│   └── iteration_template.md
├── iterations/         # 每次迭代
│   └── v1/
│       ├── ITERATION.md    # 迭代记录
│       ├── analysis_v1.md  # 分析报告
│       └── validation_v1.md # 验证结果
└── archives/           # 历史归档
```

## 使用流程
1. 发现问题 → 创建 iterations/vX/
2. 撰写 ITERATION.md → 明确假设和预期
3. 执行分析 → 写 analysis_vX.md
4. 验证结果 → 写 validation_vX.md
5. 更新 ITERATION_LOG.md 和 INDEX.md
