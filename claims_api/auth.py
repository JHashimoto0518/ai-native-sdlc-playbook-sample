"""ゲートウェイ JWT の検証.

intent が新しい ID プロバイダの追加を禁じているため、ポータルが既に
持っているゲートウェイのトークンを再利用する。このサンプルを自己完結
させるため検証はスタブにしてあるが、実サービスではゲートウェイの公開鍵
による検証に委譲する。
"""

from __future__ import annotations

from dataclasses import dataclass


class AuthError(Exception):
    """呼び出し元を特定できないときに送出する。"""


@dataclass(frozen=True)
class Caller:
    customer_id: str


# ゲートウェイが発行するトークンの代役。
_KNOWN_TOKENS = {
    "tok-cust-1": Caller(customer_id="cust-1"),
    "tok-cust-2": Caller(customer_id="cust-2"),
}


def require_gateway_jwt(authorization: str | None) -> Caller:
    """呼び出し元を返す。特定できなければ AuthError を送出する。

    受け付けるのは `Authorization: Bearer <token>` の形式のみ。
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthError("bearer トークンがない")
    token = authorization[len("Bearer ") :].strip()
    caller = _KNOWN_TOKENS.get(token)
    if caller is None:
        raise AuthError("未知のトークン")
    return caller
