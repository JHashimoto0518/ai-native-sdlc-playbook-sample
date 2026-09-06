"""GET /v2/claims/<claim_id>/status.

読み取り専用のため監査イベントは発行しない（secure-api-review 条項3）。
レスポンスは許可リストから組み立てるので、claims-core が持つ、あるいは
将来追加するフィールドがポータルのセッションに漏れることはない
（intent の制約: ポータルに新たな個人情報を持ち込まない）。
"""

from __future__ import annotations

import re
from typing import Any

from flask import Blueprint, jsonify, request

from claims_api.auth import AuthError, require_gateway_jwt
from claims_api.core.claims_core import ClaimsCoreClient

bp = Blueprint("status", __name__)

CLAIM_ID_PATTERN = re.compile(r"^CLM-\d{4}$")

# 許可リスト。ここに書かれていないフィールドはサービスの外へ出ない。
RESPONSE_FIELDS = ("claim_id", "state", "next_step", "expected_date")

_client = ClaimsCoreClient()


def _project(record: dict[str, Any]) -> dict[str, Any]:
    return {field: record[field] for field in RESPONSE_FIELDS}


@bp.get("/v2/claims/<claim_id>/status")
def get_claim_status(claim_id: str):
    try:
        caller = require_gateway_jwt(request.headers.get("Authorization"))
    except AuthError:
        return jsonify({"error": "unauthorized"}), 401

    if not CLAIM_ID_PATTERN.match(claim_id):
        return jsonify({"error": "not found"}), 404

    record = _client.get_claim(claim_id)

    # 他人が所有する請求は、存在しない請求とまったく同じ応答にする。
    # これにより claim id の列挙にこのエンドポイントを使えなくする。
    if record is None or record["customer_id"] != caller.customer_id:
        return jsonify({"error": "not found"}), 404

    return jsonify(_project(record)), 200
