# Test Smell

この資料は `testcode` skill の test smell 観点をまとめたものである。テストが壊れているとは限らないが、読みづらい、誤解しやすい、保守しにくい書き方のサインを整理する。

## test smell とは

test smell は、将来の不具合や誤判定の温床になりやすい書き方である。見つけたら「即バグ」とは限らないが、なぜ危ないかと、どう簡素化・分割できるかまで返す。

## よく見る smell

- `Assertion Roulette`
  - assertion が多いのに、どれが何を確認しているか分かりにくい
- `Conditional Test Logic`
  - テストの中に `if` や loop があり、読み手が実行経路を追いづらい
- `Eager Test`
  - 1 つのテストで複数メソッドや複数責務をまとめて触っている
- `Mystery Guest`
  - 外部ファイル、DB、hidden fixture など前提がコードから見えにくい
- `Magic Number Test`
  - 意味の説明なしに数値リテラルが並ぶ
- `Sleepy Test`
  - `sleep` に依存して flaky になりやすい
- `Unknown Test`
  - assertion がなく、落ちなければ成功になっている
- 弱いメッセージ照合
  - エラー・ログ・例外メッセージを `in`、`contains`、緩い正規表現だけで確認している

## 見つけたときの返し方

- smell 名だけで終わらせない
- 何が読みづらいか、何を見逃しやすいかを説明する
- テスト分割、fixture の縮小、assertion の明確化など、改善の方向を添える
- メッセージ照合が弱い場合は、プレフィックス、区切り、フィールド構造の回帰を見逃すことを説明し、全文一致へ変更する。詳細は [message-assertions.md](message-assertions.md) を参照する

## 並列チェック向きの使い方

`test-evaluation.md` と分けて扱うことで、次のような観点を並列に見やすくする。

- assertion の質
- メッセージ出力の完全一致
- edge case の漏れ
- 外部依存の有無
- smell の有無

全部を 1 つの pass/fail に畳まず、観点ごとに弱さを切り分ける。
