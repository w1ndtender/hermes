# 任务书 02：同所现货-永续价差回测器（只用公开行情，不需要 API key）

交给 Codex 实现。**这是验证阶段的第一段：回测。** 不涉及下单、不读私钥、不需要账户。

---

## 目标

给一组交易对，拉取历史 K 线（现货 + 永续），按「价差 ≥ 入场阈值」进出场，
扣掉真实手续费后统计：机会次数、每次净收益、累计曲线、参数平台区。

输出一份人可读报告 + 一份机器可读 JSON，用来回答一个问题：**这个玩法有没有正期望。**

---

## 硬约束

1. **只读公开接口，不带任何 key。** 不许 import 交易所私有 SDK。
2. **不许下单、不许读取任何本地私钥或 .env。**
3. 只用标准库 + `requests`（已装）。不要引入 pandas/numpy 以外的新依赖；能不用就不用。
4. 所有请求必须有超时、重试（最多 3 次、指数退避）、以及「失败当失败」的处理——
   **抓取失败必须抛错或记为 missing，绝不允许静默填 0 或沿用上一次的值。**
5. 时间一律用 UTC 毫秒时间戳，报告里同时给北京时间。

---

## 数据源（已验证可用）

| 用途 | 接口 |
|---|---|
| 币安现货 K 线 | `GET https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=1000&startTime=` |
| 币安永续 K 线 | `GET https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=1h&limit=1000&startTime=` |
| 欧易现货 | `GET https://www.okx.com/api/v5/market/history-candles?instId=BTC-USDT&bar=1H&before=` |
| 欧易永续 | `GET https://www.okx.com/api/v5/market/history-candles?instId=BTC-USDT-SWAP&bar=1H&before=` |
| Bybit 现货 | `GET https://api.bybit.com/v5/market/kline?category=spot&symbol=BTCUSDT&interval=60&start=` |
| Bybit 永续 | `GET https://api.bybit.com/v5/market/kline?category=linear&symbol=BTCUSDT&interval=60&start=` |
| Gate 现货 | `GET https://api.gateio.ws/api/v4/spot/candlesticks?currency_pair=BTC_USDT&interval=1h&from=` |
| Gate 永续 | `GET https://api.gateio.ws/api/v4/futures/usdt/candlesticks?contract=BTC_USDT&interval=1h&from=` |

分页：币安每页 1000 根，用 `startTime` 往后翻；欧易/Bybit/Gate 用各自的时间游标。
**每页之间 sleep ≥ 120ms**，避免 429；被 429 时退避重试，不许跳过静默继续。

---

## 成本模型（不许写死成一个数）

```
成本(往返) = 现货 taker × 2 + 永续 taker × 2 + 滑点假设 × 2
```
- taker 费率从配置文件读，默认：币安 0.10%、欧易 0.10%、Bybit 0.10%、Gate 0.20%（单边）
- 滑点默认 0.02%（单边），可配
- 报告里必须同时给「零成本」「默认成本」「成本×2」三档结果

---

## 策略定义（必须零主观）

对每个交易对、每根 1h K 线：
- `basis = (perp_close − spot_close) / spot_close × 100`
- **入场**：`basis ≥ entry_pct` 且当前无持仓 → 买现货 + 空永续（记入场 basis）
- **出场**：`basis ≤ exit_pct` 或持有超过 `max_hold_h` 小时 → 平两腿
- 同一时刻只持有一组，不叠加

参数扫描（默认范围，全部要跑）：
- `entry_pct ∈ {0.3, 0.5, 0.8, 1.0, 1.5, 2.0}`
- `exit_pct ∈ {0.0, 0.1, 0.2, 0.3}`
- 只统计 `entry > exit` 的组合

**注意**：这里赚的是**价差收敛**，不是资金费。资金费单独统计（可作为附加列，但不计入主收益）。

---

## 输出（必须两个文件）

1. `out/backtest_report.md` —— 人读：
   - 每个交易对：数据区间、缺失比例、basis 的 P50/P90/P99、最大/最小值
   - 参数表：每个 (entry, exit) 组合的机会数、胜率、平均每次净收益、累计净收益、最大回撤
   - **平台区判定**：把结果画成文字表格，标出哪片参数区域是「都不错」而不是单点最优
   - 明确写一句结论：该交易对在该参数下**是否有正期望**（是/否/样本不足）
2. `out/backtest_result.json` —— 机器读：同上，结构化。

---

## 验收命令（必须能跑通）

```bash
cd ~/spread
.venv/bin/python -m backtest.same_venue --symbols BTCUSDT,ETHUSDT,SOLUSDT --days 180 --out out/
.venv/bin/python -m pytest tests/test_backtest.py -v
```

测试必须覆盖：
1. 用 10 根人造 K 线算 basis，结果与手算一致（误差 <1e-9）
2. 抓取函数在 HTTP 500 时抛错，**不返回空数组**
3. 缺失 K 线（时间戳跳空）被标记，不插值
4. 一次完整进出场的收益计算正确（含成本三档）
5. 参数扫描对非法组合（entry ≤ exit）直接跳过而不是崩溃

---

## 不许动

- 不改 `~/spread` 现有任何脚本与服务
- 不碰 `config.json`
- 不碰 `wallet_watch.py` / `hedger.py` / `exec.py`
- 新代码全部放在 `~/spread/backtest/` 目录内

## 回滚

整个功能是新增目录。回滚 = `rm -rf ~/spread/backtest ~/spread/tests/test_backtest.py`。

## PR 描述必须回答

1. 你在哪一步做了「静默容错」？为什么那不是隐患？
2. 币安/欧易/Bybit/Gate 四个源里，哪个的分页最容易漏数据？你怎么验的？
3. 平台区的判定标准是什么（具体数值），为什么这么定？
