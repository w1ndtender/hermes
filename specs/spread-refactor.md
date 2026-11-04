# 交接规格书：把 PEARL 期现系统从「脚本堆」重建成分层的可验证系统

给 Codex / Claude Code 的工作说明。作者：Hermes（只出需求与验收，不写代码）。

---

## 0. 一句话目标

现有 `/home/ubuntu/spread` 里 30+ 个脚本能跑，但**同一件事有多份实现、错误被吞、状态不可信、改一处崩一片**。
目标：在**不改变交易逻辑和现有收益口径**的前提下，重建成四层，**每一层都有测试**，并保持与交易所对接的现有能力。

**硬约束：不许一次性重写。必须按下面的迁移顺序，每一步都能独立上线并回滚。**

---

## 1. 现状问题（必须逐条解决，不要只挑容易的）

| # | 问题 | 证据 |
|---|---|---|
| 1 | 价差有 3 份实现，口径不一致 | `edge.py`、`exec.edge_of()`、`spread_alert.py` 各自算 |
| 2 | 权益有 3 个算法，数字互相打架 | `combined_equity.py`、`equity.py`、HL `portfolio` |
| 3 | 用快照当实时价 | `chain_cex_scan.py` 用 30 分钟前的 `bsc_scan.json`，导致 BTW 6.5% 假机会 |
| 4 | 稳定币价格被算成 $6.45 | `wallet_watch.price()` 用 DexScreener 的 `priceUsd` 但没校验 `baseToken.address`，USDT 事件 usd 虚高 6.4 倍 |
| 5 | 同名不同币无闸 | ARIA 链上 0.00683 vs 永续 0.1174（差 17 倍）被当成 1600% 机会 |
| 6 | 错误被静默吞掉 | 全仓 `except: pass`；`eth_getLogs` 不带 address 静默返回空；SafeTrade 接口挂掉时 238 次报错无人知 |
| 7 | 状态散落、无锁、重启即丢 | `state.json` / `wallet_seen.json` / `wallet_bucket.json` / 各种 `*_cache.json`；模拟盘读真实仓位的 bug |
| 8 | 判断与执行耦合 | `hedger.py` 1000+ 行，行情/风控/下单/记账/推送全在一个文件 |
| 9 | 成本模型不随规模变 | 2.2% 来自一笔实盘样本，$50 和 $500 名义都用同一个数 |
| 10 | 阈值无验证 | 入场 2.0%、上限 300 颗、资费线 0.15%，没有样本外检验 |
| 11 | 几乎无测试 | 除 `tests_hedger.py` 9 个用例外全裸奔 |
| 12 | 靠字符串替换改代码 | 已多次改坏（`NameError: os`、`IndentationError`） |

---

## 2. 目标架构（四层，单向依赖）

```
core/          纯函数，无 IO：价差、成本、仓位、盈亏口径
  pricing.py     一条公式只写在这里：entry_edge / exit_edge / net_after_cost
  cost.py        成本模型（按规模与场所插值，不再是常量 2.2%）
  sizing.py      能吃多少（池深、盘口、保证金、硬上限取最小）

data/          所有外部数据，唯一入口，带缓存与新鲜度
  venues/        binance.py bitget.py gate.py okx.py bybit.py（统一接口：book/symbols/funding）
  chain/         dexscreener.py geckoterminal.py rpc.py（统一接口：pool/price/ohlcv/logs）
  registry.py    符号 → (链, 合约地址, 各所符号) 的唯一映射表，落库
  freshness.py   每个数据带 ts，超过 TTL 一律拒用（不许拿旧的顶）

risk/          只做判断，不下单
  limits.py      单日成交笔数、单日亏损、连续亏损、名义/持仓倍数
  killswitch.py  触发即写 STOP 并停服务（现有 kill_switch.py 演化为库函数）

exec/          只做执行与记账
  broker_hl.py   Hyperliquid 下单/平仓/持仓（封装现有 exec.py 的 HL 部分）
  broker_st.py   SafeTrade 下单/余额（封装 st_api.py）
  ledger.py      所有成交、资金费、转账写同一本账（append-only）

services/
  hedger.py      只做编排：读 core/risk → 调 exec
  alerts.py      统一出口（TG + 飞书），卡片格式一处定义
```

