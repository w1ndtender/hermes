# 任务 11：推送排版统一（Telegram + 飞书）

交给：Codex / Claude Code
产出：改动后的文件清单 + §4 每条验收命令的真实输出
不允许：自行发送任何 TG / 飞书消息（测试消息要用户当次点头）

## 0. 一句话

把 7 个推送点统一走 `fmt.push`，TG 用「分块 + 等宽对齐 + 不出现长串 ｜」，飞书统一两列卡片；
不改阈值、不改去重闸、不动账本。

## 1. 现状（实测证据，2026-11-05 00:15 CST）

两套发法并存：

- `fmt.push()`（`fmt.py:62`）→ 飞书卡片 + TG HTML。但 `_tg_html()`（`fmt.py:40`）只是把 `**` 删掉、`<font>` 换成 `<b>`、分隔线换成 `──────`，等于 TG 版把重点全丢了。
- `spread_alert.send()`（`spread_alert.py:68`）→ TG 纯文本（无 parse_mode），同时把同一段纯文本丢进飞书（`feishu()` 用 `msg_type=text`），**没有卡片**。

走纯文本的点：`taoli_alert.py:66`、`peer_alert.py:88`、`exec.py:132 tg()`（建仓/平仓/成交）
走卡片的点：`digest_compact.py:56`、`today_review3.py:98/113/132`、`risk_watch.py:100`

实测当前日报 `.venv/bin/python digest_compact.py --dry --yesterday` 原文：

```
买 **$7,821**　卖 **$4,752**　触发 **6** 条
---
🟢 NI $5.6K 买 CT $3,093 ｜ SOS $198.5K 买 BNCB $1,202 ｜ 2ea $46.7K 买 BNCB $1,051
🔴 NI $5.6K 卖 LYN $2,032 ｜ 2ea $46.7K 卖 牛来 $256 ｜ SOS $198.5K 卖 LYN $182
---
🔔 🆕 NI $5.6K ★重点 今日首次买 CAP（$92） ｜ 🔁 NI $5.6K ★重点 30 分钟内买 CT 12 笔（$3,093）
```

六个问题：

1. 每行 3 组用 `｜` 连成一条，手机上一换行就折成一堵墙。
2. 金额三种写法混排（`$5.6K` / `$3,093` / `$92`），扫读时无法纵向对比。
3. 空数据日仍输出 `🟢 ` / `🔴 ` 两条空壳（今日 `--dry` 实测就是空的）。
4. 标签被 `short()` 截到 14 字符，信号行里 `★重点` 没被清掉。
5. TG 版 `**` 全被删，标题层级和强调全部消失。
6. 同一个事件在飞书有时是卡片、有时是纯文本，取决于走哪条代码路径。

## 2. 要改成什么

### 2.1 单一入口

```
fmt.push(kind, title, sections, note=None)
```

`kind ∈ diary | opportunity | risk | entry | exit | notice`，映射 (飞书标题色, TG emoji 前缀)。
所有业务推送点改调它；`spread_alert.send()` 只保留给系统故障 / 原始日志，不再承载业务推送。

### 2.2 TG 排版规则（parse_mode=HTML）

1. 标题一行 `<b>`，含 emoji + 日期；正文按块用**空行**分隔，块内禁止 `｜` 连接。
2. 需要对齐的数字（Top N、金额、条数）放进 `<pre>` 等宽块，列宽固定；比例字体下不要用空格硬对齐。
3. 空数据整块不输出——不留 `🟢 ` / `🔴 ` 空壳；全天无信号只输出一行「今日无信号」。
4. 金额统一：≥1000 用千分位 `$7,821`，<1000 用 `$92`，**禁用 K 缩写**；BNB 一律附 USDT 等值。
5. 页脚一行 `<i>口径 · 生成 HH:MM</i>`，例：`北京时间 0 点起算 · 生成 00:12`。
6. 每个块最多 3 行，超出的进日报。
7. emoji 前缀必须落在 `msg[:40]` 内（见 §3 第 1 条硬坑）。

