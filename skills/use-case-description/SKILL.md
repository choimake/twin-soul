---
name: use-case-description
description: >-
  ユーザーストーリー等の上流入力から、アクター・事前/事後条件・基本/代替/例外フロー・用語集を備えたユースケース記述（Markdown）を起案・レビューする。「ユースケースを書いて」「ユーザーストーリーを usecase.md に詳細化して」「基本フロー・代替フロー・例外フローを整理して」のような依頼で使う。ユースケース図の作図、要求定義文書全体の構成整理（requirements-definition）、PBI・受入基準の起案（pbi）は本 skill の対象外。
---

# Use Case Description

## 目的

ユースケース記述の構造品質を保ち、手戻りを防ぐ最小限の記述（アクター、事前・事後条件、番号付きフロー、暗黙の前提の明示、用語集）を揃える。

## 使う場面

- ユーザーストーリーや利用シナリオをユースケース記述へ詳細化するとき
- 既存ユースケース記述のレビュー
- 基本・代替・例外フローの構造、番号付け、事前・事後条件を整理したいとき

## 手順

1. 対象を特定する。既存ユースケース記述の `@path` があれば優先、無ければ新規作成として扱う。入力となるユーザーストーリー（または利用シナリオ）を確認し、曖昧なら新規 / 既存レビュー / 入力ストーリーのどれかを短く確認してから本文生成に入る。
2. 出力モードを判定する。`review` / `draft` / `write-file` が明示されていれば優先。未指定なら、既存パスあり→`review`、無し→`draft`。
3. 入力から主アクター・ゴール・対応ストーリーを特定する。ストーリーに書かれていない成立前提は当て推量で埋めず、「暗黙の前提」として A 番号で明示するか、ユーザーに確認する。
4. [assets/use-case-template.md](assets/use-case-template.md) を起点に本文を組み立てる。書式の選択（fully dressed / 簡略版）や任意項目の追加判断は [references/use-case-description-knowledge.md](references/use-case-description-knowledge.md) を参照する。
5. `references/rules/` 配下のルールをファイル名順で適用し、重大 / 提案 / 任意 で指摘する。
6. [assets/review-output-template.md](assets/review-output-template.md) の形式でレビュー結果を返す。重大 あり→修正を促す、無し→ユーザー承認を求める。
7. `write-file` では保存先が明示されていればそのパスへ保存する。未指定なら、本文生成前にユーザーへ保存先を確認する（既定ディレクトリは設けず、特定ツール依存のパスも推定しない）。

詳細判断は [references/use-case-description-knowledge.md](references/use-case-description-knowledge.md) を参照する。

## 期待する出力

- ユースケース記述の下書き、またはレビュー結果（重大 / 提案 / 任意）
- 対応ストーリーへの紐づけと、採用した暗黙の前提（A 番号）の一覧
- `write-file` 時は保存先パスの明示

## 検証

- `SKILL.md` は workflow に留まり、詳細知識を `references/use-case-description-knowledge.md` に逃がしている
- 判断基準とルール本文は `references/` を読めば追える
- 新規下書きは `assets/use-case-template.md`、レビュー返答は `assets/review-output-template.md` を起点にできる
- `description` は WHAT と WHEN を含み、trigger 語（ユースケース・基本フロー・代替フロー・例外フロー・アクター）と対象外（ユースケース図・要求定義全体・PBI）が見える
- 対象未指定時は新規 / 既存レビュー / 入力ストーリーのどれかを短く確認してから本文生成に入る
