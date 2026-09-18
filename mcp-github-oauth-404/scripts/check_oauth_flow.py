#!/usr/bin/env python3
"""Safely inspect GitHub OAuth + PKCE URL configuration for MCP login 404s.

The program does not accept client secrets, tokens, authorization codes, or
PKCE verifiers. It never starts an OAuth flow or calls a token exchange endpoint.
"""

from __future__ import annotations

import argparse
import sys
from http.client import HTTPResponse
from typing import NoReturn
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

GITHUB_AUTHORIZE_ENDPOINT = "https://github.com/login/oauth/authorize"
SENSITIVE_QUERY_KEYS = {
    "access_token",
    "client_secret",
    "code",
    "code_verifier",
    "id_token",
    "refresh_token",
    "state",
    "token",
}
DISALLOWED_ARGUMENT_NAMES = {
    "--access-token",
    "--client-secret",
    "--code",
    "--code-verifier",
    "--refresh-token",
    "--token",
}


def mask_client_id(value: str) -> str:
    """Return a stable but non-reversible display version of a client ID."""
    return f"{value[:4]}****" if value else "<REDACTED>"


def fail(message: str) -> NoReturn:
    print(f"[错误] {message}", file=sys.stderr)
    raise SystemExit(2)


def reject_sensitive_arguments(argv: list[str]) -> None:
    """Reject sensitive option names before argparse can accidentally accept them."""
    for item in argv:
        option = item.split("=", 1)[0]
        if option in DISALLOWED_ARGUMENT_NAMES:
            fail(f"不接受敏感参数 {option}。本工具不会处理 secret、token、授权码或 verifier。")


def strip_query_and_fragment(uri: str) -> str:
    parts = urlsplit(uri)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def validate_redirect_uri(uri: str) -> tuple[bool, list[str]]:
    """Perform local-only format validation; no request is sent."""
    notes: list[str] = []
    parts = urlsplit(uri)

    if not parts.scheme or not parts.netloc:
        return False, ["redirect_uri 必须是绝对 URL，包含协议和主机名。"]
    if parts.username or parts.password:
        return False, ["redirect_uri 不能包含用户名或密码。"]
    if parts.scheme != "https" and parts.hostname not in {"localhost", "127.0.0.1", "::1"}:
        notes.append("警告：非 localhost 的 redirect_uri 通常应使用 HTTPS。")
    if parts.fragment:
        notes.append("警告：redirect_uri 不应包含 #fragment；OAuth 服务端不会接收 fragment。")
    if "ark_stg" in parts.path:
        notes.append("提示：路径包含 ark_stg；请核对 stg/prod 环境与回调路由是否一致。")
    if parts.query:
        unsafe = [key for key, _ in parse_qsl(parts.query, keep_blank_values=True) if key.lower() in SENSITIVE_QUERY_KEYS]
        if unsafe:
            notes.append("警告：redirect_uri 查询参数含敏感名称；请勿分享或复用其中内容。")
        else:
            notes.append("提示：callback 注册值通常要求精确匹配；请确认查询参数是否是配置的一部分。")
    return True, notes


def build_display_authorize_url(client_id: str, redirect_uri: str, scope: str) -> str:
    """Build a redacted display-only URL; it is never requested."""
    parameters = {
        "client_id": mask_client_id(client_id),
        "redirect_uri": strip_query_and_fragment(redirect_uri),
        "scope": scope,
        "code_challenge": "<REDACTED>",
        "code_challenge_method": "S256",
        "state": "<REDACTED>",
    }
    return f"{GITHUB_AUTHORIZE_ENDPOINT}?{urlencode(parameters)}"


def head_request(url: str, label: str) -> None:
    """Run a credential-free HEAD request and report only status-level details."""
    request = Request(url, method="HEAD", headers={"User-Agent": "mcp-github-oauth-404-check/1.0"})
    try:
        with urlopen(request, timeout=10) as response:
            _report_response(label, response)
    except HTTPError as error:
        print(f"[{label}] HTTP {error.code} {error.reason}")
    except URLError as error:
        print(f"[{label}] 网络错误：{error.reason}")
    except TimeoutError:
        print(f"[{label}] 请求超时（10 秒）")


def _report_response(label: str, response: HTTPResponse) -> None:
    print(f"[{label}] HTTP {response.status} {response.reason}")


def ask_callback_confirmation(callback_uri: str) -> bool:
    print("\n[确认] 即将向以下 callback URI 发送无凭据 HEAD 请求：")
    print(f"  {callback_uri}")
    print("该请求不会携带 OAuth 参数、Cookie、token 或请求体。仅在你拥有或已获授权管理该服务时继续。")
    try:
        answer = input("确认继续？[y/N] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\n[跳过] 未获得确认，未请求 callback URI。")
        return False
    return answer in {"y", "yes"}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="本地检查 MCP GitHub OAuth 配置；不会进行授权或 token 兑换。"
    )
    parser.add_argument("--client-id", required=True, help="OAuth App 的 client_id（输出会掩码）")
    parser.add_argument("--redirect-uri", required=True, help="预期 callback URI")
    parser.add_argument("--scope", required=True, help='空格分隔的 scope，例如 "repo read:org"')
    parser.add_argument(
        "--check-github-endpoint",
        action="store_true",
        help="向 GitHub authorize 基础端点发送无参数 HEAD 请求",
    )
    parser.add_argument(
        "--check-callback-head",
        action="store_true",
        help="经交互确认后，向所提供 callback 的无查询参数 URI 发送 HEAD 请求",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    reject_sensitive_arguments(argv)
    args = parse_args(argv)

    if not args.client_id.strip():
        fail("client_id 不能为空。")
    if not args.scope.strip():
        fail("scope 不能为空。")
    if "," in args.scope:
        print("[警告] scope 通常应以空格分隔，而不是逗号。")

    valid_uri, notes = validate_redirect_uri(args.redirect_uri)
    if not valid_uri:
        for note in notes:
            print(f"[错误] {note}", file=sys.stderr)
        return 2

    print("[REDACTION NOTICE] 输出已避免 OAuth secret、token、授权码、verifier 和完整 state；分享前仍请人工审核。")
    print(f"[本地检查] client_id：{mask_client_id(args.client_id)}")
    print(f"[本地检查] redirect_uri（无查询参数）：{strip_query_and_fragment(args.redirect_uri)}")
    print(f"[本地检查] scope：{args.scope}")
    for note in notes:
        print(f"[本地检查] {note}")
    print("[本地检查] code_challenge_method：应为 S256")
    print("[本地检查] 授权 URL 预览（不会发送请求）：")
    print(build_display_authorize_url(args.client_id, args.redirect_uri, args.scope))

    if args.check_github_endpoint:
        print("\n[网络检查] GitHub authorize 基础端点（无查询参数）：")
        head_request(GITHUB_AUTHORIZE_ENDPOINT, "GitHub authorize")

    if args.check_callback_head:
        callback_uri = strip_query_and_fragment(args.redirect_uri)
        if ask_callback_confirmation(callback_uri):
            print("[网络检查] callback URI（无查询参数）：")
            head_request(callback_uri, "Callback")
        else:
            print("[跳过] 未请求 callback URI。")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
