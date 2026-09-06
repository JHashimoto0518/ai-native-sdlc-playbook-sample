"""claims-core API のクライアント.

claims-core は 50 rps でレートリミットされており、オペレーターデスクトップ
と共有されている（plan/claims-status.md のリスク欄）。ポータルからの
トラフィックを一対一で通すわけにいかないため、読み取りは短い TTL の
キャッシュを経由する。

このキャッシュは最適化ではなく制御である。外すと、より重要な利用者である
オペレーター側が劣化する。
"""

from __future__ import annotations

import time
from typing import Any, Callable

CACHE_TTL_SECONDS = 30.0

# 上流サービスの代役。実際のクライアントは HTTP 呼び出しを行う。
_FIXTURES: dict[str, dict[str, Any]] = {
    "CLM-1001": {
        "claim_id": "CLM-1001",
        "customer_id": "cust-1",
        "customer_name": "J. Ortiz",
        "customer_address": "12 Beech Row",
        "state": "received",
        "next_step": "査定日程を調整中",
        "expected_date": "2026-06-09",
    },
    "CLM-1002": {
        "claim_id": "CLM-1002",
        "customer_id": "cust-1",
        "customer_name": "J. Ortiz",
        "customer_address": "12 Beech Row",
        "state": "assessing",
        "next_step": "査定人が訪問予定",
        "expected_date": "2026-06-12",
    },
    "CLM-1003": {
        "claim_id": "CLM-1003",
        "customer_id": "cust-1",
        "customer_name": "J. Ortiz",
        "customer_address": "12 Beech Row",
        "state": "awaiting_documents",
        "next_step": "修理見積書のアップロード待ち",
        "expected_date": "2026-06-16",
    },
    "CLM-1004": {
        "claim_id": "CLM-1004",
        "customer_id": "cust-2",
        "customer_name": "R. Bell",
        "customer_address": "4 Kiln Lane",
        "state": "settled",
        "next_step": "支払い済み",
        "expected_date": "2026-06-04",
    },
}


def _fetch(claim_id: str) -> dict[str, Any] | None:
    return _FIXTURES.get(claim_id)


class ClaimsCoreClient:
    def __init__(
        self,
        fetch: Callable[[str], dict[str, Any] | None] = _fetch,
        ttl: float = CACHE_TTL_SECONDS,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._fetch = fetch
        self._ttl = ttl
        self._clock = clock
        self._cache: dict[str, tuple[float, dict[str, Any] | None]] = {}

    def get_claim(self, claim_id: str) -> dict[str, Any] | None:
        now = self._clock()
        hit = self._cache.get(claim_id)
        if hit is not None and now - hit[0] < self._ttl:
            return hit[1]
        record = self._fetch(claim_id)
        self._cache[claim_id] = (now, record)
        return record
