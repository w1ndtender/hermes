# harness/

Hermes 自身的配置文件快照，用于让「harness 怎么演化的」可追溯（对应 notes/hermes-tuning/25）。

- `SOUL.md` —— 常驻规则，原样复制。
- `config.redacted.yaml` —— `~/.hermes/config.yaml` 脱敏版，所有含 key/token/secret/password 的字段替换为 `[REDACTED]`。

规矩：
1. 改完 `~/.hermes/SOUL.md` 或 `config.yaml`，同步到这里再 commit，commit message 写「症状 / 证据 / 怎么验证」。
2. 绝不放真凭据；同步前先跑脱敏。
3. 这里只是快照，不参与运行。
