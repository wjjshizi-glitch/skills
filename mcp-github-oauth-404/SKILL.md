---
name: mcp-github-oauth-404
description: "排查 MCP GitHub OAuth PKCE 登录中的 404。适用于 GitHub 授权链接打不开、GitHub 授权成功后 BytePlus/方舟 ark_stg 回调 404、redirect_uri 配置不匹配、OAuth scope 过宽或需要生成脱敏 Bug 报告的场景。"
---

# MCP GitHub OAuth 404 排错助手

## 目标与边界

本 Skill 用于定位 **MCP 使用 GitHub OAuth + PKCE 登录时的 404**，并产出可安全分享的中文问题报告。

- 只做诊断与最小化连通性检查；不发起完整授权、不兑换授权码、不访问需认证的 GitHub API。
- 不处理、保存或输出 `client_secret`、授权码 `code`、`access_token`、`refresh_token`、`code_verifier` 或完整 `state`。
- 仅可对用户拥有或已获明确授权的 callback 服务做无凭据 `HEAD` 检查。

## 先确定 404 发生位置

| 现象 | 阶段 | 优先检查 |
|---|---|---|
| 打开 `https://github.com/login/oauth/authorize?...` 就显示 404 | 阶段一：GitHub 授权端 | 链接是否完整、`client_id`、OAuth App 状态、URL 参数格式 |
| GitHub 登录/同意授权后，跳至 `redirect_uri` 才 404 | 阶段二：回调端 | callback 路由部署、精确 URI 注册、`ark_stg`/生产环境是否混用 |
| GitHub 显示 `redirect_uri_mismatch` 或其他 OAuth 错误 | 非 HTTP 404 | GitHub App 的 Callback URL 与请求里的 `redirect_uri` 是否完全匹配 |

完整流程见 [OAuth 流程概览](references/oauth-flow-overview.md)。

## 快速诊断

1. **重新从 MCP 登录入口发起一次流程**。不要复用已分享或已过期的授权 URL。
2. 记录 404 出现的时机：进入 GitHub 前，还是在 GitHub 同意授权后。
3. 仅保留安全信息：域名、路径、状态码、时间、Request ID（如有）。查询参数中 `code`、`state` 等必须删除或替换。
4. 若是阶段一，查阅 [GitHub 授权端错误](references/github-authorize-errors.md) 和 [PKCE 校验](references/pkce-validation.md)。
5. 若是阶段二，查阅 [回调 404](references/callback-404-errors.md)。`ark_stg` 只是环境路由线索，不能仅凭该字符串认定安全漏洞。
6. 评估 scope 是否符合最小权限原则，见 [Scope 检查清单](references/scope-checklist.md)。宽泛 `repo` 权限不会直接导致 404。
7. 使用 [Bug 报告模板](references/bug-report-template.md) 输出脱敏信息。

## 辅助脚本

`scripts/check_oauth_flow.py` 使用 Python 3 标准库执行本地参数检查：

```bash
python3 scripts/check_oauth_flow.py \
  --client-id "YOUR_CLIENT_ID" \
  --redirect-uri "https://your-console.example.com/oauth/callback" \
  --scope "repo read:org read:user user:email"
```

可选行为：

- `--check-github-endpoint`：对 GitHub **无查询参数** OAuth 授权端点发出 HEAD 请求；不会发起 OAuth 流程。
- `--check-callback-head`：先要求交互确认，再向所提供 callback 的无查询参数 URL 发出无凭据 HEAD 请求。仅限你拥有或获授权的服务。

脚本不会接受或打印 OAuth secret、token、授权码或 verifier。运行后仍应人工检查输出是否适合分享。

## 安全报告结论标准

404 本身通常是功能或配置问题。若要作为安全问题上报，需要额外、合法地证实例如：回调地址可被攻击者控制、服务端未校验 `state`/PKCE、授权码或 token 泄露、账户被错误绑定。不要为验证这些情况而尝试越权访问或使用他人凭据。

## Resources

### references/

- `oauth-flow-overview.md`：OAuth 流程和 404 位置
- `github-authorize-errors.md`：阶段一排查
- `callback-404-errors.md`：阶段二排查
- `pkce-validation.md`：PKCE 参数检查
- `scope-checklist.md`：最小权限检查
- `bug-report-template.md`：脱敏中文问题报告

### scripts/

- `check_oauth_flow.py`：本地参数验证和可选的无凭据 HEAD 检查

### assets/

- `oauth-flow-diagram.txt`：可复制到工单的 ASCII 流程图
