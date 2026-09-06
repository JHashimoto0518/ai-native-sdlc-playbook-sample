# ai-native-sdlc-playbook-sample

Anthropic の [The AI-Native SDLC playbook](https://claude.com/blog/the-ai-native-sdlc-playbook)（Louis Claxton、2026年8月21日）に書かれている実践を、動くリポジトリの形にしたものです。

題材は記事自身の例をそのまま使っています。保険金請求のステータスを、顧客がコンタクトセンターに電話せずポータルで自分で確認できるようにする、というもの。題材そのものより、それがどの成果物の連鎖を通って実装に至るかが本題です。

Anthropic 公式のものではありません。記事を読んだ一個人が実践してみた結果です。

これは **Phase 1** です。要求を1本だけ端から端まで通すことで、リポジトリを大きくせずに成果物の連鎖が見えるようにしています。レビュー、承認ゲート、ループを閉じる部分は後続フェーズで扱います。

## まず何を読むか

このプレイブックの主眼は個別のファイルではありません。**各ステージが成果物をコミットして終わり、次のステージがそれを読んで始まる**こと、そして**コミットの連なりがそのまま監査証跡になる**ことです。なので、まず連鎖として読んでください。

| # | 成果物 | ステージ | 中身 |
|---|---|---|---|
| 1 | `intent/claims-status.md` | Plan | 起案者自身の言葉で書かれた要求と制約 |
| 2 | `spec/claims-status.md` | Design | 要件と設計を一度に。懸念事項は flag 付き |
| 3 | `plan/claims-status.md` | Build | 変更ファイル、作業順、リスク、完了条件 |
| 4 | `tests/test_status.py` | Test | 実装より先に書いた検証 |
| 5 | `claims_api/` | Build | 実装 |

次に、履歴としても読んでください。

```
git log --reverse --stat
```

各コミットが連鎖の1本の環になっています。たとえばレートリミットの制約を追いかけると、spec の制約 C3 として現れ、plan では名前の付いたリスクになり、最後は `test_TTL内の再読み込みはclaims_coreを一度しか呼ばない` に落ちます。

## 制御（コントロール）

| ファイル | 記事のプレイ | 種類 |
|---|---|---|
| `CLAUDE.md` | The CLAUDE.md（Stage 3） | 毎セッション読まれる文脈 |
| `.claude/skills/secure-api-review/SKILL.md` | Skills as institutional knowledge（Stage 3） | 助言的。ポリシーが適用される確率を上げる |
| `.claude/hooks/protect-paths.sh` | Hooks as build-time guardrails（Stage 3） | 決定的。違反をほぼ不可能にする |
| `scripts/check-endpoints.sh` | Skills の Governance considerations | skill の1条項に対する決定的なバックストップ |
| `Makefile` と CLAUDE.md の検証ブロック | Give Claude a feedback loop（Stage 4） | 人が見る前にエージェント自身が検証する |

skill と hook は意図的に対にしてあります。記事が言うとおり、skill は助言的で遵守を強制できないため、必ず守らせたいポリシーには決定的な裏付けが要ります。ここでは skill が「上流のレコードをそのまま返すな」と書き、`scripts/check-endpoints.sh` が実際に返しているルートがあればビルドを落とします。

## 制御が効くか試す

Claude Code に、ステータスのレスポンスへフィールドを1つ足すよう頼んでみてください。あるいは `claims_api/legacy_v1/` を編集するよう頼んでみてください。何が止めるかが見えます。

```
make setup
make test    # 11 passed
make lint    # All checks passed!
./scripts/check-endpoints.sh
```

## Phase 1 に入っていないもの

`REVIEW.md` と PR レビューのループ、承認ゲートとしての hook、CI/CD の配線、eval スイート、そして次の `intent.md` を書き出す監視バンド。これらは Phase 2 と Phase 3 です。`docs/phases.md` を参照してください。

## 制作について

このリポジトリは、Anthropic の記事 [The AI-Native SDLC playbook](https://claude.com/blog/the-ai-native-sdlc-playbook) を読み、そこに書かれている実践を手を動かして確かめるために作りました。

制作の流れは次のとおりです。

1. 記事を Claude に読ませ、リポジトリに落とし込める構成要素を洗い出させた
2. そのリストを見て、どれを Phase 1 に含めるかを人が判断した
3. 題材は記事自身の例（保険金請求ステータスのセルフサービス化）を採用した
4. Claude がファイル一式を生成し、テストと lint が通ることを確認した

したがって、成果物そのものは Claude（Claude Opus 5）による生成物です。スコープの決定、生成結果の確認は人が行っています。

記事の実践という趣旨上、生成過程自体も記事のやり方をなぞる形になりました。つまり intent.md から spec.md、plan.md、テスト、実装へと順に成果物を確定させていく進め方です。