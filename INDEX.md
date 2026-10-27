# INDEX — 新会话先读这个

一句话索引。每份笔记的**结论 + 关键数字 + 日期**都在这，不用翻全文。

## 结论速查（最重要）

| 结论 | 数字依据 | 出处 |
|---|---|---|
| 打新收益取决于**有没有买盘**，不是打了多少 | 同工具同流程：有买盘赚 40.96U，无买盘 89 枚只赚 1.48U（差 27 倍） | `earnings-evidence` / `free-mint-reality` |
| Gang 内盘**几乎没有买盘** | 61 个在榜代币：59% 零成交、成交量中位数 0 BNB、已毕业 1 个 | `gang-liquidity` |
| 「人均 XX 刀」类说法不可信 | $50/day 被标注 unverified，原 mint 已结束 | `earnings-evidence` |
| 免费 mint 要过三问 | 有二级市场 / 地板 > 2 倍成本 / 供给有上限 | `free-mint-reality` |
| V3 铭文打新：开盘价=打新价 | 但因无买盘，等于"能买不能卖" | `agent-landscape` |
| Codex 重置不可预测 | 68 次重置、平均 6.0 天、最长 67.7 天；过去 60 天「48h 内重置」基础命中率 30% | `2026-10-27-daily` |
| 判开盘看 `enabled` 字段，不看 HTTP 码 | 同日 404 → 200 `{"enabled":false}`；4h11m 轮询 2,236 次全 gate_closed、真实成交 0 | `2026-10-27-daily` |

## 文件清单

### notes/（调研）
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
- `eval-set.md` — **评估集 10 题**：改完规则跑一遍，低于 8/10 回滚
- `_TEMPLATE.md` — 打法模板（成本表 / 步骤 / 实测结果）

### raw/（原始数据）
- `*.jsonl` — X 抓取原文、搜索结果，可回溯

## 使用约定

1. 新会话：先读本文件 → 再看相关笔记 → 需要细节才打开原文
2. 新结论：写进 notes/ 或 playbooks/，并在本文件的表格里加一行
3. 改规则：同步更新 `eval-set.md`
4. 所有预测：进 `prediction-log.md`
