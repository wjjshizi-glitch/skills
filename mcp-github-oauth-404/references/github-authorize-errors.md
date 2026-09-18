# GitHub 授权端错误（阶段一）

阶段一指请求 `https://github.com/login/oauth/authorize` 时即失败，或还未完成 GitHub 授权页面就无法继续。

## 先确认它真的是 404

GitHub OAuth 的配置问题经常表现为页面错误或带 `error` 参数的跳转，而非 HTTP 404。例如：

- `error=redirect_uri_mismatch`：请求中的 `redirect_uri` 与 OAuth App 注册值不匹配。
- 应用未启用、已删除、`client_id` 不正确：可能导致授权不能继续。
- 被复制、聊天工具转义或浏览器扩展改写的 URL：可能导致参数丢失或路径异常。

请记录浏览器实际状态码和最终域名/路径；不要贴出 `code`、完整 `state` 或任何 token。

## 检查清单

1. **路径固定**：应为 `https://github.com/login/oauth/authorize`，域名应是 `github.com`。
2. **`client_id`**：确认来自预期的 OAuth App 配置，且 URL 未截断。它不是 client secret，但对外报告时仍建议掩码。
3. **精确 `redirect_uri`**：协议、域名、路径、尾部斜杠都可能影响匹配。对照 GitHub OAuth App 的注册 Callback URL。
4. **scope 格式**：OAuth URL 内 scope 是空格分隔的值，经 URL 编码后常显示为 `+` 或 `%20`；不要错误使用逗号。
5. **避免手工改写 PKCE 参数**：`code_challenge_method` 应为 `S256`，见 [PKCE 校验](pkce-validation.md)。
6. **环境归属**：若 callback 路径含 `ark_stg`，确认正在使用与该环境匹配的 OAuth App 和回调配置。

## 推荐处理

- 从产品/MCP 登录入口重新生成链接，不要反复使用旧链接。
- 若 GitHub App 管理权限在团队手中，请管理员核对 OAuth App 是否仍启用，以及 Callback URL 是否精确匹配。
- 不要为了排障请求或导出 OAuth App 的 client secret。
