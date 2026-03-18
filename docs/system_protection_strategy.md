# System Protection Strategy

## 目标
- CPU/内存不崩溃；优先保证系统稳定与可恢复。
- 在高压阈值出现时，立刻进入保护态，记录证据并自动降载。

## 关键指标与阈值
- 可用内存 `available_mb < 300`
- Swap 使用 `swap_used_mb > 512`
- CPU 负载 `load1 > 2 * nproc`

## 保护动作（自动）
1. 立即写入快照（system_guard/last.json + history.jsonl）
2. 写入告警记录（system_guard/alerts.jsonl）
3. 进入保护态（写入 system_guard/guard.flag）
4. 保护态下禁止启动高负载任务（量化批量/回测等）

## 恢复条件
- available_mb >= 500
- swap_used_mb <= 256
- load1 <= 1.2 * nproc

## 人工可选动作（需确认）
- 清理缓存（drop_caches）
- 停止非关键服务
- 迁移/延后高负载任务

## 相关脚本
- `scripts/system_protection_check.sh`
- `scripts/system_protection_guard.sh`
