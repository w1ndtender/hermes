# 任务书 04：跨所价差回测器（A 所现货 + B 所永续）

在 `~/spread/backtest/` 旁边新增 `crossvenue/` 子模块。**不改动 v2 的任何文件与测试。**

## 目标

回答一个问题：**同一个币，在 A 所买现货、在 B 所空永续，扣掉两所手续费、滑点、调资摩擦之后，有没有正期望。**

这是同所价差被证伪之后的自然延伸。同所的结论已经确定：180 天 148 个市场、加流动性过滤后只剩 4 笔 +$101，价差全部出现在无法成交的薄盘口上。

## 与 v2 的四个关键差别

1. **两个市场配对**：现货来自交易所 A，永续来自交易所 B，A ≠ B。
2. **必须按时间戳严格对齐**：只保留两边都存在且都「可交易」的同一小时。
3. **调资摩擦**：两腿资金分别停在两个所，开仓不需要转账；但两所余额会漂移，需要定期再平衡。加一个 `rebalance_cost_pct_per_trade`（默认 0.05）计入每笔成本。
4. **接口复用**：同一组 (交易所, 币, 现货/永续) K 线会被多个配对复用，**必须缓存到内存或 `cache/` 目录，不许重复请求**。

## 硬约束（与 v2 完全一致，不许放松）

- 只用公开接口，不带 key，不下单，不读私钥
- 请求超时 + 最多 3 次重试 + 失败必须抛错或记 `status="error"`，**绝不许静默填 0 或沿用旧值**
- 每页之间 sleep ≥ 120ms，429 退避重试
- **下一根 open 成交**（防前视）
- 流动性过滤：A 所现货当根 ≥ `min_spot_usd_per_hour`（默认 100000）、B 所永续当根 ≥ `min_perp_usd_per_hour`（默认 200000）
- 容量：`min(A现货量, B永续量) × capacity_fraction`（默认 0.01），上限 `max_position_usd`（默认 5000），低于 `min_position_usd`（默认 200）跳过并计数
- 缺失不插值；不可交易的 K 线不产生信号，持仓中遇不可交易 K 线不顺延强平

## 策略定义

```
basis = (perp_B_close − spot_A_close) / spot_A_close × 100
入场：basis ≥ entry_pct 且无持仓 → 在 A 买现货、在 B 空永续（用 t+1 open）
出场：basis ≤ exit_pct 或持仓 ≥ max_hold_h → 两腿一起平（t+1 open）
```
参数扫描沿用 v2 的 `entries` / `exits`。

## 成本

```
往返成本 = A 现货 taker×2 + B 永续 taker×2 + 滑点×2 + rebalance_cost_pct_per_trade
```
费率从 `settings.json` 的 `fees` 读，Gate 仍是 0.20%、其余 0.10%；**永续腿按各所真实 taker 分开配**（新增 `perp_taker_pct`，币安/欧易/Bybit 现货 0.10、永续 0.05；Gate 均 0.20）。
同时保留「零成本 / 默认 / 成本×2」三档。

## 输出

`out_cross/backtest_report.md` + `backtest_result.json`：

1. **配对表**：每个 (A现货, B永续, 币) 的 basis P50/P90/P99/max、可交易小时占比
2. **参数表**：笔数、胜率、每次净 %、单笔均额 $、累计 $、最大回撤 %、被过滤入场数、容量跳过数
3. **排行榜**：按累计 $ 排序，只列 `trades ≥ 10` 且 `total_pnl_usd > 0`
4. **全局汇总**：总笔数、总盈亏 $、最大单市场贡献占比
5. **反向配对**：A→B 与 B→A 都要跑（12 个有序配对/币），报告里分区展示

## 规模控制

- 默认 `--symbols` 只跑 `--venues` 里全部有序配对，单次运行币数 ≤ 12（可传参）
- 缓存命中率必须打印出来（`cache_hits / total_requests`）
- 单次运行不允许超过 25 分钟；超过就分批

## 验收命令

```bash
cd ~/spread
.venv/bin/python -m backtest.crossvenue --symbols WUSDT,BOMEUSDT,GMXUSDT --days 180 --venues binance,okx,bybit,gate --out backtest/out_cross
.venv/bin/python -m backtest.tests.test_crossvenue -v
```

测试至少覆盖：时间戳严格对齐（一边缺小时整根丢弃）、缓存不重复请求、下一根 open 成交、容量跳过、不可交易不顺延、失败记 error 不静默。

## 不许动
- v2 的 `same_venue.py`、`settings.json` 现有字段、`tests/test_backtest.py`
- `~/spread` 其它任何文件、`config.json`、任何私钥

## 回滚
新增目录，回滚 = `rm -rf ~/spread/backtest/crossvenue ~/spread/backtest/tests/test_crossvenue.py`
