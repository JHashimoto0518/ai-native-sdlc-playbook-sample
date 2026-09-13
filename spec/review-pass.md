# Spec: レビューパス

- 参照する intent: intent/review-pass.md（2026-09-13 に受理）
- レビュー: リポジトリ作者
- 適用した Skill: なし（API エンドポイントを変更しないため secure-api-review の対象外）

## 要件

- **R1** レビューは3本のパスからなる: bugs / security / spec と plan への適合。
- **R2** 所見を Important と nit に分ける。Important はマージを止め、nit は止めない。
- **R3** 1レビューあたりの nit に上限を設ける。
- **R4** レビュー対象から除外するパスを明示する。
- **R5** 差分を書いたセッション以外がレビューを実行できる経路を用意する。

## 設計

2つのファイルに分ける。

    REVIEW.md               リポジトリ直下。レビューの基準
    .claude/agents/verifier.md   その基準を適用する実行者

基準（REVIEW.md）と実行者（verifier）を分けるのは、基準を読む相手が Claude だけではないためである。人間のレビュアーも、将来の PR ワークフローも同じファイルを読む。基準をエージェント定義の中に埋めると、Claude 以外から参照できなくなる。

CLAUDE.md に直接書かない理由は「採らなかった選択肢」として plan に記す。

### レビューパス（R1）

パス3が、このリポジトリに固有のものである。差分のすべての変更が intent/ spec/ plan/ のいずれかに辿れるかを見る。辿れない変更は、それ自体が良い変更であっても Important とする。成果物を先に更新させるためで、CLAUDE.md の「すべての変更はそのいずれかの成果物から始める」を、レビューの時点でもう一度検査することになる。

パス2は既存の .claude/skills/secure-api-review/SKILL.md の5条項をそのまま適用する。レビュー用に基準を書き直さない。二重管理になり、いずれ食い違うため。

### verifier の権限（R5）

verifier には読み取り専用のツールだけを与える。Edit と Write を持たせない。

自分が指摘した箇所を自分で直せないことが、この器の要点である。直せるなら、レビューと実装が同じ主体に戻り、intent が問題としている「書いた本人が承認している」状態に戻る。

## intent から引き継いだ制約

- **C1** レビュー基準はリポジトリの中に置く。REVIEW.md をリポジトリ直下のコミット対象とすることで担保する。セッションの記憶やプロンプトの書き方には置かない。
- **C2** 助言的な制御と決定的な制御を混同しない。REVIEW.md と verifier がいずれも助言的であることを、両ファイル自身に明記して担保する。

## 懸念事項（flag）

- CONCERN-1（open、担当: リポジトリ作者）。verifier は助言的な制御でしかない。skill と同じく、適用される確率を上げるだけで遵守を強制できない。決定的な裏付けは make test / make lint / scripts/check-endpoints.sh の側にあり、verifier はそれらを実行して出力を引用するに留まる。
- CONCERN-2（open、intent の未解決の問いから引き継ぎ）。ゲートが無いため、verifier の所見は親セッションが無視できる。真のゲートはブランチ保護と CODEOWNERS で、いずれも今回のスコープ外。したがって本変更は「基準を置いた」ところまでであり、「基準が守られる」ことは保証しない。この差を README や phases.md で曖昧にしないこと。

## スコープ外

docs/phases.md が挙げる Phase 2 の残り4項目、すなわち claude-code-action のワークフロー、`@claude` の修正ループ、承認ゲートとしての hook、ブランチ保護と CODEOWNERS。

.claude/settings.json の PreToolUse matcher が Edit|Write のみで Bash 経由の書き込みを捕捉できない件も、本 spec のスコープ外とする（別途判断する）。
