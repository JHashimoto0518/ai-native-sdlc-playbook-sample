#!/usr/bin/env bash
# PreToolUse のガードレール。凍結パスへの編集をブロックする。
# exit 2 で操作を中断し、標準エラーに書いたメッセージが Claude に返る。
set -uo pipefail

input=$(cat)
path=$(printf '%s' "$input" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("tool_input",{}).get("file_path",""))' 2>/dev/null)

case "$path" in
  *claims_api/legacy_v1/*)
    echo "claims_api/legacy_v1/ は凍結されています。v2 側のパスで変更してください。本当に v1 に入れるべき変更であれば、intent.md の起票とプラットフォームチームの承認が必要です。" >&2
    exit 2
    ;;
esac
exit 0