日报目标形态（TG，`<pre>` 部分实际是等宽块）：

```
📊 11-04 同行日报

买入  $7,821
卖出  $4,752
触发  6 条

🟢 买入 Top3
1  NI    CT     $3,093
2  SOS   BNCB   $1,202
3  2ea   BNCB   $1,051

🔴 卖出 Top3
1  NI    LYN    $2,032
2  2ea   牛来     $256
3  SOS   LYN     $182

🔔 信号
• NI 首买 CAP $92
• NI 30 分钟买 CT 12 笔 $3,093

北京时间 0 点起算 · 生成 00:12
```

这个样例要写成测试期望（§4 第 5 条）。

### 2.3 飞书排版规则

统一 `fmt2.card()`：`column_set` 两列（左名字 weight 3、右金额 weight 2 右对齐）+ `hr` 分块 + 标题色按 kind + 页脚 `note` 与 TG 页脚同文。
**禁止再用 `msg_type=text` 推业务消息。**

### 2.4 各推送点目标形态

| 推送点 | kind | TG 分块 |
|---|---|---|
| digest_compact | diary | 总览 / 买入 Top3 / 卖出 Top3 / 信号 |
| today_review3 版1·2·3 | diary | 同上；版3 的条形图只留飞书卡片，TG 用 Top5 `<pre>` |
| taoli_alert | opportunity | 品种 + 两腿 / 资费·年化·24h量 / 建议 size 与一句风险提示 |
| peer_alert | opportunity | 币 + 池 / 金额 + 笔数 / 依据 |
| exec.tg 建仓 | entry | 品种 / 两腿价格与数量 / 预期价差与止损位 / 单号 |
| exec.tg 平仓 | exit | 品种 / 开平价格 / 已实现盈亏 / 原因 |
| risk_watch | risk | 触发原因 / 当前值 / 建议动作（不自动执行） |

## 3. 不许动

1. **去重闸**：`exec.py:136` 的
   `_must = any(k in msg[:40] for k in ("📌", "🟢", "🔴", "✅ 平仓", "🚨", "建仓", "已平"))`
   —— 建仓/平仓/成交推送的 emoji 前缀必须留在前 40 字符内，否则会被 `_alert_gate` 吞掉。改版后必须回归验证。
2. 阈值、冷却时间、每日上限、`config.json` 任何字段。
3. `STOP`、`APPROVE_CLOSE`、`dry_run` 默认值。
4. 账本文件（`exec_ledger.jsonl`、`wallet_events.jsonl`、`hedger.jsonl`）不读不写。
5. 不新增依赖（只用 stdlib + 现有 venv）。
6. 不加网络请求、不加遥测。

## 4. 验收

```bash
cd /home/ubuntu/spread
cp fmt.py fmt.py.bak_$(date +%m%d_%H%M)

# 1) 昨日日报：无空 emoji 行、无 ｜ 连串、金额千分位
.venv/bin/python digest_compact.py --dry --yesterday

# 2) 今日空数据：只输出「今日无信号」，无空壳行
.venv/bin/python digest_compact.py --dry

# 3) 现有单测全绿
.venv/bin/python tests_exec.py

# 4) 去重闸回归：建仓消息必须不被闸
.venv/bin/python -c "import exec as ex; ex.cfg=lambda: {'tg': True}; print(ex._alert_gate('🟢 建仓 PRL USDT'))"

# 5) 只渲染不发送：新增 --preview，把 TG HTML 打到 stdout
.venv/bin/python digest_compact.py --preview
```

通过标准：1–3 无报错；4 返回 `True`；5 的输出与 §2.2 样例逐行对得上（日期、数字除外）。

## 5. 回滚

`cp fmt.py.bak_<时间戳> fmt.py`，其它改动文件同样按时间戳备份回滚。
`~/spread` **不是 git 仓库**，不要用 git 回滚。
改前先 `ps aux | grep -E "digest|alert|exec.py"` 确认没有进程正在写消息。
