"""凍結中。編集しないこと。

v1 の請求ステータス射影は、個人情報の許可リストを導入する前のもの。
処理中のポータルセッションを壊さないためだけに残している。
.claude/hooks/protect-paths.sh がこのパッケージへの書き込みをブロックする。
新しい作業は claims_api/routes/ 側の v2 パスで行うこと。
"""

LEGACY_STATUS_FIELDS = (
    "claim_id",
    "customer_name",
    "state",
)
