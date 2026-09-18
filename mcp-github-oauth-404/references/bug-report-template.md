# GitHub OAuth 404 问题报告（脱敏模板）

> 提交前请确认本文不包含 `client_secret`、`access_token`、`refresh_token`、授权码 `code`、`code_verifier`、完整 `state` 或 Cookie。它们请全部替换为 `<REDACTED>`。

## 问题阶段（必填，选一）

- [ ] 阶段一：打开 GitHub 授权地址时出现 404 或无法进入授权流程
- [ ] 阶段二：GitHub 授权成功后，跳转到 `redirect_uri` 时出现 404
- [ ] 其他 OAuth 错误（例如 `redirect_uri_mismatch`，请填写错误名称）

## 环境信息

- MCP/产品入口：
- 环境：生产 / stg / 不确定
- 回调路径特征：包含 `ark_stg` / 不包含 / 不确定
- PKCE：是 / 否 / 不确定
- 发生时间（含时区）：
- Request ID / Trace ID（如有）：

## 已脱敏的地址

- authorize URL（仅域名、路径和非敏感参数；`client_id`、`state` 等已掩码）：
  ```text
  https://github.com/login/oauth/authorize?client_id=<REDACTED>&redirect_uri=<YOUR_CALLBACK_URI>&scope=<SCOPE>&state=<REDACTED>&code_challenge=<REDACTED>&code_challenge_method=S256
  ```
- 实际 404 地址：仅填写域名与路径，**不含查询参数**
  ```text
  https://example.com/path/to/callback
  ```

## 回调配置核对

- GitHub OAuth App 中登记的 callback URL（仅协议、域名、路径）：
- 实际请求的 redirect URI（仅协议、域名、路径）：
- 两者是否完全匹配：是 / 否 / 无法确认
- BytePlus/服务端 callback 路由部署状态：

## 错误现象

- HTTP 状态码：
- 出错位置（GitHub 授权页 / 浏览器回调页 / 服务端日志）：
- 错误文本（已脱敏）：
- 复现频率：

## 已尝试的排查

1. 
2. 
3. 

## 本地检查输出（可选，已审核脱敏）

```text
粘贴 check_oauth_flow.py 的无敏感输出
```

## 期望与实际结果

- 期望：
- 实际：
