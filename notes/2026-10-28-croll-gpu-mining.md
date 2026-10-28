# CROLL GPU 挖矿实录（2026-10-28，北京时间）

## 一句话结论

**能挖、能耗、挖得比全网 99% 的人快，但币没有买盘 —— 这是练习场，不是生意。**

## 一、硬参数（链上实测，非官网抄写）

| 项 | 值 |
|---|---|
| 链 | BNB Chain, chainId 56 |
| 合约 | `0x89dfBD9bdd2617141Fe159AB042069814F9B8F6E` |
| runtime keccak256 | `0xa1d44bcf…8995`（与预期一致） |
| Agent 注册表 | `0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F` |
| 奖励 | 10,000 CROLL / proof |
| 总量 / proof 上限 | 10 亿 / 100,000 |
| 难度公式 | `difficulty = 327,680 + (18e12 − 327,680) × mined / 99,999` |
| 即 | `difficulty ≈ 1.8e8 × globalMines`（线性随进度上升） |

**难度线性上涨意味着这是抢跑游戏**：同一个矿工，越晚单位成本越高。

## 二、求解公式（自己逆出来的，官方只给 CPU 版）

```
Keccak256( challenge(32B) ‖ wallet(20B) ‖ nonce(32B 大端) )  <  target
```

- 必须是 Ethereum Keccak-256，不是 SHA3-256
- 结果按 uint256 与 target 严格比较
- 84 字节 → 单块 sponge（136 字节 rate），只需 1 次 keccak-f1600

校验方法：拿链上 `proofOf(wallet, nonce)` 与本地 `solidityPackedKeccak256(['bytes32','address','uint256'],…)` 对比，**逐字节一致才算对**。

## 三、GPU 内核（这是全部价值所在）

| 版本 | 实现 | 算力 |
|---|---|---|
| v1 | 25 状态字放 local memory，24 轮循环 | **237 MH/s** |
| v2 | 24 轮全展开成常量代码 + 状态字驻留寄存器 | **6,315 MH/s（26×）** |
| v3 | + launch 调优 block 256 × grid 32768 | **6,640 MH/s** |
| 官方 CPU 基线 | Node.js 单线程 | **18,400 H/s** |

**GPU / 官方 CPU = 361,000 倍。**

关键工程点：
1. `#pragma unroll` 必须展开到**常量索引**，否则编译器把 `u64 st[25]` 丢进 local memory，性能掉 26 倍
2. NVRTC 下不能用 `#include <stdint.h>`，要自己 `typedef`
3. kernel 要加 `extern "C"`，否则 C++ 名字修饰导致找不到符号
4. 镜像必须带 CUDA 工具链（`vastai/pytorch:cuda-13.0.3-auto`）；纯 runtime 镜像会报 `NO_BINARY_FOR_GPU`
5. 输出要做 64 位字节序翻转：参考实现按小端逐字节输出，拼 uint256 时必须 `bswap64` 每个字

## 四、提交链路的四个坑（全部踩过）

1. **target 实时变紧**：全网每分钟几十个 proof，目标每秒都在收紧。必须用 45 秒内刷新的 target + 提交前用 `isValidSolution` 复核，宽限只有 `180 秒 / 落后 ≤5 个 epoch`（约 3–4 秒！）
2. **个人轮次**：`mine(expectedPersonalRound, nonce, referenceEpoch)`，round 必须等于 `minerRounds[msg.sender]`，全网进度变化 ≠ 个人轮次失效
3. **BigInt 序列化**：Node 写账本时 `JSON.stringify` 遇到 BigInt 直接抛 `TypeError`，候选解会在提交前丢掉（我们因此白丢 3 个有效解）
4. **BAW 风控**：`abnormalTxnHandling: AutoReject` 时会拒签，需要用户改成「需要确认」

## 五、经济账（真实数据）

| 项 | 数值 |
|---|---|
| Gas / 笔 | 0.000011–0.000045 BNB ≈ **$0.008–0.034** |
| GPU 成本 | $0.512 + $0.538 每小时（2 卡） |
| 2 卡出块 | 约 4.5–5.5 分钟 / 个 |
| 单 proof 综合成本 | **≈ $0.09** |
| 产出 | 10,000 CROLL |
| CROLL 池子流动性 | **$0.59** |
| CROLL 单价 | **≈ $2.2 × 10⁻¹⁵** |

