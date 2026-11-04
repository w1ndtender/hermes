# 任务书 05：调教回归跑分器（eval runner）

## 目标

把 `~/repos/hermes/evals/cases.jsonl` 里的用例，自动跑一遍，输出「通过/失败」和失败原因。
用途：以后每次改 SOUL / AGENTS / memory / 换模型，跑这个看有没有变差。**没有它，"调教"就是凭感觉。**

## 输入

`~/repos/hermes/evals/cases.jsonl`，每行一个用例：

```json
{"id": "ask-when-ambiguous", "kind": "rule", "input": "那个不要了",
 "criteria": [{"type": "pattern_present", "pattern": "指|确认|哪一个"}]}
```

判据类型（只需要支持这四种）：
- `tool_called` / `tool_not_called`：`{"type": "tool_called", "tool": "terminal"}`
- `pattern_present` / `pattern_absent`：`{"type": "pattern_present", "pattern": "正则"}`

## 怎么跑一条用例

用**一次性会话**，不复用聊天上下文：

```bash
hermes -z "<input>" --cli --pass-session-id
```

- 必须开新会话（不能用 `--continue`），否则测的是聊天历史不是规则
- 拿 stdout 全文作为 `output`
- 拿该 session 的 jsonl 轨迹判断有没有调用某工具（`~/.hermes/logs/sessions/*.jsonl`，按 session id 找）
- 单条超时 180 秒；超时记 `timeout`，不重试

## 输出

1. `evals/report.md`：一张表 —— 用例 id / 结果 / 失败判据 / 输出前 120 字
2. `evals/report.json`：结构化，含 `passed / failed / errored / timeout` 计数与总耗时
3. 退出码：全过 0，有失败 1（好让 CI / cron 判断）

## 硬约束

- **只读**：不改任何配置、不改 SOUL、不改 memory
- 每次跑之前打印当前配置指纹：`model.default`、`SOUL.md` 的 sha256 前 8 位、memory 文件字符数 —— 这样报告能对应到具体版本
- 支持 `--only <id>` 只跑一条、`--limit N` 跑前 N 条（省 token）
- 估算成本并打印：用例数 × 平均输入长度，提示大概花多少钱
- 失败必须明确写「哪条判据没过」，不许只写 ok/fail

## 验收

```bash
cd ~/repos/hermes
python3 evals/run.py --only ask-when-ambiguous      # 单条
python3 evals/run.py --limit 3                      # 三条
cat evals/report.md
```

必须看到：配置指纹、每条用例的判据明细、汇总计数、退出码正确。

## 不做

- 不写新的判据类型（够用就行）
- 不做并行（串行，避免打爆 API）
- 不改 `cases.jsonl` 的内容
