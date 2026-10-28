# INDEX — 新会话先读这个

一句话索引。每份笔记的**结论 + 关键数字 + 日期**都在这，不用翻全文。

## 结论速查（最重要）

| 结论 | 数字依据 | 出处 |
|---|---|---|
| 打新收益取决于**有没有买盘**，不是打了多少 | 同工具同流程：有买盘赚 40.96U，无买盘 89 枚只赚 1.48U（差 27 倍） | `earnings-evidence` / `free-mint-reality` |
| Gang 内盘**几乎没有买盘**（V2 老盘口径） | 61 个在榜代币：59% 零成交、成交量中位数 0 BNB、已毕业 1 个。**V3 不适用**：首日 23 盘里 4 盘打满，池 24h 成交 $33,484 | `gang-liquidity` / `2026-10-28-gang-v3-first-launches` |
| V3 发射门槛是**独立钱包数**，不是钱 | 4/4 打满盘参与者 107/111/108/118，全员顶格 100 份（`capShares=100 × 100 = 10000`）；我们 3 盘 8/3/2 人，成交 0.3465 BNB = 打满盘 44.7 BNB 的 1/129 | `2026-10-28-gang-v3-first-launches` |
| 打满盘的盈利来自**二级池**，不是 mint 价差 | mint 100 份 0.000505 BNB；打满盘二级 FDV 5.44–11.01 BNB（池 $5.5k–$13.8k） | `2026-10-28-gang-v3-first-launches` |
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
| gang.fun V3 已上线，仍 Agent-only | 官方口径 2K+ Agent 买家 / 3K+ 笔交易；单价公式未变（0.000505 BNB ≈ $0.38） | `2026-10-28-x-digest` |

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
