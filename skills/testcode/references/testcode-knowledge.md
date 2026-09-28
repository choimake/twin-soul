# Testcode 判断知識

この資料は `testcode` skill の入口となる判断知識をまとめたものである。`SKILL.md` は使い方に留め、詳細判断はこの資料と分割した `references/` の各ドキュメントを起点にする。

skill 自体を試す test prompt（将来の評価テンプレートや rubric の起点）:

- [../assets/test-prompt-template.md](../assets/test-prompt-template.md)

## この skill の役割

- テストコード生成を、対象理解なしの一発生成として扱わず、ケース整理を挟んだ workflow として扱う
- 生成したテストを、`通るかどうか` だけでなく `何を保証しているか` で評価する
- coverage だけを追うのを避け、必要に応じて mutation testing や test smell の観点へ広げる

## 呼び出し側が渡せる入力

- 対象コードや既存テストの `@path`
- `generate` / `evaluate` / `improve` のモード指定
- 言語、テストフレームワーク、既存のテスト規約
- 保存先や更新対象ファイル
- `coverage` `mutation` `smell` のような見たい論点

未指定なら、この skill が会話から妥当な既定値を判断する。必要最低限の確認だけを追加する。

## 対象と探索の絞り方

1. `@path` があれば、そのコードと近接する既存テストを優先して読む。
2. モード指定があれば優先する。未指定なら、作成依頼は `generate`、レビュー依頼は `evaluate`、改善依頼は `improve` を既定にする。
3. 対象コードが広すぎる場合は、まず公開 API、主要分岐、例外処理、既存テストの有無に絞る。
4. 既存テストがある場合は、何を既に保証していて、何が未検証かを先に見る。
5. リポジトリ全体のテスト方針を読む前に、対象関数やクラス単位でケース整理できるかを確認する。

## 参照する文書

- [test-generation.md](test-generation.md)
  - `generate` の進め方、ケース整理、足さない 3 種
- [tests-express-what.md](tests-express-what.md)
  - テストが示す層は振る舞い。実装手順の鏡を避ける
- [test-evaluation.md](test-evaluation.md)
  - `evaluate` と `improve` の基本、品質の見方、coverage の扱い
- [mutation-testing.md](mutation-testing.md)
  - mutation testing、`killed mutant`、`surviving mutant`
- [test-smells.md](test-smells.md)
  - `Assertion Roulette` などの smell と改善の見方
- [message-assertions.md](message-assertions.md)
  - エラー・ログ・例外メッセージを完全一致で検証する方針
- [sources.md](sources.md)
  - 出典と深掘り用 URL

## 応答時の明示事項

- 対象コードが不明なときは `@path`、言語、テストフレームワークのどれかを確認する
- coverage だけで品質保証したことにしないと明示してよい
- mutation testing 未導入でも、今すぐ必要か後回しでよいかを切り分けて返す
