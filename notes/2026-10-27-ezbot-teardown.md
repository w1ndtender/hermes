# EZbot 拆解：别人的 Agent 工作台怎么做的

对象：`github.com/0xquqi/EZbot-agentic-wallet`（MIT，作者 @0xquqi，X 长文 352K 浏览）
价值：这是目前公开最完整的「Agent ID 内盘工作台」，把我们要做的事拆成了可复用的模块。

## 一、它覆盖什么

- **多账号钱包管理**：每个账号独立 Profile、独立钥匙串标识、备注、扫码登录、状态识别
- **三平台内盘聚合**：Four.meme `OpenFour AgentIdExclusive`、**Gang.fun**、Flap Agent Curve（Genius 待接入）
- **项目铸造**：贴 URL / 原文 / 合约 → 自动提取指南、前端线索、铸造路径 → 源码、安全、费用三项报告 → 再报价、模拟、预览
- **高级合约调用**：手填 calldata，先模拟再确认
- **交易记录**：按编号核对，**不自动重发**

设计原则：预览、提交、成交核对三步分离；真实交易必须人工确认；不扩大为无限额度授权。

## 二、能直接拿来用的东西（重点）

### 1. Gang 的两个行情索引（我们狙击器可以用）

```
https://gang.fun/api/tokens?sort=new&limit=50&offset=0
https://gang.fun/api/stocks/tokens?limit=50&offset=0
```

2026-10-27 实测均可用：返回 `items[]`，字段含 `address / createdAt / createdTx / graduated / progressPct / raisedBnb / soldTokens / priceBnb / holders / quoteSymbol`，另有 `hasMore`、`nextOffset` 分页。

→ **比只盯 `/api/fair/config` 多一条发现路径**：V3 开盘后新盘会先在 `sort=new` 里出现。

### 2. 三个已核验的内盘市场合约（BSC）

| 市场 | 地址 | 类型 |
|---|---|---|
| 市场 A | `0x315ba2e8952d06094cc636b2b84229fa32fb23a7` | BNB 报价 |
| 市场 B | `0x1b8f3f69dfa0a7f63d308c7eb0fd38d8b099966e` | 多报价币 |
| 市场 C | `0xf81c4e51c48466c6025b0165b1ea0f6978c712cb` | 多报价币 |

调用方式：
- `curves(address)` → 判断某代币属于哪个市场、是否毕业
- `isAgent(address)` → 判断某个钱包是否有 Agent ID 资格（**下单前预检，能省掉一次失败交易**）

### 3. 官方 Skill 清单（做工具前先读）

`binance-agentic-wallet`、`meme-rush`（扫 OpenFour Agent 内盘）、`query-token-info`、`query-token-audit`、`query-address-info`

## 三、它的判断，和我们一致的 / 不一致的

**一致**
- 打新 = 新时代撸毛：不花钱的、或花钱但有明确套利空间的，都去参与
- 多账号是普通人唯一能拉开差距的资源
- 必须程序化盯盘，人手动跟不上

**不一致（我们不采纳）**
- 它整套是 macOS + Python 桌面工作台，人工确认每一步 → 只适合手动玩，**不适合抢开盘**
- 它不做无人值守交易（作者明确写「没有无人值守交易」）

→ 结论：**它的发现层和预检逻辑值得抄，交易层不要抄**（我们已经有 BAW + 原生 calldata 的自动路径）。

## 四、对我们的具体改进（待实施，不花钱）

1. **双源发现**：狙击器除了扫 `/api/fair/*`，再加 `/api/tokens?sort=new` 轮询，任意一边出现新盘就触发
2. **下单前 isAgent 预检**：命中市场合约后先读 `isAgent(wallet)`，不合格直接跳过，不浪费 gas
3. **市场路由校验**：拿到代币地址后调三个市场的 `curves(address)`，命中哪个走哪个，避免打错市场
4. **失败不重发**：一次 mint 失败只记录不重试，防止双花式重复扣费

## 五、源码位置（本地）

克隆在 `/home/ubuntu/.hermes/cache/scratch/ezb`（浅克隆），关键文件：
- `desk/gang.py` —— 分页与截断逻辑
- `desk/discovery.py` —— 发现流程
- `docs/gang-discovery-review.md` —— 核验记录（本文数据来源）
- `docs/gang-discovery-sample.json` —— 50 项样本读数
