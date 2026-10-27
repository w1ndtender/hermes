# Gang fair mint：一条跑通过的真实链路（2026-10-27 实战）

只写**实测跑通**的部分。每一步后面是当时的返回值，不是推测。

## 0. 固定参数（BSC 主网，当日）

| 项 | 值 |
|---|---|
| Launchpad（pad+router 合并同一个地址） | `0x15CFD2dc8278Fb87a1783ef42111618E20874365` |
| Router（`mintFor` 走这里） | `0xE040445690Aa56C8b68B7f7038C7b2562B5079C4`（必须 `getAddress()` 归一，否则 `bad address checksum`） |
| `mintFor` selector | `0xf8a28d71` |
| `withdraw` selector | `0xb5c5f672 = withdraw(address,uint256,uint256)`（**不是** `0x724b8b35`） |
| `previewWithdraw` selector | `0xe3537a5e` |
| `Minted` 事件 topic | `0xff1b99c8afce899f46662ffc7045877162dd660b4cacca896efb18ce5e64c3fa` |
| `Withdrawn` 事件 topic | `0xbe561b8cf046c475f2…`（前缀匹配即可） |
| 可用的 BSC RPC | `https://rpc.48.club`（`eth_getLogs` 单次 ≤ 4900 块）、`https://bsc-dataseed.bnbchain.org`（会 `limit exceeded`） |

## 1. 单价（必须先算对，否则闸门全错）

```
sharePrice = raiseBnb / totalShares(10000)
need       = sharePrice * (1 + mintFeeBps/10000)
```

实测两档：5 BNB 盘 `0.000505`、15 BNB 盘 `0.001515`。**没有常数。**

## 2. 下单前

```bash
python3 /home/ubuntu/gang-sniper/preflight.py   # 六项全绿才开 auto
```
六项：gate `enabled` / BAW `CONNECTED` / pad+router 都有 / 交易锁 `UNLOCKED` / 真实盘路由模拟过 / 预算闸。

## 3. 下单

```
calldata = 0xf8a28d71 | token(32B) | shares(32B) | minShares(32B) | deadline(32B)
baw contract-call preview --binanceChainId 56 --from <W> --to <ROUTER> --value <need> --inputData <calldata>
baw contract-call execute --requestId <preview.data.requestId>
```
`preview` 返回 `simulationResult.balanceChanges`，ERC20 +50000e18 / native −505000000000000 就是对的。

## 4. 成交确认（唯一可信的来源）

```python
eth_getLogs(fromBlock=head-4900, toBlock=head, address=PAD, topics=[MINTED_TOPIC])
# 过滤 topics[2] == 钱包；data = shares, cost, fee, userShares, sold
```
或 `GET https://gang.fun/api/fair/sales/<token>/position/<wallet>` → `shares` / `sellBackAll`。

**不要看 sniper.log 的 `sale ok:true`**：那是 `analyze()` 在打之前写的计划日志（`sniper.py:312`），10/27 出现 6 条 `ok:true` 而链上只 3 条。

## 5. 出场（撤回）

```
previewWithdraw(token, user, shares) -> (payout, fee)     # 只读，先算钱
withdraw(token, shares, minPayout)                        # minPayout 填 payout*0.99
```
退出费 1%（超过 `STALE_AFTER` 无进展则 0）。**minting 阶段没有池，只能撤回不能卖。**

坑：BAW `wallet settings` 里 `abnormalTxnHandling: AutoReject` 会让撤回直接 `351803 Transaction risk is too high: blocked`（不是链上 revert，改 calldata 无用）。要先在币安 App → 钱包 → Agentic Wallet → 设置 → 异常交易处理 → 改「需要确认」。

## 6. 事后对账（每天一遍，30 秒）

1. `sale ok:true` 条数 == `Minted` 条数？不等就是假成功。
2. `state.fired` 里每条都有 `res`（tx hash）？没有就是没发。
3. `getLogs` 按钱包过滤的 cost+fee 合计 == 预期花费？