规则：
- `core` 不许 import 任何网络库。
- `data` 不许被 `core` 依赖。
- 任何模块都不许自己实现一遍价差或权益。
- 所有对外数字必须带 `source`（哪个所、哪个接口、什么时间）。

---

## 3. 必须先做的三件小事（1 天内可交付）

1. **统一价差**：`core/pricing.py` 写 4 个函数（entry_edge/exit_edge/net_after_cost/positions），
   把 `edge.py`、`exec.edge_of`、`spread_alert` 全部改为调用它，并加断言测试：
   - 永续买一 1.4642 / 现货卖一 1.45 → entry_edge = +0.98%
   - 标记价一旦被传入 → 抛异常（不许静默降级）
2. **统一权益**：只保留 HL `portfolio.accountValueHistory` + SafeTrade 余额，其余算法删掉，写进 `core/`，
   输出必须带 `as_of` 时间戳。
3. **符号注册表**：`data/registry.py` 建 `symbol → {chain, address, venues{sym}}`，
   写入时校验「链上价与永续价量级差 < 3 倍」，不满足就标记 `unverified` 并拒绝参与计算。

---

## 4. 验收标准（缺一条不算完成）

- [ ] `pytest` 覆盖率：`core/` ≥ 90%，`risk/` ≥ 80%，`exec/` 的关键路径有集成测试（用 mock 交易所）
- [ ] 所有外部请求有超时 + 重试 + 失败可见（日志一条 warn，不再 `pass`）
- [ ] 任何数字进推送前，必须能回答：来源、时间、口径
- [ ] 同一份数据两次调用结果一致（幂等）
- [ ] 断网/接口挂掉时：不交易、不误报、有明确日志，恢复后自动继续
- [ ] `kill_switch` 有测试：构造 21 笔成交 / 净亏 $6 / 连亏 3 次 → 必须停机
- [ ] 默认 `dry_run=true`；真下单必须显式传参并读取 `config.json` 的 `live: true`
- [ ] 迁移过程中每个 PR 都能单独回滚，旧脚本保留一个版本周期

---

## 5. 明确不要做的事

- 不要新增策略、不要调阈值、不要「顺手优化」收益模型。
- 不要把 SafeTrade / Hyperliquid 的鉴权方式换掉（现有 `st_api.py` 走本机 Chrome CDP + 住宅代理，能跑就别动）。
- 不要引入数据库以外的重型依赖；SQLite 够用。
- 不要把 `io:PRL`（HIP-3 dex）当成普通永续处理，它有独立 dex 与保证金。

---

## 6. 环境事实（省得再踩）

- 机器：`/home/ubuntu`，Python 3.12，`~/spread/.venv`
- Hyperliquid：钱包 `0xE24Cff9DE22F2242F967CFe67bA1Cb1576fCB278`，`io:PRL` 在 dex `io`，3x
- SafeTrade：必须经本机 Chrome（CDP 9335）+ 住宅代理 socks5://127.0.0.1:1080，直连被 Cloudflare 挡
- BSC 出块 **0.45 秒**（不是 3 秒）；`bsc.blockrazor.xyz` 限流 429；`publicnode` 的 `eth_getLogs` 不带 address 会**静默返回空**
- 交易所只有 Bitget 有账户；Gate/Bybit/Binance/OKX 均无
- 资金：约 1,430 USDT（SafeTrade）+ HL 已清空

---

## 7. 提交方式

每个 PR 一个主题，标题格式：`refactor(core): 统一价差口径`。
PR 描述里必须写：改了什么口径、旧值是多少、新值是多少、哪个测试能证明。
不允许在同一次提交里既改逻辑又改阈值。
