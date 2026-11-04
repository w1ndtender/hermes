# 16 脚本模式 cron（no-agent）：零 token 监控的正规做法

官方文档：`docs/guides/cron-script-only`。

## 机制
调度器每 N 分钟跑一次脚本 → 脚本 stdout 非空就投递（Telegram/飞书/…），**空则完全静默**。
不调用模型，不消耗 token，不会因为模型理解不同给出不确定结论。

## 创建方式（agent 自己就能建）
```python
cronjob(action="create",
        schedule="every 5m",
        script="pc-watch.sh",        # 相对 ~/.hermes/scripts/
        no_agent=True,
        deliver="telegram",
        name="pc-watch")
```
脚本先写到 `~/.hermes/scripts/` 下。

## 硬性限制（踩了就白干）
- 脚本路径**必须落在 `~/.hermes/scripts/` 内**（相对、绝对、`~` 都行，但不能越界）。
- `.sh` / `.bash` 用 bash 跑；其他扩展名用当前 Python 解释器。
- 要用自己的 venv：`--interpreter /path/to/.venv/bin/python`。
- **脚本不继承 provider 凭据**（不要指望环境里有 API key，凭据要自己从文件读）。
- 停任务：`hermes cron cancel <id>`（只停当次）/ `remove`（连在跑的一起杀）。

## 什么时候用哪种
- **脚本模式**：条件明确、输出即消息（阈值告警、心跳、状态检查、抓取后过滤）。
- **agent 模式**：需要判断该说什么（总结长文、挑重点、写人话）。

## 价格监控技能里的三条硬规矩（可直接搬到我们的行情监控）
1. **先定义合约**：同一个标的不能有两种理解（币、链、池、交易对、方向）。
2. **先跑一次前台基线**，确认抓得到，再挂定时；不许「先挂上去看看」。
3. **抓取失败 ≠ 价格变了**：失败要标记为「未知」，绝不能拿错误页覆盖上一次好数据。

## 我们该怎么改
现有 5 个 cron 全是 agent 模式。改造顺序：
1. `chain-scan`（每 10 分钟）→ 脚本模式，有货才输出。
2. 同行钱包监控 → 脚本模式做抓取与去重，只在命中三类条件时输出。
3. 日报 → 保留 agent 模式（要写人话、要挑重点），但钉小模型。
