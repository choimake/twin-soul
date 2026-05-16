# Mutation Testing

この資料は `testcode` skill の mutation testing 観点をまとめたものである。coverage だけでは見えないテストの弱さを判断したいときに使う。

## mutation testing とは

mutation testing は、コードに人工的な小さな変更を入れて、既存テストがその変化を検出できるかを見る方法である。

例:

- `>` を `>=` に変える
- `true` を `false` に変える
- 条件分岐の片側を常に通るようにする

## killed mutant と surviving mutant

- `killed mutant`:
  - 変更を入れたあとでテストが落ちた状態
  - その変化をテストが検出できたことを示す
- `surviving mutant`:
  - 変更を入れてもテストが通ってしまった状態
  - その変化を現行テストが見逃していることを示す

## `surviving mutant` から分かること

- 境界値ケースが抜けている
- 条件分岐の片側しか見ていない
- assertion が広すぎる
- 例外や失敗系を検証していない

`surviving mutant` は「このあたりのテストが弱い」というヒントとして使う。

## いつ勧めるか

mutation testing は強力だがコストがあるため、まず次のような場面に絞る。

- coverage は十分だが不安が残る
- バグ再発防止のために assertion の強さを見たい
- 重要なドメインロジックで、条件分岐や比較演算が多い
- 変更の影響が大きく、テストの見逃しコストが高い

## 改善提案への落とし方

mutation testing の結果を使うときは、抽象論で終わらせず次の形にする。

- どの条件が生き残ったか
- どの入力や境界値が不足しているか
- 既存 assertion をどう狭くするか
- 追加すべきテストをテスト名やケース名レベルで提案する
