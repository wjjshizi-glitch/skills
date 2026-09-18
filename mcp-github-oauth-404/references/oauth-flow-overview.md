# GitHub OAuth + MCP 流程概览

```text
[MCP 客户端 / 控制台]
        |
        | 1. 构造 authorize URL
        |    client_id / redirect_uri / scope / state /
        |    code_challenge / code_challenge_method=S256
        v
[GitHub: /login/oauth/authorize]
        |
        +--- 这里显示 HTTP 404 ---> 阶段一：授权端或链接构造问题
        |
        v
[用户登录并同意 GitHub 授权]
        |
        | 2. GitHub 重定向：redirect_uri?code=...&state=...
        v
[BytePlus / MCP callback handler]
        |
        +--- 这里显示 HTTP 404 ---> 阶段二：回调路由、环境或注册配置问题
        |
        v
[服务端使用 code + code_verifier 兑换 token]
        |
        v
[MCP 连接建立]
```

## 关键判断

- **阶段一**：浏览器还没有成功完成 GitHub 的授权页面或请求。先确认授权 URL 未被截断、OAuth App 仍有效、参数格式正确。
- **阶段二**：GitHub 已接受登录/授权，浏览器地址栏已跳到 `redirect_uri`，然后该回调服务返回 404。优先查 callback 路由、网关、环境和精确 URI 注册。
- `redirect_uri_mismatch` 是 GitHub OAuth 配置错误，通常不是 HTTP 404。应记录错误名称，不能把它与回调端 404 混为一谈。

## 分享信息前脱敏

不要分享 URL 查询参数中的 `code` 或完整 `state`，也不要分享 `client_secret`、token、`code_verifier`。保留域名和路径通常足以判断回调是否落在正确服务。
