# INDEX — 新会话先读这个

一句话索引。每份笔记的**结论 + 关键数字 + 日期**都在这，不用翻全文。

## 结论速查（最重要）

| 结论 | 数字依据 | 出处 |
|---|---|---|
| 打新收益取决于**有没有买盘**，不是打了多少 | 同工具同流程：有买盘赚 40.96U，无买盘 89 枚只赚 1.48U（差 27 倍） | `earnings-evidence` / `free-mint-reality` |
| Gang 内盘**几乎没有买盘**（V2 老盘口径） | 61 个在榜代币：59% 零成交、成交量中位数 0 BNB、已毕业 1 个。**V3 不适用**：首日 23 盘里 4 盘打满，池 24h 成交 $33,484 | `gang-liquidity` / `2026-10-28-gang-v3-first-launches` |
| V3 发射门槛是**独立钱包数**，不是钱 | 4/4 打满盘参与者 107/111/108/118，全员顶格 100 份（`capShares=100 × 100 = 10000`）；我们 3 盘 8/3/2 人，成交 0.3465 BNB = 打满盘 44.7 BNB 的 1/129 | `2026-10-28-gang-v3-first-launches` |
| 打满盘的盈利来自**二级池**，不是 mint 价差 | mint 100 份 0.000505 BNB；打满盘二级 FDV 5.44–11.01 BNB（池 $5.5k–$13.8k） | `2026-10-28-gang-v3-first-launches` |
| **价差 pp 不是钱**：一轮 = 收窄 − 0.218% 手续费 − 两边盘口宽（实测 1.20–3.10%） | 收窄 1.19pp − 0.22 − 1.29 = −0.32pp，白干；24h 永续现金流 −14.71 vs 账本 +7.33（残差 −22.05） | `2026-10-30-pearl-cash-truth` / `spot-perp-spread-execution` |
| **单腿是最大操作风险**：平仓时现货比永续快 → 攒出 70 颗裸空，买回一次亏 −$6 | 现货卖 200 颗 / 永续只平 140 颗；之后每 5 秒自动对账补永续 | `2026-10-30-pearl-cash-truth` |
| **state 里的入场价差不可信**：本轮写 3.61%，持仓均价反推只有 0.21% | 每轮必须用交易所持仓均价校准，并从它反推现货成本 | `2026-10-30-pearl-cash-truth` |
| 平仓档位要锚定历史 P5，不是「入场 − 固定 pp」 | PEARL P5=0.87%；入场 2.0% 用 −3.7pp → 全平线 −1.7%，历史 0% 时间达到 | `spot-perp-spread-execution` |
| 期现看到 2% 价差 ≠ 赚 2% | R6 300 PRL 毛 2.0262% → 净 1.9172%，立刻平仓 -6.70 USDT，打平需收敛 1.26pp（3000 PRL 需 3.00pp） | `2026-10-28-pearl-perp-basis` |
| 三家永续多头资金费全为正 → 只有「现货多+永续空」收钱 | HL 0.02595%/h、Lighter 0.04696%/h（负值 0h）、Aster 0.04080%/h；期期配对历史净 -0.015%~-0.021%/h | `2026-10-28-pearl-perp-basis` |
| **同名 ticker 是最大假信号源**：配对/挑盘先核 baseAsset 或 creator | Aster `PRLUSDT` $0.0956 ≠ `PEARLUSDT` $1.78 → 按符号对齐造 94.7% 假价差；gang 23 盘里 11 个叫 MYT、2 个 Gangstar | `2026-10-28-pearl-perp-basis` |
| 交易所自己的 oracle 有半权重跟随自身盘口 | HL `io:PRL` w_I≈0.48（盘口 D_eff 仅 $27–54），隐含外部价 1.7886 vs Safe 中价 1.765 | `2026-10-28-pearl-perp-basis` |
| 「人均 XX 刀」类说法不可信 | $50/day 被标注 unverified，原 mint 已结束 | `earnings-evidence` |
| 免费 mint 要过三问 | 有二级市场 / 地板 > 2 倍成本 / 供给有上限 | `free-mint-reality` |
| V3 打新：开盘价=打新价，但要看有没有二级买盘 | 打满的 4 盘池子 24h 成交 $454–$17,273，卖单多于买单（280/177 等）；我们打的 3 盘无池、24h 成交 0.3465 BNB | `agent-landscape` / `2026-10-28-gang-v3-first-launches` |
| Codex 重置不可预测 | 68 次重置、平均 6.0 天、最长 67.7 天；过去 60 天「48h 内重置」基础命中率 30% | `2026-10-27-daily` |
| 判开盘看 `enabled` 字段，不看 HTTP 码 | 同日 404 → 200 `{"enabled":false}`；4h11m 轮询 2,236 次全 gate_closed、真实成交 0 | `2026-10-27-daily` |
| 日志 `ok:true` ≠ 成交，对账看 `Minted` 事件 | 当天 6 条 `sale ok:true`，链上 `Minted` 只有 3 条（22:54 那批 `router: null` 假成功） | `2026-10-27-daily` |
| 每份价格 = `raiseBnb/10000×1.01`，不是常数 | 5 BNB 盘 0.000505 / 15 BNB 盘 0.001515，差 3 倍；写常数会把预算闸算错 | `2026-10-27-daily` |
| 出场链路必须开盘前先跑一遍 | selector 推的 `0x724b8b35` 不在 bytecode，真值 `0xb5c5f672`；改对后 BAW `AutoReject` 直接 `351803 blocked` | `2026-10-27-daily` |
| 单位（wei/BNB）混用是最贵的 bug | 8 个真实盘 8/8 被「募集 1.5e+19 不在 5–50」拒，错过 22:28–22:37 全部窗口 | `2026-10-27-daily` |
| Ptah 关掉网页/二维码登录，生态只能 Agent 操作 | 10/27 起 ptah.trade QR 登录暂停；同时 POA SBT 已 mint 35,645 枚 | `2026-10-28-x-digest` |
| 语料作者级复核：真人长消息里唯一新内容＝群主的 LP+双向限价对冲，但 PRL 无 CLMM 池不适用 | 顺带查实「PEARL $4,000 万池」是 10-20 后新部署的同名假池（价 2.42 vs 我们 1.47、24h 量 $53） | `notes/2026-11-01-corpus-saturation-author-pass` |
| 手册 §26：**统一账户现货 USDC 即保证金，不需划转**（原判「保证金 0」是误读；探针实测可下单）（现货 392 USDC 在 spot，不在 perp）→ 门槛调好了也开不了仓；已加保证金前置检查 | 另记借币规则/地址投毒/风控降级 | `playbooks/spot-perp-spread-execution.md` |
| 手册 §25：HL 标记价公式（mark≠mid≠oracle，已加 mark_dev 0.5% 闸）/ 单腿概率可到 50% / 失败后状态不复位会卡死 / 多档止损 / 双边成本 0.3 | 111 条中短消息全读完 | `playbooks/spot-perp-spread-execution.md` |
| 手册 §24：语料已饱和（46.5 万条 → 148 条精确候选 → 5 条新 → 1 条可用）| 继续挖边际收益≈0；瓶颈在门槛与单笔大小，不在语料 | `playbooks/spot-perp-spread-execution.md` |
| 手册 §23：3 秒时效标准（已收紧 5s/3s）/ 延迟实测 HL 20–30ms vs SafeTrade 0.4–0.8s / 返佣可把成本 0.23→0.13pp / 只信自己账本 | 5 条 | `playbooks/spot-perp-spread-execution.md` |
| 手册 §22：笔数本身是成本（501 笔 −3.4U vs 6 笔 +3024U）→ 每日轮次上限已落代码 / 费率必须归一结算周期 / 指数要看充提状态 | 3 条 | `playbooks/spot-perp-spread-execution.md` |
| 手册 §21：门槛按 P80 分位（实测 1.06% vs 挂的 3.00%）/ 成交价偏离告警已落代码 / io:PRL 参数实测 / 指数来源未确认 | 4 条 | `playbooks/spot-perp-spread-execution.md` |
| 手册 §20：成本实测 0.23pp（现货 0.1%/边是大头）/ 记账用 avg_price / PRER 剪单 / 成交权 / 指数停充污染 | 5 条全部来自语料+交易所字段实测 | `playbooks/spot-perp-spread-execution.md` |
| 手册 §19：机会窗口比精细重要（没吃满=没赚到）/ 1tick 宽+大挂量＝LP 机器人守卫（已落代码）/ 建仓价差≠平仓价差 | 3 条来自语料 + 我们自己的成交速度实测 | `playbooks/spot-perp-spread-execution.md` |
| pearlusdt 价差研究（1.5h 真实成交+HL 1m）：中价基差中位 **1.73%**，挂单口径 **1.03%** | 门槛 1.0% 时 15 轮/1.5h、每轮 +0.7pp；**逆行中位 −0.8pp、最大 −1.42pp** → 止损须 ≥2pp | `2026-10-31-pearlusdt-basis-study` |
| pearlusdt 实测（1.6h / 1000 笔）：真实价差中位 **1.23%**，3.0% 门槛 0% 时间满足 | 挂买一中位 7 秒成交、P90 22 秒；300 颗只占 1.6h 吃买一量的 0.7% | `2026-10-31-pearlusdt-microstructure` |
| 错误台账 18 条（12 条已发生 + 6 条巡检新增）：每条都必须有防复发的代码或检查 | 取价≠下单市场 / 低于最小名义 / 撤单不回读 / pp 当钱 / state 入场价 / 粉尘 / 符号拼接 … | `playbooks/mistake-ledger` |
| 2026-10-31 三道闸落地：确认窗口 3 次 / 报价时效 15s+5s / 以损定仓 $25 | 撤单回读+cancel 三次重试、粉尘 0.2 颗自动清；tests 12/12、drift 一致 | `playbooks/spot-perp-spread-execution` §17 |
| 群聊 46.5 万条只留下**对这条线有用的 36 条**，写进期现手册 §10–§15 | 单腿静默形态/确认窗口/时效/ADL 真实规则/指数成分/记账四件套；另列 7 类明确不适用 | `playbooks/spot-perp-spread-execution` |
| taoli 群 465,057 条全量读完：**没有可抄的参数，只有失败清单** | 2025-03→2026-10；9 条私库缺口，3 条直接改执行器 | `2026-10-31-taoli-groupchat-full-distillation` |
| 单腿有**三种静默形态**，pnl 里可能一条记录都没有 | bundle 误判 / 黄色 `transaction replaced` / 合约被平现货还在但无 pnl | 同上 |
| 爆仓价由**指数成分**决定，成分会被挑着打 | Gate LA：kucoin 进指数 → 40+ 人爆仓人均 3 万刀，拒赔；维权成本 6000U | 同上 |
| 资金费**周期与上下限会被交易所中途改** | 2026-07-15 BN SKHYNIX/SAMSUNG 8h→4h、±0.50%；ARIAUSDT 8h→4h | 同上 |
| 正滑点/分佣是成本项：BSC 3%、Solana 10% | 我们 BSC 未设分佣，正滑点 100% 返还，暂不受影响 | 同上 |
| gang.fun V3 已上线，仍 Agent-only | 官方口径 2K+ Agent 买家 / 3K+ 笔交易；单价公式未变（0.000505 BNB ≈ $0.38） | `2026-10-28-x-digest` |
| **POA 每日帖 EV 三天从 $1.91 跌到 $0.47** | 入场 9,109→20,928→23,044，每槽 13,266→12,437→6,123 PTAH；中签率 5.49%→2.17%；PTAH $0.003241、池 $3,568 | `2026-10-29-x-digest` |
| **期现一轮真实成本 1.08%**（现货双边 1.1% 实测 + 手续费 0.22%），不是 0.22% | 买 2 颗 @1.79→卖 @1.77 亏 $0.045；永续往返 −$0.012 | `2026-10-29-pearl-inventory-hedge` |
| **收窄 0.5pp 就走 = 亏钱**；最优是收窄 **1.8/2.6/3.4pp** 三段 | 带真实成本回测：0.5/0.7/0.9 胜率 32%、后半段 −1.83pp；1.8/2.6/3.4 为 +10.35pp | `2026-10-29-pearl-inventory-hedge` |
| **高资金费全在小所**（Kraken/Lighter/Aster/Bitget），Binance/HL 自有永续被压到 ≤11% 年化 | taoli 50 行榜单：FLY 247%（$345K）、HUMA 225%（$2.3M）、4STOCK 216%（$762K）；榜首 ZIG 4380% 但量仅 $2K | `2026-10-29-pearl-inventory-hedge` |
| **Aster `PRLUSDT` $0.094 ≠ 我们的 PEARL $1.80**，Lighter 已无 PRL 市场 | 2026-10-29 复查，与 10-28 结论一致：PEARL 别去 Aster/Lighter 找空头 | `2026-10-29-pearl-inventory-hedge` |
| POA 截止是每日 **04:44 UTC（12:44 CST）**，一个窗口只算一条帖 | #35081 的 entries 只有 period 3（10/27）与 period 4（10/29 03:02Z）；10/28 那条未重复计数；wins 仍为空 | `2026-10-29-x-digest` |
| **BSC 期现成本 0.25% ≈ SafeTrade(1.26pp) 的 1/5**，模拟 6 笔全胜 +5.27U/$100 名义（0.879%/笔） | 滑点 0.002%+gas 0.15%+CEX 0.10%；但同时 2 笔未平浮亏 −0.38U，6/6 样本不足 | `2026-10-29-daily` |
| **现货盘口宽 >0.8% 时禁止平仓**（当天生效即救场） | 23:16 买一 1.76/卖一 1.79 = 宽 **1.70%**，按买一平 100 颗=白送 0.31pp | `2026-10-29-daily` |
| **自己参与的算力市场，观测速率≈自身算力，不能外推** | CROLL 预估 88 proof/min、实测 **19/min**（差 4.6 倍）；剩余 37,593/100,000 | `2026-10-29-daily` / `prediction-log` #13 |
| **币安安全事件：充提全停、承担全部损失、冻结 $2.54B→约 $3B**；初查是 **DevOps 工程师笔记本被攻陷 → 服务容器 → 未授权提币**，无钱包私钥泄露证据 | 官方 @binance 四条原帖（10/30 00:13–02:25Z）；同期本机 **BAW=UNCONNECTED、钱包地址=None** | `2026-10-30-x-digest` |
| **PTAH 24h −47.9%（$0.001689）、池只剩 $1,960；POA 每帖 EV 按现价回到 $0.42** | P4 入场 12,288（-47%）、每槽 6,066.18 PTAH；按发奖价 $0.80/帖、按现价 $0.42/帖；#35081 参与 2 次抽 0 中 | `2026-10-30-x-digest` |
| **`systemd is-active` 不是健康检查** | `exec.py` 补丁把 `mid_ok` 用在赋值前（L533/L543），22:00 起每 6 秒一条 `UnboundLocalError`（515 条），服务仍 active，进场路径全废 | `2026-10-29-daily` |
| **固定绝对阈值会把系统关死**：`entry_max_book_pct=1.0%` 今天只有 4% 的采样点满足，联合「价差≥2%」后仅 **9/620 = 1.5%** | 盘口宽中位 **1.80%**（min 0.62/max 4.56）；`exit_paused_wide_book` 732 次 + `open_abort` 33 次，实开 **0 笔**。改法：闸门取 P20 分位或按深度分批 | `2026-10-30-daily` |
| **链上腿真实换手 1.82%/单边、往返 2.2%**，是原模型 0.5pp 的 4.4 倍 | SIREN 基差 +2.52% → 实盘 **−0.32 USDT = 名义 −3.2%**；进场门槛应写 `基差 ≥ 往返成本 × 1.5`（当时=3.3%） | `2026-10-30-daily` / `bsc-bitget-first-live` |
| **账本价差推算比现金高估 $9**（24h 口径残差 −$22.05） | 18 笔 close 账本 +8.67 vs 现金 −0.5；永续现金流 −14.71（已实现 −15.63/费 −0.26/资金费 +1.18） | `2026-10-30-daily` / `pearl-cash-truth` |
| **单腿 70.8 颗裸空，买回 −$6.03**，吃掉当天全部价差收益 | 现货卖 200 颗 / 永续 IOC 只平 140；`rebalance()` 已上线（偏离 >2 颗自动对齐） | `pearl-dual-hedge-rebalance` |
| **taoli 库是「证据分层」库，不是策略库**：报价→可成交→成交→已实现净收益四层不可互换 | 作者自述收益（5.9%/200ms/30% 年化）一律标待核验，不得升级为参数 | `2026-10-30-taoli-repo-lessons` |
| **gang Flywheel V2 上线（10/31 02:48Z）：开盘后仍按池价继续 mint、Mint Guard 15/20/30 默认关、新币走 V2** | 本机 config.json 与 `/api/fair/config` 都还是 **V1 pad 0x15CFD2…**；「preflight 全绿」只证明 V1 链路通，V2 换地址就会漏单 | `2026-10-31-x-digest` |
| **PTAH 回升 $0.001919（24h +8.9%）、池 $1,682；P5 开奖 11,633 入场 / 6,027.47 PTAH 每槽 → 每帖 EV $0.50** | 估值价 $0.0021356（10/30 估值）；#35081 period 6 已登记（截止 10/31 12:44 CST），wins 仍 0/3 | `2026-10-31-x-digest` |
| **gang 官宣 Launchpad 2.0（10/31 16:12Z）：curve fee 70% 归 creator、毕业档 6/9/12/15 BNB 自选**，但 `/api/fair/config` 仍是 `version=1` / `gradPick=false` / `creatorFeeShareBps=0` | 官方毕业率 **21/1,450 = 1.45%**（3,950 .ai 钱包、9.5 万笔、9M+ GANG 烧毁）；V2 换 pad 前「preflight 全绿」仍只覆盖 V1 | `2026-11-01-x-digest` |
| **PTAH 两天腰斩：$0.0008587（24h −54.6%）、池只剩 $835**，POA 每帖 EV 按现价跌到 **≈$0.23** | 10/30 $0.001689 → 10/31 $0.001919 → 11/01 $0.000859；全链仅 1 个 PTAH 对 | `2026-11-01-x-digest` |
| **V2 `getPair=0x0` ≠ 没有池子**：TOSH 一直在 PancakeSwap **Infinity** `TOSH/WBNB 0.2%` 池里 | hook `0x45F29984…6bC8`；开盘 `soldOutAt=10-29 12:27:54Z` 即建池，池内报价币 ≈**49.7 BNB ≈ $35,180**，现价 0.000000300 BNB = 2P 的 **42.2%**；DexScreener 对该合约 `pairs: null` | `2026-10-31-daily` / prediction-log #18（已证伪） |
| **平台内记账 ≠ 链上交付**：TapeUP 页 89 页成交记录，链上 0 笔 UP 到买家 | 24,000 区块内 UP 仅 2 条 Transfer（铸造→引擎）；页面价 0.00935314 vs 链上 `price()` 0.01073208（差 **12.9%**）；页面 BEM 比引擎实持多 **3,049（≈$60k）**；引擎 163B 代理 + 单 EOA owner | `2026-10-31-daily` |
| **结论不落进 config ＝ 没做**：3.0% 门槛已证 0% 时间满足，config 仍是 3.0% | `entry_threshold=3.0`、`taker=3.4`、`max_loss_usd=12`（固定）、`spot_maker_wait_s=45`；研究建议 1.0/1.4 + 名义 2pp + 25s 未落地 | `2026-10-31-daily` |
| **联合闸门（≥1.7% 且盘口 ≤0.9%）只占全天 6.55%**：116/1,772 点 ≈ 93 分钟，瓶颈是价差不是盘口 | 盘口宽中位 **0.687%**（P25–P75 0.669–0.697）；≥1.7% 占 8.1%、≥2.5% 仅 1.0%；12–16 时占 74/144 点 | `2026-11-01-daily` |
| **平仓触发口径与真实落地差 0.47pp**：显示净 +0.53pp → 实收 0.057pp（25 颗 = $0.02） | 两笔真实 round：+0.565pp/$0.21（入场 1.65→出口 0.795）、+0.057pp/$0.02（1.96→1.613）；合计 +$0.23 | `2026-11-01-daily` / prediction #27 |
| **永续一档只吃得下 13–16.4 颗**（下 25 颗单成交 52–66%）→ 现货腿被迫 1.51→1.50 卖回，白付 0.66% | `perp_fail` 13/25、16.4/25；修法：`qty ≤ 一档量×0.8`、失败只回滚未对冲差额 | `2026-11-01-daily` |
| **打新速判：`全体可回收上限 / 募集额` < 100% 直接回避**，比看审计/叙事更早判死 | bianfenhong.fun：50 BNB 入 → 上限 **39.08 BNB = 78.16%**；开盘 9 分钟 25% 份额砸回底价，储备 40→29.79 BNB | `2026-11-01-daily` |
| **gang Launchpad 2.0 的毕业档直接改单价**：6 BNB 盘单价 **0.000606 BNB**（=6/10000×1.01），只有 15 BNB 盘的 40%；但本机 pad 仍是 V1、`gradPick=false`，换地址前别按 6 BNB 改预算 | 官方累计 **21/1,450 = 1.45% 毕业率**、3,950 .ai 钱包、95k 笔、9M+ GANG 烧毁；curve fee 70% 归 creator | `2026-11-02-x-digest` |
| **PTAH 三天 −70%（$0.001919 → $0.000859 → $0.0005698），池只剩 $673**：POA 每帖 EV 等比跌到 **≈$0.15**，Genesis 已发 ~60% 排放、Phase 3 未上线 → 打卡是成本项 | 24h 量 $11.8k / 池 $673；IAO 已退款+发币，空投 ≥5u 需手动 claim（未执行） | `2026-11-02-x-digest` |
| **本机直连 Binance API 被地域限制**（spot/fapi 均 restricted location）→ 基差二次确认必须走代理出口 | 2026-11-01 巡检实测，未走代理只能停在「研究候选」 | `2026-11-01-daily` |


