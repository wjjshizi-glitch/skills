# 授权后回调 404（阶段二）

阶段二指用户已在 GitHub 完成登录/授权，随后浏览器跳到 `redirect_uri`，例如 BytePlus 控制台路径，最后由该地址返回 404。

## 常见原因

| 检查项 | 可能问题 | 建议处理 |
|---|---|---|
| 回调路由 | callback handler 没有部署或路径变更 | 核对网关/API 路由和发布版本 |
| 精确 URI 注册 | GitHub App 中的 Callback URL 与实际请求不一致 | 比较协议、域名、完整路径和尾部斜杠 |
| 环境错配 | 生产入口引用 `ark_stg` 路由，或预发 handler 未部署 | 核对 stg/prod 的独立配置与部署状态 |
| 反向代理/网关 | 网关没有转发 callback 或路径重写错误 | 查看受控服务的路由规则和服务日志 |
| 回调 handler | handler 仅允许某些方法或依赖缺失 | 检查授权服务日志、Request ID、部署健康状态 |

## 关于 `ark_stg`

路径中出现 `ark_stg` 是该系统使用预发/环境路由命名的线索，不自动构成漏洞。它值得确认：

1. 此路径是否是该登录入口预期的环境；
2. 该环境是否部署了完整 callback handler；
3. GitHub OAuth App 和控制台是否都登记了同一个、精确的 callback URI；
4. 是否存在生产/预发配置交叉引用。

## 安全的最小验证

在你拥有或明确获授权管理 callback 服务的前提下，可请求不带查询参数的 URL：

```bash
curl -I "https://your-console.example.com/api/.../VaultOAuthCallback"
```

- 无查询参数也返回 404：路由本身可能未部署或网关未匹配。
- 返回 200、204、302、401、403 或 405：路由可能存在；不能仅由此判定 OAuth 回调会成功。

不要把真实 OAuth 回调 URL（尤其含 `code`、`state`）交给 curl、日志、截图或工单。可使用本 Skill 的脚本并在交互确认后执行无凭据 HEAD 检查。
