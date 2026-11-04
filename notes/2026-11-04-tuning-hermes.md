# 别人怎么调教 Hermes：能用的挑出来（2026-11-04）

来源：官方 docs（tips / use-soul / memory / troubleshooting-agent-quality）、
Neogen「生产环境一个月」复盘、Reddit 多 profile 车队帖、DEV 三个月教训、知乎 7 万字中文教程。
只记对我们这套（TG 单会话 + 交易自动化 + 代码交 Codex）有用的。

## 一、五条立刻能用

### 1. SOUL.md 只放「怎么说话」，不放「项目规矩」
官方原文划得很清：SOUL 管 tone / personality / 怎么处理不确定和分歧；
**file paths、commands、ports、workflow 全部属于 `AGENTS.md`**。
判断标准一句话：到处都适用的进 SOUL，只属于某个目录的进 AGENTS。

我们的问题：把「价差口径、推送规则、目录路径」写进了 SOUL —— 属于放错层。
改法：SOUL 保留身份与语气（直白、不吹、认错认具体），规则挪进 `~/spread/AGENTS.md`（已建）。

### 2. 改完 SOUL / 记忆，必须新会话才生效
记忆与系统提示是**会话开始时冻结的快照**。Telegram 的一个聊天是一个长会话，
机器重启都不算结束。所以：改完配置 → `/new` 或重启 gateway，否则改动不生效。

这条解释了我们之前「明明写进 memory 了但它还是老样子」。

### 3. cron 必须钉模型，否则换 provider 静默失败
生产复盘原话：每个 cron job 都要 model-pinned，不然供应商一换，任务静默死掉，
**连报错都没有**。我们的 `peer-digest`、`chain-scan`、`kill-switch` 要逐个确认钉了模型。

### 4. 每个静默失败都要有计数器
他们踩的是「六天静默停机」。我们的版本：接口挂了当没有数据、`except: pass`、
`eth_getLogs` 返回空当没交易 —— 没人知道发生过。
最小做法：每个任务结束写一行 `{任务, 时间, 成功/失败, 条数}` 到统一 log，
一天一条汇总，只有异常才推。

### 5. 钱和不可逆动作放在闸后面
他们把 17 类动作放在一次性验证码后面。我们的对应物：`STOP` 文件 + 亏损平仓先问 +
真实下单要 `dry_run:false` 且当次点头。这条方向是对的，保持不变。

## 二、值得抄的做法

- **配置进 git**：每次改 SOUL / config / skills 都 commit，改坏了能回滚。`~/.hermes` 目前没进版本管理。
- **量化验收用脚本，不让模型自评**：他们的原话是「别让 LLM 判你的量化指标，脚本更快更稳」——这正是 `tests_edge.py` 该干的事。
- **skill 会长胖**：官方也说 skill 越写越长，要定期砍。我们的 skill 一个都没有，先别急着堆。
- **观察性优先**：中间产物（原始响应、解析结果）留档，否则出问题无法复盘。
- **一个会话只干一件事**：TG 单会话的情况下，等于我要自己收口，不把话题搅在一起。

## 三、不要照抄的

- **七 agent 车队（协调者 + 六个专员）**：适合多项目管理，我们只有一个 workspace，纯属增加故障面。
- **Kanban 卡片链**：同上，重量级流程，对「一个人 + 一个策略」没有收益。
- **多 profile 隔离**：只有在「既要跑交易又要跑别的业务」时才值得，现阶段过度设计。

## 五、第二轮：又找到四条（含我们自己机器上的实测）

### 6. cron 钉模型的具体命令
```
hermes config set cron.model <model>                      # 全体默认
hermes cron edit <job_id> --model <m> --provider <p>      # 单任务钉
```
不钉就用聊天那个模型跑例行任务，既贵又可能被换供应商搞死。

**我们机器的实测**：5 个 cron 任务（`daily-learning-sweep`、`agent-daily-brief`、
`pearl-daily-watch`、`spot-perp-opportunity-research-v1`、`PEARL 期现：每日对账`），
**一个都没钉模型**，`cron.model` 也是空的。

### 7. 静默失败已经在我们身上发生
`agent-daily-brief` 上一次运行 **idle 7943 秒（2 小时 12 分）后超时失败**，
错误记在 cron 历史里但没人看。这就是「六天静默停机」的缩小版。

### 8. Prompt 缓存是最大的省钱杠杆（我们正好在用 deepseek-flash）
一篇生产实测（同款 flash）：**缓存命中 98.7%**，命中价 $0.003/M vs 未命中 $0.15/M，**差 50 倍**。
原理是「系统提示 + 技能 + 记忆 + 工具表」构成一个**逐字节不变的前缀**，每轮只追加小增量。
所以：
- 前缀越稳定越便宜；中间频繁改 SOUL/记忆/技能，会让下一轮重新付一次冷前缀。
- 短会话最亏（每个新会话至少付一次冷前缀，约 47k tokens ≈ $0.007），
  所以 TG 这种长会话反而便宜，不必为了省钱频繁 `/new`。
- 反过来：真正烧钱的是「超时还在打转」的任务（第 7 条那个 2 小时）。

### 9. `delegate_task` 可以并行 10 个子任务，上下文互不污染
适合「10 个地址同时查」「多来源同时读」，比我在一个会话里串行做省上下文。
但子任务自报的成功不算数，产物要我自己验（官方也这么写）。

### 10. 我们自己的 cron 里还有两个该退休的
套利已经全停，但 `pearl-daily-watch`、`PEARL 期现：每日对账` 还在每天跑并推送。
要么改成「只在有持仓时才跑」，要么停掉 —— 否则天天推没用的东西，正是你最烦的那种。

## 六、我们该做的（更新后，按性价比排序）

1. `hermes config set cron.model` 钉一个便宜模型 + 检查 5 个任务（5 分钟）
2. 停掉/改造两个 PEARL 相关 cron（5 分钟）
3. 给 `agent-daily-brief` 加超时与失败告警，或直接删（10 分钟）
4. SOUL.md 拆层（规则进 AGENTS.md）（10 分钟）
5. `~/.hermes` 配置入 git（30 分钟）


## 附：来源

- https://hermes-agent.nousresearch.com/docs/guides/use-soul-with-hermes
- https://hermes-agent.nousresearch.com/docs/guides/tips
- https://hermes-agent.nousresearch.com/docs/user-guide/features/memory
- https://hermes-agent.nousresearch.com/docs/guides/troubleshooting-agent-quality
- https://neogenmedia.com/blog/hermes-agent-in-production
- https://dev.to/threerouter/my-3-month-hermes-agents-journey-lessons-learned-and-disagreements-c5k
- https://www.reddit.com/r/hermesagent/comments/1xi1oyz/
- https://zhuanlan.zhihu.com/p/2044206310426671040