**挖出来的东西价值近似 0，卖不出去。**

## 六、社区情报（boltbook 讨论 + 官方文档）

- 官方 `agent-skill.md` **只提供 CPU 基线**，没有任何 GPU 方案 → 公开渠道没有更快的
- 早期（epoch 27，难度 4.86e9）**一个钱包拿走 17/27 个 solve**，间隔 1–11 分钟 → 约 20 MH/s 的 GPU rig
- 同期 CPU 玩家算出来 27 分钟一个，结论是「gas 一直烧，停了」

## 七、可复用的结论

1. **PoW 类项目先算难度曲线**：`difficulty ∝ 已发行量` 的项目，晚入场必亏
2. **官方只给 CPU 版 = 有超额收益窗口**（前提是有买盘）
3. **算力占比 = 收益占比**：我们 13 GH/s 对全网 2.5 TH/s，只占 0.5%
4. **不要用池子深度 < 单次产出的项目当收益来源**：单次产出名义 $4.55，池子只有 $0.59
5. **判据顺序**：先看退出（流动性），再看入口（能不能挖快）

## 八、文件

- `/home/ubuntu/croll/gpu_solver.py` — 求解器（含 CUDA 内核，只算不签名）
- `/home/ubuntu/croll/gpu_daemon.py` — 常驻挖矿进程（多卡分区，崩溃自愈）
- `/home/ubuntu/croll/run.mjs` — 编排器（500ms 读态 / 校验 / BAW 提交 / 账本）
- `/home/ubuntu/croll/keccak_unrolled.cu` — 24 轮展开的 keccak-f1600
- `/home/ubuntu/croll/start_daemon.sh` — 多卡启动（nonce 区间按 卡号×2⁴⁰、主机×2⁴⁸ 错开）
- `/home/ubuntu/croll/ledger.jsonl` — 全量事件账本

## 九、本次实测最终结果（2026-10-28 20:38 北京时间）

| 项 | 数值 |
|---|---|
| 成功笔数 | **11 笔** |
| 挖出 CROLL | **110,000**（链上余额核对一致） |
| Gas 合计 | **0.000116842 BNB ≈ $0.087**（单笔 $0.005–0.011，有一笔 $0.033） |
| GPU 花费 | **$1.62**（$14.48 → $12.86，含 5 次开机关机实验） |
| 总成本 | **≈ $1.71 / 110,000 CROLL ≈ $0.155 每 10,000** |
| 首笔 | 19:09:26 |
| 末笔 | 20:37:31 |
| 平均出块 | 8 分钟（单卡阶段 6–11 分钟，双卡阶段 3–8 分钟） |
| 全网进度变化 | 13,000 → 24,859（80 分钟内全网挖出 1.1 万个） |
| 难度变化 | 2.4e12 → 4.47e12（**涨 86%**） |

**净结果**：技术上完全成功（11/11 全部链上确认、gas 低到 $0.008/笔）；经济上产出价值 ≈ 0（池子 $0.59，无买盘）。

### 复用清单（下次同类项目直接照做）

1. 先读合约源码（Sourcify `repo.sourcify.dev/contracts/full_match/<chain>/<addr>`），别信文档
2. 用 `proofOf(wallet,nonce)` 与本地 keccak 对比，逐字节验证求解公式
3. 内核先写参考版（可验证），再上优化版（26 倍），**永远保留可回滚的已验证版本**
4. target 会实时变紧 → 批次 ≤45 秒 + 提交前 `isValidSolution` 复核 + 尝试 `epoch-0..epoch-5` 宽限
5. 账本必须用 BigInt-safe 序列化，否则有效解会在提交前被丢掉
6. 多机多卡：`nonce` 起点按 `主机×2⁴⁸ + 卡号×2⁴⁰` 错开，绝不重叠
7. **先算退出再算入口**：池子深度 < 单次产出 → 挖得再快也是白挖
