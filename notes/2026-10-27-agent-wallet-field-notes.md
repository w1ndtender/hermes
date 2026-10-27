# 近两天 Agent Wallet 一手情报（2026-10-26 ~ 10-27）

来源：X 搜索（已登录 @SauravY79514198，住宅 IP）。原文链接全部保留。

## 1. PTAH POA 免费卡 + 每日抽奖（当前最确定的零成本机会）

**原文**：@vkf1785187 https://x.com/vkf1785187/status/2115030752597581858

> POA 是 Ptah 推出的灵魂绑定卡，每个 Binance Agent ID 可以免费领一张。每天发帖就能参加当天的 PTAH 抽奖，共 15 场，10 月 26 日到 11 月 9 日。
> 第二步：打开 ptah.trade/poa，连接钱包，点铸造。BNB Chain 上只需少量 gas，不需要授权代币。
> 第三步：在 X 或币安广场发帖，必须带 `#ProofOfAgent` + 你的 Agent #。
> 每天 UTC 04:44（北京 12:44）开奖。当天帖子里选 500 张卡，平分当天奖池；不足 500 张则所有人平分。PTAH 直接空投到持卡钱包，不用领取。
> 每天以 UTC 04:44 为界，昨天的帖子不算今天。同一天发多条不增加名额。同一张卡不同天可重复中奖，同一天最多一次。
> 铸造截止 11 月 8 日 UTC 04:44。

**官方页**：https://ptah.trade/poa （"one free, soulbound card per Binance Agent ID"）

**关键数字**（第三方转述，待自验）：
- 每日奖池 ≈ 14,000 U，最多 500 人分 → 人均 ≈ 28 U
- 上一期 Relics：人均 40–80 U（@monkey_7788）

**成本**：仅 gas（BSC 一笔 ≈ $0.02–0.05），无授权、无付费。

## 2. 效率派做法：绕开对话，直接调 CLI

**原文**：@0xAllBuy https://x.com/0xAllBuy/status/2115101490155327952

> 当我已经知道要买哪个币、买多少时……如果每次都要和 AI 聊天，等它理解需求、组织参数、调用工具，整个过程就显得太长了。
> 关键在于，Binance Agentic Wallet 已经提供了可以被程序调用的交易能力……可以把 AI 每次在聊天中组织的操作，提前写成固定逻辑，再给它加一个界面。
> 交易执行路径不再需要大模型逐笔理解自然语言。AI 的工作集中在开发阶段。
> 我保留了报价有效期、合约风险检查、钱包状态校验和重复提交保护。出现提交超时、结果不明确时，程序会暂停新下单。
> 操作变快和链上成交变快是两个指标。预览报价不会锁定最终成交价格。

**这条印证了我们 sniper 的路线**（固定逻辑 + CLI，不经模型），也提醒：成交速度受币安接口/路由/网络限制，不是脚本能决定的。

## 3. 平台限制必须逐项确认

**原文**：@Naive_BNB https://x.com/Naive_BNB/status/2115093997555417236

> 1 登录时长：默认 2 天，高强度交互建议延长；每 48 小时必须有交互，否则自动登出。
> 2 交易权限：可交易代币要设成"全部代币"，否则打不了内盘 meme。
> 3 开发者模式：多数场景需要开启。

**再次印证**：会话 48h 自动过期是常态，不是异常（我们这次撞上的就是这条 + 币安全局掉线）。

## 4. 社区共识的痛点

**原文**：@AKAKAY04 https://x.com/AKAKAY04/status/2115102649238622321

> Binance Agentic Wallet really needs to launch the "Always Allow" option as soon as possible. Automated workflows are constantly getting interrupted.

同一账号 1 小时前：`币安 AI 钱包刚刚强制掉线，所有人都被踢出来了`（2026-10-27 ~21:30）。
→ 我们那次 `UNCONNECTED` 不只是 48h 到期，还叠加了平台侧全局断开。

## 5. 生态信号

- @neroxca：`Claimed my Proof of Agent Agent #34946 … Minted by my AI agent with Binance Agentic Wallet`（POA 已经在被批量领）
- @CXNIAO：`这个 Agent ID 以后就是我的 agent 在链上的身份证了 … 让它替我盯盘、打新、跑腿`
- @ling65697_z 热榜：PTAH 主打 Fair for All；GANG 是 agent 专属发射台，单钱包上限 1%，毕业后进 Pancake，LP 烧掉，"follow a thought" 可跟某个 agent 的下单

## 我的结论

1. **短期最值**：POA 免费卡 + 每日发帖，成本≈0，每天一次抽奖机会，持续到 11-9。这是当下唯一"投入 5 分钟、期望值正"的动作。
2. **我们的 sniper 路线被社区验证**：固定逻辑调 CLI 是对的，但**速度和成交不受我们控制**，别把期望压在"抢得比人快"。
3. **会话过期是常态**：48h 一续，且平台会强制踢人 → 必须每轮检查 + 提前刷新，不能假设一直在线。
4. **fair mint 不是利润来源**：Gang 内盘 59% 零成交（61 个代币实测），打进去也是"能买不能卖"。权重下调，只当小样验证。

## 待办

- [ ] mint POA 卡（gas ≈ $0.03），拿到 Agent #
- [ ] 每天 12:44 前发一条带 `#ProofOfAgent` + Agent # 的帖子（可写入 cron）
- [ ] 记录每日期望值 vs 实际中奖，7 天后复盘
