#!/usr/bin/env bash
# secure-api-review skill に対する決定的なバックストップ。
#
# skill は助言的な制御でしかない。ポリシーが適用される「可能性を高める」
# だけで、セッションに遵守を強制はできない。このスクリプトはその条項の
# うちひとつを機械的に検査可能にするもので、違反があれば非ゼロで終了する。
set -uo pipefail
cd "$(dirname "$0")/.."

status=0

# 条項4: レスポンスの射影は許可リストであること。素通しにしない。
if grep -rn "jsonify(record)\|return record\b" claims_api/routes/ >/dev/null 2>&1; then
  echo "指摘: 上流のレコードをそのまま返しているルートがある（skill 条項4）。"
  status=1
fi

# 条項1: すべてのルートモジュールが認証ヘルパーを参照していること。
for f in claims_api/routes/*.py; do
  case "$(basename "$f")" in __init__.py) continue ;; esac
  if ! grep -q "require_gateway_jwt" "$f"; then
    echo "指摘: $f に require_gateway_jwt を通さないルートがある（条項1）。"
    status=1
  fi
done

if [ "$status" -eq 0 ]; then
  echo "check-endpoints: 指摘なし。"
fi
exit "$status"
