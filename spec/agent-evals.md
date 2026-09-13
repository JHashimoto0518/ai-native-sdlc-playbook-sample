# Spec: エージェント設定の回帰テスト

- 参照する intent: intent/agent-evals.md（2026-09-13 に受理）
- レビュー: リポジトリ作者
- 適用した Skill: なし（API エンドポイントを変更しないため secure-api-review の対象外）

## 要件

- **R1** 決定的な制御に対する回帰テストを `evals/` に置く。`tests/` とは分ける。
- **R2** `make evals` で実行でき、違反があれば非ゼロで終了する。
- **R3** `CLAUDE.md`、`.claude/**`、`scripts/**`、`evals/**`、`Makefile`、ワークフロー自身のいずれかに差分が出たとき CI で走る。
- **R4** eval は対象の制御を実際に実行して観測する。ファイルの文字列一致で済ませない。
- **R5** 既知の穴は、通る eval ではなく「失敗することを期待する eval」として記録する。

## 設計

### 置き場所（R1）

    evals/                  エージェントを制御する設定の回帰テスト
    tests/                  claims_api/ の検証

`pyproject.toml` の `testpaths` は `tests` のまま変えない。`make test` の出力は 11 passed のままであり、eval は `make evals` が `pytest evals -q` を明示して走らせる。

分ける理由は対象が違うためである。`tests/` が落ちたときに壊れているのは請求ステータスの挙動で、`evals/` が落ちたときに壊れているのはガードレールである。混ぜると、どちらが壊れたのかを出力から読めなくなる。

### 何を測るか（R4）

| 対象の制御 | 測り方 | 根拠 |
|---|---|---|
| `.claude/hooks/protect-paths.sh` | PreToolUse の JSON を stdin に与えて実行する。凍結パスで exit 2、v2 のパスで exit 0 | CLAUDE.md の凍結 |
| `scripts/check-endpoints.sh` | 違反を仕込んだツリーを一時ディレクトリに作り、スクリプトを複製して実行する。非ゼロと指摘文言 | spec/claims-status.md の条項4と条項1 |
| `.claude/agents/verifier.md` | front matter の `tools` を読む | spec/review-pass.md R5 |
| `CLAUDE.md` のコマンド | 記載された make ターゲットが `Makefile` に存在する | CLAUDE.md の「コマンド」節 |

`check-endpoints.sh` は `cd "$(dirname "$0")/.."` で自分の位置からリポジトリ根を決める。したがって作業ディレクトリを変えても対象は変えられない。一時ディレクトリに `scripts/` を作ってスクリプトを複製し、その隣に違反ツリーを置くことで、本物のスクリプトを本物どおりに走らせる。

verifier の `tools` だけは記述を読む。宣言的な設定であり、実行して観測する手段がサブエージェントの起動しかないためで、R4 の唯一の例外とする。

### 既知の穴の記録（R5）

`.claude/settings.json` の PreToolUse matcher は `Edit|Write` のみで、`protect-paths.sh` は `tool_input.file_path` を読む。したがって Bash 経由の書き込み（`sed -i`、リダイレクト）は凍結パスであっても捕捉されない。`spec/review-pass.md` のスコープ外に挙げた件である。

これを `xfail(strict=True)` の eval として置く。現状は失敗するため xfail として記録され、CI は緑のままになる。穴が塞がれた瞬間に XPASS で CI が落ち、この eval と spec を更新させる。

通る eval にすると穴が仕様に見え、書かなければ穴が見えなくなる。intent の未解決の問いに対する回答がこれである。

### CI（R3）

`.github/workflows/agent-evals.yml`。`push` と `pull_request` で、上記パスに差分があるときに限り起動する。`make setup` のあと `make evals` を走らせる。

起動条件にはワークフロー自身も含める。含めないと、起動条件や実行手順を変える差分が、その変更後の条件で一度も走らないまま入る。

`claims_api/` の変更では起動しない。制御が変わっていないのに制御の回帰テストを回す理由が無く、起動条件を広げると「いつも走っているもの」になって差分との対応が読めなくなる。

## intent から引き継いだ制約

- **C1** 新しい依存を追加しない。`pytest` は既に `requirements.txt` にあり、eval はそれと標準ライブラリだけで書く。`requirements.txt` に差分を出さないことで担保する。
- **C2** eval が測れるのは決定的な制御だけである。助言的な制御（skill、`CLAUDE.md`、`REVIEW.md`）を eval で担保したことにしない。`evals/` 自身の冒頭と本 spec の CONCERN-1 に明記して担保する。

## 懸念事項（flag）

- CONCERN-1（open、担当: リポジトリ作者）。モデルを呼ぶ eval が無い。skill や `CLAUDE.md` がセッションの出力を実際に変えているかは、この spec では測れていない。測るには API キーと新しい依存が要り、C1 と衝突する。したがって本変更は「決定的な制御の劣化を検知する」ところまでであり、「エージェントが指示に従う」ことは検証しない。
- CONCERN-2（open）。`.github/workflows/` の最初の1本がこれになる。Phase 2 の `claude-code-action` が未実装のため、CI に載るのは eval だけで、レビューパスは載らない。また Actions が有効かはリポジトリ設定の話で、リポジトリの中身では担保できない。ワークフローを置いたことと、CI が回っていることは別である。

## スコープ外

Phase 3 の残り2項目、すなわち `bands.yaml` と決定的な検知スクリプト、および書き戻し。

Phase 2 の残り4項目。本変更は `.github/workflows/` を新設するが、`claude-code-action` のワークフローはここには含まない。
