# 25 · 七层 harness 地图（ETCLOVG）：我们缺哪层

来源：
- CMU/Yale/Amazon 等 2026 综述提出的 ETCLOVG 分类法，原文解读 https://truefoundry.com/blog/etclovg-agent-harness-reliability-gateway
- deepset《Harness Engineering》https://deepset.ai/blog/harness-engineering
- Anthropic《Writing effective tools for agents》https://www.anthropic.com/engineering/writing-tools-for-agents

## 一句话

**可靠性是模型外面那圈系统的属性，不是模型的属性。** 出问题时先定位是哪一层，别一上来就换模型或改提示词。

## 七层

| 层 | 管什么 | 我们的实现 | 状态 |
|-|---|---|-|
| **E** 执行环境 | 动作在哪跑、能碰什么 | systemd 服务、Codex bwrap 沙箱 | 中（沙箱无网，是特性） |
| **T** 工具接口 | 能力怎么描述/发现/调用 | Hermes 工具 + skill | 中（返回体偏大） |
| **C** 上下文 | 模型每一步看到什么 | SOUL 48 行、memory 901 字、skill 按需加载、compaction | 较好 |
| **L** 生命周期 | 读写状态的控制流 | cron + claim 锁、state.db | **弱**（今天刚修 IncompleteRead 整批失败） |
| **O** 可观测 | trace/成本/失败 | healthcheck.py（今天上线） | 刚起步 |
| **V** 验证 | 跑对没有 | evals/cases.jsonl 20 条 | **最弱**（用例跑不通 trace） |
| **G** 治理 | 权限/审批/审计 | 审批队列、STOP 文件、vault | 中 |

综述说 O 和 V 在开源项目里普遍最薄——和我们一致。

## 三个跨层效应（最容易踩）

1. **能力–控制是同一根轴**：工具越多、记忆越久、沙箱越松，能做事的范围变大，误伤范围同比变大。
2. **改一层会顶到别层**：加重试（L）会让输出重进上下文（C）、让 trace 多一条（O）、让每次重试重新计费（成本）。
3. **必须整系统测**：单层看起来变好，组合起来可能更差。

## 我们的三个缺口（按可修性排序）

1. **配置不在 git。** `SOUL.md`、`config.yaml`、skills 的改动没有历史，所以"harness 是怎么演化来的、每次改动有没有变好"根本查不了。deepset 的整篇论点就是这个：harness 必须在版本控制里。
2. **V 层是半成品。** 20 条用例，实测只跑通几条；会话轨迹在 `~/.hermes/state.db` 的 `sessions`/`messages` 表，不在 jsonl，所以"有没有调工具"这类判据全部 error。
3. **L 层靠运气。** cron 卡 7943 秒、claim 过期被判 wedged、一个源断了整批失败——都是生命周期层的问题，不是模型问题。

## 规矩

- 出问题先归类到七层之一，再说怎么修；归不了类说明还没看懂。
- 每次改 harness（改 SOUL/memory/skill/cron/工具）当成系统变更：跑 eval、看成本、看 trace。
- O 和 V 不建起来，前面五层改了也不知道有没有变好。
