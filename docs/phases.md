# このリポジトリにまだ入っていないもの

Phase 1 では要求を1本だけ端から端まで通しています。プレイブックの残りのプレイをここに列挙しておくことで、抜けが「見えない欠落」ではなく「意図的な未実装」であることを明示します。

## Phase 2 — レビューとゲート（Stage 5: Deploy）

6項目のうち2項目が入りました。成果物の連鎖は `intent/review-pass.md` → `spec/review-pass.md` → `plan/review-pass.md` です。

入ったもの:

- リポジトリ直下の `REVIEW.md`。レビューのパス（bugs / security / spec と plan への適合）、Important と nit の線引き、nit の上限、除外するパス。
- `.claude/agents/` の verifier サブエージェント。Edit と Write を持たないため、自分が指摘した箇所を自分で直せません。

まだ入っていないもの:

- `claude-code-action` のワークフロー。すべての PR に同じレビューパスを通す。
- レビューコメントに対する `@claude` の修正ループ。
- 承認ゲートとしての hook。リリース承認のないまま本番デプロイをブロックする。
- ブランチ保護と CODEOWNERS。コードを書いたエージェントが自分で承認する経路をなくす。

**この4項目が残っている間、Phase 2 は完成していません。** `REVIEW.md` も verifier も助言的な制御でしかなく、マージそのものを止める仕組みはまだありません。所見は無視できます（`spec/review-pass.md` の CONCERN-2）。基準を置いたことと、基準が守られることは別です。

## Phase 3 — ループを閉じる（Stage 4 と Stage 6）

3項目のうち1項目が入りました。成果物の連鎖は `intent/agent-evals.md` → `spec/agent-evals.md` → `plan/agent-evals.md` です。

入ったもの:

- `evals/` の eval スイートと `.github/workflows/agent-evals.yml`。`CLAUDE.md`、`.claude/**`、`scripts/**` が変わったときだけ走ります。エージェントを制御する設定にも、コードと同じ回帰テストを課すという考え方です。既知の穴は `xfail(strict=True)` として記録してあり、塞いだ時点で CI が落ちて成果物の更新を促します。

まだ入っていないもの:

- `bands.yaml` と決定的な検知スクリプト。1σ はログのみ、2σ は読み取り専用で診断、3σ で PR の起票または事前承認済み runbook の実行を許す。
- 書き戻し。診断結果を次の `intent/*.md` にする。これがあってはじめて、この工程は直線ではなくループになる。

**この2項目が残っている間、Phase 3 は完成していません。** 入ったのは「制御が劣化したら気づく」ところまでで、運用の観測から次の要求が生まれる経路はまだありません。工程は依然として直線です。

また eval が測れるのは決定的な制御だけです。skill や `CLAUDE.md` が実際にセッションの出力を変えているかは検証していません（`spec/agent-evals.md` の CONCERN-1）。ワークフローを置いたことと、GitHub 上で CI が回っていることも別です（CONCERN-2）。

## どのフェーズでも扱わないもの

Claude Security の定期スキャンと Claude Tag のオンコールは、リポジトリの中身ではなくホステッドサービスです。managed settings もプラットフォームチームが MDM や管理コンソールから配布するものです。記事の managed settings の例は読む価値がありますが、設計上プロジェクトリポジトリには置けません。置けないことがそもそもの狙いだからです。
