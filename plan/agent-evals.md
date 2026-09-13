# Plan: エージェント設定の回帰テスト

- 参照する spec: spec/agent-evals.md
- 承認: リポジトリ作者
- 作成方法: Claude Code のセッションで生成し、スコープを人が絞り込んだ

## 変更するファイル

- evals/__init__.py（新規）— パッケージ化。tests/ に合わせる
- evals/test_controls.py（新規）— 決定的な制御の回帰テスト（spec R1、R4、R5）
- .github/workflows/agent-evals.yml（新規）— 起動条件を制御のパスに絞った CI（spec R3）
- Makefile（更新）— evals ターゲットを追加（spec R2）
- CLAUDE.md（更新）— 「コマンド」節に make evals を追加
- README.md（更新）— 制御の表に2ファイルを追加
- docs/phases.md（更新）— Phase 3 の一覧から実装済みの1項目を「入ったもの」へ移す

`claims_api/` と `tests/` には触れない。`requirements.txt` にも差分を出さない（spec C1）。

## 作業順

1. evals/test_controls.py を書く。先に eval を書き、対象の制御には手を入れない。制御が既に正しいことを確認する側であって、eval に合わせて制御を動かす側ではない。
2. Makefile に evals ターゲットを足す。`pytest evals -q` を明示し、`pyproject.toml` の testpaths は変えない。make test の出力を 11 passed のまま保つため。
3. eval を流し、意図した7件が通り、xfail が1件記録されることを出力で確認する。
4. .github/workflows/agent-evals.yml を書く。paths を spec R3 の5つに絞る。
5. CLAUDE.md、README.md、docs/phases.md を実態に合わせる。
6. make test / make lint / make evals / scripts/check-endpoints.sh を流して出力を貼る。

## リスク

- **eval が制御を追認するだけになる。** 制御の実装を読んでから eval を書くと、実装の現状をそのまま期待値に写すことになり、劣化は検知できても設計との乖離は検知できない。したがって期待値は spec と CLAUDE.md の記述から取る。`protect-paths.sh` の case 文ではなく CLAUDE.md の「凍結されており、hook が書き込みをブロックする」から、exit 2 を期待する。
- **xfail が忘れられる。** strict=True にしないと、穴が塞がれても XPASS が黙って通り、eval が古いまま残る。strict=True で XPASS を失敗にし、塞いだ人に必ずこのファイルを開かせる。
- **CI の起動条件が広がる。** paths を足すのは簡単で、いずれ `claims_api/**` まで含めたくなる。含めると eval は「いつも走っているもの」になり、赤くなったとき何の制御が壊れたのかを差分から読めなくなる。起動条件を広げるときは spec R3 を先に更新する。
- **ワークフローが動いて見える。** リポジトリに YAML があることと、GitHub 上で Actions が有効であることは別である（spec CONCERN-2）。README と phases.md では「CI に載せた」ではなく「ワークフローを置いた」と書く。

## 採らなかった選択肢

- eval を `tests/` に混ぜる。却下：落ちたときに請求ステータスの挙動が壊れたのか、ガードレールが壊れたのかを出力から区別できない。`make test` の「11 passed」という CLAUDE.md の目印も動く。
- `pyproject.toml` の `testpaths` に `evals` を足して `make test` で両方走らせる。却下：上と同じ理由に加え、CLAUDE.md が「末尾が N passed で終わること」と書いている数字が変わり、既存の記述を無効にする。
- モデルを呼ぶ eval を含める。却下：新しい依存と API キーが要り、intent の制約と衝突する。CONCERN-1 として開いたまま残す。
- 既知の穴（Bash 経由の書き込み）をこの変更で塞ぐ。却下：`spec/review-pass.md` が明示的にスコープ外とした件であり、別途判断する。ここでは xfail で見えるようにするに留める。
- `.claude/settings.json` の matcher に `Bash` を足す。却下：同上。加えて eval の変更のついでに制御の挙動を変えると、この差分が何を検証したのか読めなくなる。

## 何をもって完了とするか

- `evals/test_controls.py` が spec の表の4対象をすべて覆っていること（R4）。
- `make evals` が非ゼロで落ちうること、かつ現状では通ること（R2）。
- 既知の穴が xfail(strict=True) として1件記録されていること（R5）。
- `.github/workflows/agent-evals.yml` の paths が spec R3 の6つ（ワークフロー自身を含む）であること。
- make test が 11 passed、make lint が All checks passed!、scripts/check-endpoints.sh が指摘なしであること。
