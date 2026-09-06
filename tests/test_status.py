"""plan/claims-status.md に対する検証.

各テストは、それが何を証明しているか（spec の要件番号や制約番号）を
名前とコメントに書いてある。レビュアーが差分を spec と突き合わせるとき、
経緯を推測し直さずに済むようにするため。
"""

from __future__ import annotations

import pytest

from claims_api.app import create_app
from claims_api.core.claims_core import ClaimsCoreClient
from claims_api.routes.status import RESPONSE_FIELDS


@pytest.fixture
def client():
    return create_app().test_client()


AUTH_CUST_1 = {"Authorization": "Bearer tok-cust-1"}
AUTH_CUST_2 = {"Authorization": "Bearer tok-cust-2"}


# --- spec R3: 4つの状態を表現できること ------------------------------------


@pytest.mark.parametrize(
    ("claim_id", "state"),
    [
        ("CLM-1001", "received"),
        ("CLM-1002", "assessing"),
        ("CLM-1003", "awaiting_documents"),
    ],
)
def test_所有する請求の状態を返す(client, claim_id, state):
    response = client.get(f"/v2/claims/{claim_id}/status", headers=AUTH_CUST_1)
    assert response.status_code == 200
    assert response.json["state"] == state
    assert response.json["next_step"]
    assert response.json["expected_date"]


def test_settled状態を返す(client):
    response = client.get("/v2/claims/CLM-1004/status", headers=AUTH_CUST_2)
    assert response.status_code == 200
    assert response.json["state"] == "settled"


# --- intent 制約 C1: ポータルに新たな個人情報を持ち込まない -----------------


def test_許可リスト外のフィールドを返さない(client):
    response = client.get("/v2/claims/CLM-1001/status", headers=AUTH_CUST_1)
    assert set(response.json) == set(RESPONSE_FIELDS)


def test_顧客の識別情報を返さない(client):
    response = client.get("/v2/claims/CLM-1001/status", headers=AUTH_CUST_1)
    body = response.get_data(as_text=True)
    assert "J. Ortiz" not in body
    assert "Beech Row" not in body
    assert "customer_id" not in response.json


# --- intent 制約 C2: 認証は既存のもののみ -----------------------------------


def test_トークンなしのリクエストを拒否する(client):
    response = client.get("/v2/claims/CLM-1001/status")
    assert response.status_code == 401


def test_未知のトークンのリクエストを拒否する(client):
    response = client.get(
        "/v2/claims/CLM-1001/status", headers={"Authorization": "Bearer nope"}
    )
    assert response.status_code == 401


# --- spec R4: 他人の請求は存在しない請求と区別がつかないこと ----------------


def test_他人の請求は存在しない請求と同じ応答になる(client):
    owned = client.get("/v2/claims/CLM-1004/status", headers=AUTH_CUST_2)
    not_owned = client.get("/v2/claims/CLM-1004/status", headers=AUTH_CUST_1)
    absent = client.get("/v2/claims/CLM-9999/status", headers=AUTH_CUST_1)

    assert owned.status_code == 200
    assert not_owned.status_code == 404
    assert not_owned.json == absent.json
    assert not_owned.status_code == absent.status_code


# --- spec C3: claims-core への読み取りをキャッシュすること ------------------


def test_TTL内の再読み込みはclaims_coreを一度しか呼ばない():
    calls: list[str] = []

    def counting_fetch(claim_id: str):
        calls.append(claim_id)
        return {"claim_id": claim_id, "customer_id": "cust-1", "state": "received"}

    now = [1000.0]
    core = ClaimsCoreClient(fetch=counting_fetch, ttl=30.0, clock=lambda: now[0])

    core.get_claim("CLM-1001")
    now[0] += 5.0
    core.get_claim("CLM-1001")

    assert len(calls) == 1, "キャッシュは制御である。claims-core はレートリミットされている"


def test_TTL経過後はclaims_coreから読み直す():
    calls: list[str] = []

    def counting_fetch(claim_id: str):
        calls.append(claim_id)
        return {"claim_id": claim_id, "customer_id": "cust-1", "state": "received"}

    now = [1000.0]
    core = ClaimsCoreClient(fetch=counting_fetch, ttl=30.0, clock=lambda: now[0])

    core.get_claim("CLM-1001")
    now[0] += 31.0
    core.get_claim("CLM-1001")

    assert len(calls) == 2