## 操作参数速查（狙击器）

| 项 | 值 |
|---|---|
| 单份成本（实测） | **= 募集/10000 × 1.01**：5 BNB 盘 **0.000505**、15 BNB 盘 **0.001515**（不是常数） |
| 3 笔真实成交（10/27） | 0.002525 BNB ≈ $1.89，可撤回 0.002475 BNB ≈ $1.86（BAW `AutoReject` 卡住） |
| 撤回 selector | `0xb5c5f672 = withdraw(address,uint256,uint256)`（务必 grep 进 bytecode；`0x724b8b35` 是错的） |
| 预算闸 | 单份 ≤ 0.0016 / 总额 ≤ 0.005 / 最多 3 个仓位 |
| 轮询 | 闸门 5s、盘内 1.5s、新币索引 20s |
| 服务 | `gang-sniper.service`（用户级 systemd，崩溃自重启） |
| 钱包 | `0x532d3dE2aBE4dFBF2d2fEF42B66d888D5d34Ac2b`（BSC，BAW 托管） |
| 开闸判据 | `/api/fair/config` 的 **`enabled` 字段**（不是 HTTP 码） |

## 文件清单

### notes/（调研）
- `2026-11-02-x-digest.md` — **X 简报**：preflight 两红灯（BAW UNCONNECTED / 钱包 None）、gang Launchpad 2.0 毕业率 21/1,450=1.45% 与 6 BNB 档单价 0.000606、PTAH 三天 −70% 到 $0.0005698（池 $673、POA EV≈$0.15）、Ptah IAO 退款+空投 claim 参数（未执行）、0xDaaa「币安 63 亿」实为回顾长文
- `2026-11-01-daily.md` — **当日归档**：三条硬教训（联合闸门只占 6.55% 时间 / 平仓触发与落地差 0.47pp / 永续一档只吃 13–16.4 颗）+ 打新速判比值 + Bianfenhong 78.16% + Binance API 出口限制
- `2026-10-31-daily.md` — **当日归档**：三条硬教训（V2 getPair=0x0 ≠ 没池子 / 平台内记账 ≠ 链上交付 / 结论不落 config ＝ 没做）+ 预测 #17 对、#18 错
- `2026-10-31-pearlusdt-basis-study.md` — **价差研究**：中价中位 1.73% → 挂单口径 1.03%；门槛 1.0% 时 15 轮/1.5h、每轮 +0.7pp；逆行中位 −0.80pp、最大 −1.42pp
- `2026-10-31-pearlusdt-microstructure.md` — **微观结构**：1.6h/1000 笔，真实价差中位 1.23%、≥3.0% 占 0%；挂买一中位 7 秒成交、P90 22 秒
- `2026-10-31-taoli-groupchat-full-distillation.md` — taoli 群 465,057 条全量蒸馏：12 条教训、9 条私库缺口、3 条可改执行器（无新策略）
- `2026-10-30-daily.md` — **当日归档**：三硬教训（1.0% 固定闸门只满足 1.5% 时间、账本 +8.67 vs 现金 −0.5、链上腿换手 1.82%）+ 单腿 70.8 颗 −$6.03
- `2026-10-30-pearl-cash-truth.md` — **现金流口径**：价差收窄 ≠ 收益（收窄 1.19pp − 费 0.22 − 盘口 1.29 = −0.32pp）、entry_edge 3.61% 实为 0.21%、平仓金字塔锚 P5=0.87%
- `2026-10-30-pearl-dual-hedge-rebalance.md` — 真双边（USDT 买现货 + Entropy 空）、往返 0.218pp、单腿自动对齐、平仓 1:2:3 档
- `2026-10-30-bsc-bitget-first-live.md` — **BSC↔Bitget 首笔实盘**：SIREN 基差 2.52% → 净 −0.32 USDT；链上单边换手 1.82%、往返 2.2%
- `2026-10-30-taoli-repo-lessons.md` — taoli 私有库蒸馏：证据四层分层、两腿残差属账户、资金费限幅与公式版本
- `2026-10-30-x-digest.md` — **X 简报**：币安安全事件（DevOps 笔记本 / 充提停 / 冻结 $2.54B→$3B / BAW 掉线同期）、PTAH −47.9% 与 P4 开奖（12,288 入场、每槽 6,066、现价 EV $0.42）、gang 支持 MCP + bond mode、POA p5 已发帖
- `2026-10-31-x-digest.md` — **X 简报**：gang Flywheel V2 上线（开盘后继续按池价 mint，V1 pad 未变→假绿风险）、gang Split、Ptah 二维码登录仍停/Phase 3 将至、PTAH $0.001919 与 P5 开奖（11,633 入场 / 6,027.47 每槽 / EV $0.50）、AKAKAY 的 TRX 价差搬砖
- `2026-11-01-x-digest.md` — **X 简报**：gang Launchpad 2.0（70% fee 归 creator、毕业档 6/9/12/15）但接口仍 `version=1`、官方毕业率 21/1,450=1.45%、PTAH −54.6% 到 $0.000859（池 $835、每帖 EV≈$0.23）、Ptah IAO 测试中、AKAKAY 给出 IAO 空投 claim 参数（未执行）
- `2026-10-29-daily.md` — **当日归档**：PRL 首笔实盘 −1.34U 根因（入场哨兵被绕过）、盘口宽闸门生效、BSC 模拟 6 笔 +5.27U、CROLL 速率证伪、exec.py 未赋值 bug
- `2026-10-29-x-digest.md` — **X 简报**：POA 每日帖 EV $1.91→$0.47（入场 23,044 / 每槽 6,123 PTAH）、#35081 只进 period 3–4 且 wins 为空、gang 烧币>0.5% + CLI 回购销毁、QR 登录仍停
- `2026-10-28-daily.md` — **当日归档**：三条硬教训（钱包数门槛 / 2% 价差≠2% 收益 / 同名 ticker）+ CROLL 尾盘状态
- `2026-10-28-gang-v3-first-launches.md` — **Gang V3 首日**：4 盘打满（107–118 钱包）、我们 3 盘 0.3465 BNB、仓位闸按概率分配的改法
- `2026-10-28-pearl-perp-basis.md` — **PRL 期现**：R6 净 1.92% 但需收敛 1.26pp、PRLUSDT/PEARLUSDT 撞车、三场所资金费结构、HL oracle w_I≈0.48
- `2026-10-28-croll-gpu-mining.md` — CROLL GPU 挖矿实录（26x 内核、难度模型、11 笔 $1.71 净价值≈0）
- `2026-10-28-zhijiu-teardown.md` — 九(zhijiu) 0.6BNB 打法拆解
- `2026-10-28-winner-profile.md` — 赢家画像：秒进/小仓/早卖
- `2026-10-28-x-digest.md` — **当日 X 简报**：Ptah 关网页登录(只能 Agent)、gang V3 上线(2K+买家/3K+笔)、35,645 POA SBT、preflight 全绿
- `2026-10-27-daily.md` — **当日归档**：闸门判据(404→200)、2,236 次轮询 0 成交、Codex 重置基础率 30%、TG 钉 IP
- `2026-10-27-agent-wallet.md` — Agentic Wallet 三类赚钱出口（mint / 发射台 / 自动化），附案例
- `2026-10-27-agent-landscape.md` — 6 个 Agent 专属平台地图：成本、上限、入口、状态
- `2026-10-27-ezbot-teardown.md` — 拆 @0xquqi 的开源工作台；Gang 双索引 API + 三个市场合约
- `2026-10-27-earnings-evidence.md` — **有账可查 vs 口号**：Ptah 4 枚净赚 40.96U 的完整流水
- `2026-10-27-free-mint-reality.md` — **反例**：89 枚免费 NFT 只值 1.48U；三条判别标准
- `2026-10-27-gang-liquidity.md` — **链上实测**：Gang 全站 61 个代币的成交量分布
- `method-evidence-first.md` — 方法论：信源分级、四格单元、反向搜索、自洽校验

