# 任务书 03：回测器 v2 —— 加流动性过滤、容量上限、美元口径、防前视

在现有 `~/spread/backtest/` 上增量修改（**不要重写，不要动 tests 里已经通过的 9 项**）。

## 为什么要改（真实数据支撑）

1. Gate 的 GMX 出现 2.6% 价差，查原始 K 线：那一小时现货成交额 **$248**，下一小时 **$7**。
   死盘口的陈旧收盘价 = 假机会。**必须按成交额过滤。**
2. 现在是「用当根 close 判断、也用当根 close 成交」＝前视偏差。**入场/出场都改成下一根 open。**
3. 现在只输出百分比，看不出「这个策略一年能赚几美元」。**必须按容量折算成美元。**

## 改动清单（六项，逐项都要）

### 1. 抓成交量
四个数据源的 K 线都带成交额，必须一并解析并跟 K 线一起存：
- 币安 `klines`：`[7]` = 计价币成交额（USDT）
- 欧易 `history-candles`：`[7]` = 计价币成交额
- Bybit `kline`：`[6]` = 成交额
- Gate `candlesticks`：`[1]` = 计价币成交额（注意字段顺序，别按 OHLC 顺序取）

缺少成交额字段的市场 → `status="error"`，不许当 0。

### 2. 流动性过滤（新增配置，默认值如下）
```json
"min_spot_usd_per_hour": 100000,
"min_perp_usd_per_hour": 200000
```
只有当根**现货**成交额 ≥ `min_spot_usd_per_hour` **且** 永续成交额 ≥ `min_perp_usd_per_hour` 时，这根 K 线才算「可交易」。
不可交易的 K 线：不产生入场信号；持仓中遇不可交易 K 线不强制平仓（继续持有，等下一根可交易时判断）。

### 3. 防前视：下一根 open 成交
- 第 t 根收盘算出 `basis_t ≥ entry_pct` → **用第 t+1 根的 open 成交**（两腿都用 t+1 的 open）
- 第 t 根收盘算出 basis ≤ exit_pct 或到最长持仓 → **用第 t+1 根的 open 平仓**
- 第 t+1 根不存在或不可交易 → 顺延到下一根可交易的
- 超过 `max_hold_h` 也没等到可交易 K 线 → 记 `open_position`，不计入已完成交易

### 4. 容量上限（每笔能下多少钱）
```
单笔名义 = min( 现货小时成交额 × capacity_fraction,
              永续小时成交额 × capacity_fraction,
              max_position_usd )
```
默认 `capacity_fraction = 0.01`、`max_position_usd = 5000`。
单笔名义 < `min_position_usd`（默认 200）→ 该笔跳过（记 `skipped_capacity` 计数，不静默丢）。

### 5. 美元口径
每笔输出：`notional_usd`、`pnl_usd`（= notional × net_pct / 100）、`capital_usd`（= notional × 2，两腿都要占用）。
市场级输出：`total_pnl_usd`、`trades`、`skipped_capacity`、`avg_notional_usd`。
报告里给**全局汇总**：所有市场合计 `total_pnl_usd`、平均单笔 $、最大单市场贡献占比。

### 6. 报告新增一列 + 一节
- 表格加两列：`单笔均额 $`、`累计 $`
- 新增一节「剔除假机会后的排行榜」：按 `total_pnl_usd` 排序，只列 `trades ≥ 10` 且 `total_pnl_usd > 0` 的市场，前 20 名
- 明确写出：`假机会剔除计数`（因流动性过滤而消失的入场数）

## 不许动
- 不改 `~/spread` 其它文件、不改 `config.json`、不碰任何私钥
- 不删除现有 9 项测试；可以新增，不许让旧的失败
- 参数默认值只改 `settings.json`，不写死在代码里

## 验收命令
```bash
cd ~/spread
.venv/bin/python -m backtest.tests.test_backtest -v     # 旧 9 项 + 新增项全过
.venv/bin/python -m backtest.same_venue --symbols WUSDT,GMXUSDT --days 180 --out backtest/out_v2
```
验收必须看到：
1. Gate 的 GMX 在 v2 里交易数**显著减少**（因为 $248 成交额被过滤）
2. 币安 WUSDT 仍有交易，且 `total_pnl_usd` 为正
3. 报告里出现「假机会剔除计数」且 > 0
4. 所有失败市场在报告里明确标 error，不许静默变 0

## 回滚
`git` 没有就手工：改前先 `cp -r backtest backtest.bak`，回滚 = 覆盖回去。
