# 任务书 10：跑分器改从 state.db 读会话轨迹

## 背景

`evals/run.py` 每跑一条用例，靠"找本轮的会话文件"来判定有没有调用工具。但会话**不存在 jsonl 文件里**，
而在 `~/.hermes/state.db`。所以 `tool_called` 类判据全部 `errored`（未找到本轮的会话文件）。

## 真实表结构（已实测）

```sql
sessions(id TEXT PK, started_at, ended_at, message_count INT, tool_call_count INT,
         tool_names TEXT, model, estimated_cost_usd REAL, cost_status, title, ...)
messages(id, session_id, role, content, tool_calls, tool_name, timestamp, token_count, ...)
```

`messages.tool_calls` 是 JSON 串（assistant 发起调用时）；`messages.tool_name` 非空表示那是工具结果行。

## 要改成什么

1. 每条用例开始前记 `t0 = now()`；跑完后在 `state.db` 里找
   `SELECT id FROM sessions WHERE started_at >= t0 ORDER BY started_at DESC LIMIT 1`。
   找不到 → 该用例 `errored`，原因写"state.db 里没有本轮会话"。
2. 从 `messages` 里统计：
   - `tool_calls` 非空的 assistant 行 → 解析 JSON，取出每次调用的 `name`
   - `tool_name` 非空的行 → 也算一次调用
   - 汇总成 `tool_names`（去重、按出现顺序）
3. 判据 `tool_called` 改为：`expected ⊆ tool_names`；`tool_not_called`：`expected ∉ tool_names`。
4. 报告里加两列：`会话 id`、`工具调用`（逗号分隔，最多列 6 个）。
5. 顺带把 `estimated_cost_usd` 读出来，报告末尾给"本轮总成本（估算）"。
6. `state.db` 只读打开（`mode=ro` URI），绝不写。

## 不许动

- 不改 `cases.jsonl`
- 不改 `--only` / `--limit` / `--dry-run` 语义
- 不改退出码规则（全过 0，有失败 1）
- 不加依赖（sqlite3 标准库）

## 验收

```bash
cd ~/repos/hermes
python3 evals/run.py --only conflict-merge
# 期望：能打印会话 id 和工具调用；判据不再报"未找到会话文件"
python3 -m unittest evals.test_run -v   # 原有 5 项仍需通过
```

## 回滚

改前 `cp evals/run.py evals/run.py.bak`。
