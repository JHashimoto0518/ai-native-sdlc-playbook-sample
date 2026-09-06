# claims-api

保険金請求ステータスのセルフサービス化。このコードが存在する理由は intent/、spec/、plan/ にある。すべての変更はそのいずれかの成果物から始める。

## コマンド

- セットアップ: make setup（.venv を作り requirements.txt を入れる）
- テスト: make test（pytest。末尾が "N passed" で終わること）
- Lint: make lint（ruff。"All checks passed!" と出ること）

## 作業の検証

タスクを完了と報告する前に `make test` と `make lint` を実行し、その出力を貼ること。テストが失敗したら、テストではなくコードを直すこと。

## 規約

- Python 3.11 以上。標準ライブラリと Flask のみ。依存を追加する場合は先に spec/ を更新すること。
- 外部公開するエンドポイントは claims_api/routes/ に置き、claims_api/app.py で登録する。
- レスポンスは許可リストによる射影で組み立てる。claims-core のレコードをそのまま返さないこと。
- 日付は ISO 8601 の文字列（YYYY-MM-DD）で扱う。datetime オブジェクトをそのまま返さない。

## アーキテクチャ

- claims_api/routes/ — HTTP 層。業務ルールを置かない
- claims_api/core/ — claims-core クライアントと TTL キャッシュ
- claims_api/auth.py — ゲートウェイ JWT の検証。全ルートで共用
- claims_api/legacy_v1/ — 凍結中。下記参照

## Claude が間違えやすいこと

- claims_api/legacy_v1/ を編集しないこと。このパッケージは凍結されており、hook が書き込みをブロックする。新しい作業は v2 側で行う。
- routes/status.py のレスポンス射影を「claims-core が返したものすべて」に広げないこと。許可リストは定型句ではなく制御である。
- テストを通すために core/claims_core.py のキャッシュを外さないこと。claims-core は 50 rps でレートリミットされている（plan/claims-status.md のリスク欄）。
