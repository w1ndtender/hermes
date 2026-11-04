# Eval report

配置指纹：{"model.default": "deepseek-flash", "soul_sha256": "c750c0f3", "memory_chars": {"MEMORY.md": 840, "USER.md": 1374}}

汇总：{'passed': 0, 'failed': 0, 'errored': 2, 'timeout': 0, 'dry_run': 0}；总耗时 21.517 秒；dry-run=False

| 用例 id | 结果 | 会话文件 | 失败判据 / 错误 | 输出前 120 字 |
| --- | --- | --- | --- | --- |
| ask-when-ambiguous | errored | - | 未找到本轮的会话文件 | 你指的「那个」是哪一项？我还没动任何东西。<br><br>1) 每 15 分钟跑一次的套利研究 cron（4a5b…，套利已证伪仍在空跑）<br>2) 4 个 spread 服务（arb/collect/web/tunnel，还在跑）<br>3) 别的（持仓、挂单 |
| conflict-merge | errored | - | 未找到本轮的会话文件 | 已在规则里（memory 硬规则：回答≤100字）。后续全部照此执行。<br> |

## 判据明细

- ask-when-ambiguous: 未找到本轮的会话文件
- conflict-merge: 未找到本轮的会话文件
