# 任务书 06：修跑分器的两个缺陷

在现有 `~/repos/hermes/evals/run.py` 上做最小修改。**不重写，不改 `cases.jsonl`。**

## 缺陷 1：拿不到 session id，导致 tool_called 判据全废

现状：`hermes -z "<input>" --cli --pass-session-id` 实测**不输出任何 session id 标记**（stdout 只有回答正文），所以 `session_id=null`，`tool_called` / `tool_not_called` 永远 `errored`。

改成**按时间发现会话文件**：
1. 每条用例开始前记录 `t0 = time.time()`。
2. 跑完后在 `~/.hermes/logs/sessions/` 里找 `mtime >= t0 - 2` 且最新的那个 `*.jsonl`（注意：也可能是 `~/.hermes/sessions/`，两个路径都要试）。
3. 找不到就记 `errored`，错误写「未找到本轮的会话文件」，不许降级成通过。
4. 从该 jsonl 里数工具调用：找 `tool_calls` / `"name": "<tool>"` 结构即可，不需要精确解析全部 schema；判据只要求「有没有调用过某工具」。

## 缺陷 2：`--only` 重复传只跑最后一条

现状：`--only a --only b --only c` 只跑 c。

改成 `--only` 可重复（`action="append"`），跑所有指定的 id，按文件顺序执行。

## 附带要求

- 每条用例打印一行进度：`[3/20] id ... passed/failed/errored (12.3s)`
- 报告里加一列 `会话文件`（找到的文件名，找不到写 `-`）
- 保持退出码语义：全过 0，有 failed/errored 1

## 验收（必须真跑，别只 dry-run）

```bash
cd ~/repos/hermes
python3 evals/run.py --only ask-when-ambiguous --only conflict-merge
```

必须看到：
1. 两条都真的执行了（不是只跑最后一条）
2. `ask-when-ambiguous` 的判据明细里出现「是否调用工具」的结果（不再是 errored）
3. 报告里两行都有会话文件名

## 不许动
- `cases.jsonl` 的内容
- 判据类型（四种，够用）
- 不许把找不到会话文件当通过
