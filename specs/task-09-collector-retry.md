# 任务书 09：研究脚本的批次容错（IncompleteRead 不该整批失败）

## 症状

`hermes cron` 任务 `spot-perp-opportunity-research-v1`（每 15 分钟）从 2026-11-03 12:35 起反复失败，
退出码 1，错误：

```
ValueError: Incomplete configured batch: ['IncompleteRead: IncompleteRead(5215 bytes read, 7455 more expected)']
```

调用链：`~/.hermes/scripts/arb_cost_aware_tick_v1.py` → `runner.py:main()` → `collector.py:capture()`
→ 某个源读取时 chunked 响应被截断 → 整个批次判失败 → raise。

## 问题定性

**一次网络截断，惩罚整批数据。** 该脚本的设计意图是"批次不完整就保留上一次完整观察"，
这个方向对；但实现成了"任何一源 IncompleteRead → 整批失败"，导致：
- 15 分钟一次，一次抖动就白跑
- 失败率被健康检查持续抓到，噪音掩盖真故障

## 要改成什么

1. **单源重试**：`IncompleteRead`、`ChunkedEncodingError`、`ConnectionResetError`、读超时
   属于可重试；对失败的那个源重试 2 次，退避 1s / 3s。
2. **重试后仍失败 → 只把该源标记为 `missing`**，其余源照常写入完整观察，
   并在 `run-state.json` 里记 `partial: true` + 缺失源名。
3. **只有「关键源全失败」才 raise**（定义写进配置：哪些源是关键）。
4. **不要用旧值冒充新值**：缺的源写 null/missing，不许沿用上一轮数值。
5. 日志里给每个源一行：`source=binance status=ok retries=0`，便于以后统计。

## 不许动

- 不改策略、不改阈值、不改推送逻辑、不下单
- 不改其他三个 cron 任务
- 不引入新依赖（标准库 urllib/requests 已有足够能力）

## 验收

```bash
cd ~/arb-research-hermes-v1/efficient-v1
python3 runner.py            # 正常应退出码 0
python3 -c "import json;d=json.load(open('run-state.json'));print(d.get('partial'), d.get('missing_sources'))"
```

另外用一个假源模拟 IncompleteRead（测试里 monkeypatch），必须看到：
重试 2 次 → 该源 missing → 仍有完整输出 → 退出码 0。

## 回滚

改前 `cp collector.py collector.py.bak`。
