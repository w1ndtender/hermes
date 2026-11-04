# 任务书 08：每日健康检查（脚本模式，零 token）

## 目标

每天早上 08:00 用户只看到**一行**：正常就一句话；有异常才列问题。
不让用户自己去翻日志、猜哪里坏了。

## 形态

- `~/.hermes/scripts/healthcheck.py`
- cron：`every day at 08:00`，`--no-agent --script ~/.hermes/scripts/healthcheck.py --deliver telegram`
- **不许调用任何 LLM**，纯脚本，stdout 直接推给用户

## 检查项（每项给「正常/异常」+ 证据）

1. **网关存活**：`hermes gateway status` 或进程存在性；不在就报「网关没在跑」。
2. **定时任务**：查 `~/.hermes/cron/executions.db`（SQLite），统计过去 24 小时
   `status != 'ok'` 的执行，列出 job 名 + 错误首行。
3. **静默失败**：统计 `~/.hermes/logs/errors.log` 过去 24 小时
   `ERROR`/`CRITICAL` 条数；>0 时按模块聚合，给出前 3 类。
   过滤掉已知噪音（`linked SQLite ... is vulnerable`、`unknown config keys ignored`、
   `Background MCP discovery`、`memory pressure is elevated`）。
4. **余额**：`GET https://api.deepseek.com/user/balance`，key 从 `~/.hermes/.env` 的
   `DEEPSEEK_API_KEY` 读；**只在 < ¥3 时报警**，正常不显示（用户不需要每天看）。
5. **磁盘/内存**：根分区 >85% 或可用内存 <500MB 才报。
6. **STOP 文件**：`~/spread/STOP` 存在就报（说明有东西被停机了）。
7. **eval 基线老化**：`~/repos/hermes/evals/report.json` 超过 14 天没更新就提示「该跑一次基线」。

## 输出格式（硬要求）

全部正常时，只输出一行：
```
✅ 一切正常 | 网关 ok | 定时 3/3 成功 | 24h 无报错 | 磁盘 16%
```

有异常时：
```
⚠️ 2 个问题
1. 定时任务 agent-daily-brief 昨天 11:00 失败：TimeoutError（卡 7943s）
2. 24h 内 ERROR 4 条，集中在 cron.jobs（锁等待 3 次）
其它：网关 ok | 磁盘 16% | 余额正常
```

- 总长 ≤12 行
- **不解释过程、不给建议清单**，只说事实
- 某项查不到就写 `未知`，不许当正常

## 硬约束

- 只读：不改任何配置、不重启服务、不写数据库
- 网络请求必须 10 秒超时；失败记「未知」，不许让整条脚本挂掉
- 任何单项检查抛异常，捕获后记为「未知（检查出错: 原因）」，其余项继续
- 不许读私钥文件、不许把 API key 打印出来

## 验收

```bash
python3 ~/.hermes/scripts/healthcheck.py          # 现在跑一次，看输出
python3 ~/.hermes/scripts/healthcheck.py --json   # 结构化，便于以后画趋势
```

必须能在这台机器上真实跑通并给出上述格式。
