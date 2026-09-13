# Plan: レビューパス

- 参照する spec: spec/review-pass.md
- 承認: リポジトリ作者
- 作成方法: Claude Code の plan mode で生成し、スコープを人が絞り込んだ

## 変更するファイル

- REVIEW.md（新規）— レビューの基準。3パス、Important と nit の線引き、nit の上限、除外パス
- .claude/agents/verifier.md（新規）— 基準を適用するサブエージェント。Edit と Write を持たせない
- docs/phases.md（更新）— Phase 2 の一覧から実装済みの2項目を落とす
- README.md（更新）— 制御の表に2ファイルを追加し、「Phase 1 に入っていないもの」から REVIEW.md を外す

Python コードには触れない。claims_api/ と tests/ に差分は出ない。

## 作業順

1. REVIEW.md を書く。基準が先で、実行者は後。verifier は REVIEW.md を参照するだけの薄い器にするため、参照先が存在しない状態で verifier を書かない。
2. .claude/agents/verifier.md を書く。ツールは Bash / Read / Grep / Glob のみ。
3. docs/phases.md と README.md を実態に合わせる。
4. make test / make lint / scripts/check-endpoints.sh を流し、Python に差分が無いことを出力で確認する。

## リスク

- ドキュメントが実態より進んで見える。この変更で置かれるのは基準であって、基準が守られる保証ではない（spec CONCERN-2）。README と phases.md で「レビューとゲートが入った」と読めてしまうと、ブランチ保護が無いことが見えなくなる。したがって phases.md には残り4項目を未実装として明示的に残し、REVIEW.md 自身にも助言的な制御である旨を書く。
- nit の上限が形骸化する。上限は数字だけ書いても守られないため、verifier の手順に「3件で打ち切る」と動作として書く。
- 除外パスに claims_api/legacy_v1/ を入れたくなる。凍結パスなので触らないはず、という理屈は逆で、ここに差分があること自体がパス3の Important 所見である。除外すると凍結の破れが見えなくなる。除外しない。

## 採らなかった選択肢

- レビュー基準を CLAUDE.md に直接書く。却下：CLAUDE.md は毎セッション読み込まれる文脈であり、レビュー時にしか要らない基準で膨らませたくない。また将来の PR ワークフローから参照するとき、リポジトリ直下の REVIEW.md のほうが素直である。
- verifier に Edit を持たせ、所見をその場で直させる。却下：レビューした本人が直せる経路を残すと、intent が問題としている「書いた本人が承認している」状態に戻る。
- verifier を作らず REVIEW.md だけ置く。却下：基準はあるが適用する主体が決まらず、結局セッションごとの運用に戻る（spec R5）。

## 何をもって完了とするか

- REVIEW.md が spec R1 の3パス、R2 の線引き、R3 の上限、R4 の除外パスをすべて含んでいること。
- .claude/agents/verifier.md が Edit と Write を持たないこと（spec R5 と C2）。
- docs/phases.md の Phase 2 に、未実装の4項目だけが残っていること。
- make test が 11 passed、make lint が All checks passed!、scripts/check-endpoints.sh が指摘なしであること。
