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

## 四、我们该做的三件事（按优先级）

1. 把 SOUL.md 拆干净（身份 vs 规则），规则进 AGENTS.md —— 十分钟。
2. `~/.hermes` 的配置纳入 git（不含密钥），改坏可回滚 —— 半小时。
3. 逐个检查 cron 是否钉模型，并加「一天一行健康日志」—— 一小时。

## 附：来源

- https://hermes-agent.nousresearch.com/docs/guides/use-soul-with-hermes
- https://hermes-agent.nousresearch.com/docs/guides/tips
- https://hermes-agent.nousresearch.com/docs/user-guide/features/memory
- https://hermes-agent.nousresearch.com/docs/guides/troubleshooting-agent-quality
- https://neogenmedia.com/blog/hermes-agent-in-production
- https://dev.to/threerouter/my-3-month-hermes-agents-journey-lessons-learned-and-disagreements-c5k
- https://www.reddit.com/r/hermesagent/comments/1xi1oyz/
- https://zhuanlan.zhihu.com/p/2044206310426671040
