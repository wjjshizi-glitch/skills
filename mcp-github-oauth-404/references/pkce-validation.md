# PKCE 参数校验

PKCE 用于防止授权码被截获后被其他客户端兑换。检查参数时不得记录或共享 `code_verifier`。

## 正确关系

```text
code_challenge = BASE64URL(SHA256(code_verifier))
code_challenge_method = S256
```

- `code_verifier` 长度应为 43–128 个字符。
- 允许字符应符合 PKCE 规范：URL 安全字符集合。
- `code_challenge` 使用 URL-safe Base64：`+` 替换为 `-`，`/` 替换为 `_`，去掉结尾 `=` 填充。
- 授权请求带 `code_challenge` 和 `code_challenge_method=S256`；服务端交换授权码时必须带回原始 `code_verifier`。

## 常见错误

| 错误 | 影响 | 排查方向 |
|---|---|---|
| 使用普通 Base64 | challenge 含不安全字符或填充 | 使用 URL-safe Base64 并移除 `=` |
| `code_challenge_method` 大小写错误 | 授权端拒绝或流程失败 | 固定使用 `S256` |
| verifier 丢失或跨会话替换 | token 兑换失败 | 确认服务端按会话安全保存并匹配 verifier |
| callback 后未带 verifier 兑换 | token endpoint 返回错误 | 检查仅服务端可见的兑换逻辑 |

## 注意

PKCE 配置问题通常影响授权或 token 兑换，不一定直接导致 HTTP 404。若 404 出现在 GitHub 授权成功后的 callback，请优先检查 [回调 404](callback-404-errors.md)。
