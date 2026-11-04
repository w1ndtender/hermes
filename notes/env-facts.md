# 环境事实（memory 外置区）

> memory 只留指针；具体路径、端口、参数、命令都在这里。改动请同时更新本文件。

## 主机与通路

- Hermes 主机：`43.163.243.28`（腾讯云东京，用户 `ubuntu`）
- 住宅代理：CBLNK VPS `162.225.42.211`（仅密钥登录），SSH SOCKS 隧道 `127.0.0.1:1080`，启动脚本 `~/.ssh/tunnel_x.sh`
- X 拒绝机房 IP：必须住宅 IP + 有头 Chrome
- 网页/远程输密码：用户 `cat > ~/.pw` 写入 → `xdotool type --file` 输入 → `shred` 删除
- VNC：`x11vnc` 需 `-auth`/`-xkb`；noVNC 走 `websockify`
- 文件上传：`~/uplink.py` 监听 8791，token `up58fb9264`
  隧道 `https://thehun-engineering-royalty-provided.trycloudflare.com/up58fb9264/`
  只收 `.html/.zip/.json/.txt`；拖文件夹必失败；VPS 公网 80 被腾讯云安全组挡死

## 浏览器 / X

- Xvfb `:98`（1400x1000x24）+ Chrome `--user-data-dir=/home/ubuntu/.cache/x-profile --proxy-server=socks5://127.0.0.1:1080 --remote-debugging-port=9335`
- 启动脚本 `~/squeek/chrome_restart.sh`；CDP 驱动 `~/squeek/cdp.py`
- X 账号 `@SauravY79514198`，登录态 `/home/ubuntu/.cache/x-profile`
- `browser_vault_fill` 只能填内置 Chromium；挂代理的 Chrome 会报 origin_mismatch，要用户经 VNC/xdotool 自己输
- 存密码：`vlogin <label> <origin> <user>`（隐藏输入，直写 vault）

## 交易所与账户

- 资金：SafeTrade USDT ~1,427 + PEARL 灰尘；Hyperliquid accountValue 0
- Hyperliquid API 钱包 `0xE24Cff9DE22F2242F967CFe67bA1Cb1576fCB278`，私钥 `/home/ubuntu/spread/hl_key.json`（600）
- SafeTrade 公开 API 被 Cloudflare 挡直连 → 必须 `~/squeek/cdp.py` 同源 fetch（`CDP_MATCH=safetrade`）
  `trades` 最多 1000 笔；加 `from/to/page` 参数即 403
- Entropy = Hyperliquid HIP-3 dex `io`（0-based index 9）；`io:PRL` asset=`190010`，最大 3x；行情走 `api.hyperliquid.xyz/info` + `dex:'io'`
- 现货盘口很薄：卖一常见 300 颗级，一次买超 300 颗就把价差买没
- 只有一个交易账户：Bitget。OKX 只有链上钱包，无交易所账户；缺 Gate/Bybit/Binance 充值地址库

## 链上 / 数据源坑

- BSC 查池子别只看 Pancake V2/V3 和 DexScreener：TOSH 在 PancakeSwap Infinity（v4 hook）池，报价换 USDT 才能路由到
- `api.bscscan.com` 403、Blockscout 403、Routescan 400/422
- `bsc.publicnode.com` / `base-rpc.publicnode.com`：`eth_getLogs` 不带 address 会**静默返回空**
- `bsc.blockrazor.xyz` 约 50 块/次且会 429；已降 2 并发 + 重试
- Base 用 `https://1rpc.io/base`；BSC 出块 **0.450 秒**（不是 3 秒）
- `fapi.binance.com` 可用；`api.binance.com` 部分路径 400

## 回测器（2026-11-04 建）

- 代码：`~/spread/backtest/`（Codex 写，我跑）
- 同所：`.venv/bin/python -m backtest.same_venue --symbols ... --days 180 --out backtest/out_x`
- 跨所：`.venv/bin/python -m backtest.crossvenue --symbols ... --venues binance,okx,bybit,gate --out ...`
- Codex 沙箱**没有外网**，真实接口必须我在沙箱外跑
- 结论：同所 148 市场 4 笔 +$101；跨所 0 笔。价差套利已证伪

## 停机与审批

- 独立停机看门狗 `~/spread/kill_switch.py`，触发写 `STOP` 文件；`hedger.py` 启动检查
- 亏损平仓审批：`~/spread/approve_close.sh` 建 `APPROVE_CLOSE` 文件
- 常驻看门狗（spread-watchdog / exec-watch.timer）已全部停用，用户禁止监控刷推送