### playbooks/（可执行）
- `zero-cost-agent-tasks.md` — 零成本任务清单（POA / agentka / Coracle）
- `prediction-log.md` — **预测日志**：所有结论先落可证伪预测，事后回填
- `eval-set.md` — **评估集 13 题**：改完规则跑一遍，低于 8/10 回滚（E11–E13 是 10/27 实战教训）
- `skip-rules.md` — **不看清单**：三层过滤（配置 / 判据 / 红灯）
- `gang-fairmint-flow.md` — **跑通过的完整下单链路**：pad/router 地址、selector、单价公式、成交对账、撤回
- `_TEMPLATE.md` — 打法模板（成本表 / 步骤 / 实测结果）

### raw/（原始数据）
- `*.jsonl` — X 抓取原文、搜索结果，可回溯

## 使用约定

1. 新会话：先读本文件 → 再看相关笔记 → 需要细节才打开原文
2. 新结论：写进 notes/ 或 playbooks/，并在本文件的表格里加一行
3. 改规则：同步更新 `eval-set.md`
4. 所有预测：进 `prediction-log.md`
- notes/2026-11-01-external-lessons-delta-neutral.md — 外部经验：做市复盘 unexplained gap / BIS carry / Leung-Li 最优进出场，及我们对应的代码改动
- playbooks/spot-perp-spread-execution.md §29 — 口径三坑：可成交价公式（买一 vs 卖一差 0.7–1.3pp）、权益必须用 portfolio 端点、fundingHistory 不是逐小时实收
