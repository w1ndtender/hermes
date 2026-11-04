# 任务书 01：统一价差口径（`core/pricing.py`）

> 交给 Codex。**这是唯一允许计算价差的地方**，其余脚本一律调用它。
> 不允许在这次提交里调整任何阈值或策略参数。

---

## 目标

把现在散在 3 个地方的价差公式收敛成一个纯函数模块，并保证「输入错、数据缺、订单一腿」时**抛错而不是给一个看起来正常的数**。

现状：
- `edge.py` —— 只被 `spread_alert.py` 用
- `exec.py: edge_of() / close_edge_of() / edge_maker()` —— 被执行器用
- `spread_alert.py` 曾经自己算过一份（已改调 edge.py，但函数还在）

三份口径已经出现过不一致（报警用标记价算出 2.07%，执行器用盘口算出 0.34%）。

---

## 接口（必须完全照这个签名，不许改名）

```python
# core/pricing.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Book:
    spot_bid: float
    spot_ask: float
    perp_bid: float
    perp_ask: float
    spot_bid_sz: float
    spot_ask_sz: float
    perp_bid_sz: float
    perp_ask_sz: float
    ts_spot: float      # 毫秒时间戳，数据产生的时刻
    ts_perp: float
    venue_spot: str
    venue_perp: str

def entry_edge_pct(b: Book) -> float:      # 开仓：（永续买一 − 现货卖一）/ 现货卖一 × 100
def exit_edge_pct(b: Book) -> float:       # 平仓：（永续卖一 − 现货买一）/ 现货买一 × 100
def net_after_cost(b: Book, cost_pct: float, side: str) -> float   # side ∈ {"entry","exit"}
def fillable_qty(b: Book, max_notional: float, step: float = 0.0, min_notional: float = 10.0, slippage_bps: float = 10) -> float
    # step = 该交易对的最小数量单位（由调用方从场所 meta 取，见下）
    # min_notional = 场所最小名义金额
def validate(b: Book, max_age_ms: int = 3000) -> None   # 不合法直接抛异常
```

---

## 必须处理的 18 种情况（每条都要有测试）

**数据完整性**
1. 任一价格 ≤ 0 → `ValueError`
2. 盘口倒挂（spot_bid > spot_ask）→ `ValueError`
3. 现货与永续数据时间差 > 3000ms → `StaleDataError`
4. `ts` 在未来（服务器时钟漂移）→ `StaleDataError`
5. 深度为 0（只有价没有量）→ `ValueError`

**量级/身份**
6. 永续价与现货价量级差 > 3 倍 → `SymbolMismatchError`（同名不同币：ARIA 0.00683 vs 0.1174）
7. 标的价格被当成买一传入（调用方误用）→ 无法自动识别，但**文档必须写明**：只接受 `bid/ask`，不接受 `mark/index`

**方向**
8. `entry_edge_pct` 为负（永续比现货便宜）→ 正常返回负数，**不许取绝对值**
9. 有人误把 `exit_edge_pct` 的值当开仓用 → 通过不同函数名隔离，测试断言两者在同一盘口下不同

**成本**
10. `cost_pct` 为负 → `ValueError`
11. `net_after_cost` 在 `entry` / `exit` 两个方向用同一份成本，但**测试要证明**成本只扣一次

**数量**
12. `fillable_qty` 受 4 个上限约束：现货卖一量、永续买一量、`max_notional`、交易对最小步长（向下取整）
13. 任一上限为 0 → 返回 0（不是抛错，是「吃不下」）
14. 步长取整后为 0 → 返回 0

**并发/副作用**
15. 函数必须是纯函数：同样输入两次，结果完全一致（无内部缓存、无读文件）
16. 不许 import `requests` / `urllib` / `ccxt` / 任何网络库

**边界数值**
17. 价格差 1e-9 级别的浮点误差不得导致 sign 翻转（用 1e-12 容差判断正负）
18. 极端值：价格 1e-8 和 1e8 都能正确计算，不溢出

---

## 验收命令（必须能跑通）

```bash
cd ~/spread && .venv/bin/python -m pytest tests/test_pricing.py -v
```

必须看到：
- 上述 18 条各至少 1 个用例
- 覆盖率 ≥ 90%：`pytest --cov=core/pricing --cov-fail-under=90`
- 全部通过，0 skip

另外提供一条**对比命令**，证明三个旧实现与新实现结果一致（容差 0.01pp）：

```bash
cd ~/spread && .venv/bin/python tools/compare_edge.py --fix 1.45 --perp-bid 1.4642
# 期望：entry_edge = +0.9793%（三个旧实现 + 新实现一致）
```

---

## 不许动

- 不改 `config.json` 任何值
- 不改 `hedger.py` 的交易逻辑，只允许把 `edge_of()` 的实现换成调用 `pricing.entry_edge_pct`
- 不引入 pandas / numpy 之外的新依赖；能不用外部库就不用
- 不删除旧函数（先保留一个版本周期，标 `@deprecated`）

---

## 回滚

单文件改动 + 函数改名，回滚 = `git revert` 一次提交。
`core/pricing.py` 若被删，旧代码仍可运行（因为旧函数保留）。

---

## 提交要求

一个 PR 只做这一件事。PR 描述必须写：

| 项目 | 内容 |
|---|---|
| 改了什么口径 | 无（口径不变，只是收敛实现） |
| 旧值 | 报警曾用标记价 1.4085 → 2.07% |
| 新值 | 统一用买一 1.3847 → +0.34% |
| 证明 | `tests/test_pricing.py::test_mark_price_rejected` |

---

## 给 Codex 的讨论点（需在 PR 描述里逐条回答，不许沉默实现）

**问 1：`fillable_qty` 的滑点模型？**
已查官方规则，约束来自场所而非模型，按下面事实实现：
- Hyperliquid 永续：最小名义 **$10**（`Order must have minimum value of $10.`）；数量小数位由 `meta` 里每资产的 `szDecimals` 决定；价格最多 5 位有效数字、且小数位 ≤ `6 - szDecimals`（现货为 `8 - szDecimals`）。
- 所以 `step` 由调用方传入（`10^-szDecimals`），本函数不猜。
- 滑点：默认 `slippage_bps=10`，即按「卖一价 × (1 − 10bps)」折价后计算名义；不需要深度曲线，因为 `Book` 只有一档。

**问 2：`Book` 是否带 `source`？**
要。加 `source_spot: str` / `source_perp: str`（例如 `"hl:io"`、`"safetrade"`），出问题能追到接口。

**问 3：3000ms 时效是否按场所区分？**
区分。`validate()` 接受 `max_age_ms` 由调用方传；默认值保持 3000，但 SafeTrade 腿的建议值是 8000（页面刷新慢），HL 腿 2000。具体阈值不在本函数硬编码。

**问 4：同名不同币 3 倍阈值改成历史分布？**
保持 3 倍固定值（本任务不做历史分布），但函数要把触发值返回给调用方，便于以后改判据。历史分布判定放到 `tasks/task-05-symbol-identity.md`，不在本任务范围。

来源：Hyperliquid 官方 tick-and-lot-size 文档、exchange endpoint 报错样例（`Order must have minimum value of $10.`）。
