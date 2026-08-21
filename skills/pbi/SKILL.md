---
name: pbi
description: >-
  プロダクトバックログアイテム（PBI）用 Markdown の起案・レビューする。受入基準・確認方法・スコープを軽量に整理する。バックログ、ユーザーストーリー、受入基準、受け入れ条件、INVEST の整理時に使う。実装手順、変更ファイル一覧、CI やコマンド検証を主体とする計画書は本 skill の対象外。
---

# PBI

## 目的

PBI ドキュメントの構造と受入品質を保ち、手戻りを防ぐ最小限の記述（背景・目的、受入基準、確認方法、メモ・論点）を揃える。

## 使う場面

- 新規 PBI の下書き、または既存 PBI のレビュー
- 受入基準・確認方法・論点を揃えたいとき
- ユーザーストーリー、受け入れ条件、INVEST の観点整理が必要なとき

## 手順

1. 対象を特定する。既存 PBI の `@path` があれば優先、無ければ新規作成として扱う。曖昧なら、新規 / 既存レビュー / 保存先のどれかを短く確認し、決まるまで本文生成には入らない。
2. 出力モードを判定する。`review` / `draft` / `write-file` が明示されていれば優先。未指定なら、既存 PBI パスあり→`review`、無し→`draft`。
3. [assets/pbi-template.md](assets/pbi-template.md) を起点に、既定では軽量な必須セクションだけを埋める。抽象レイアウトとの対応、Web 検索ロジック、保存先未指定時の扱いは [references/pbi-knowledge.md](references/pbi-knowledge.md) を参照する。
4. `references/rules/` 配下のルールをファイル名順で適用し、重大 / 提案 / 任意 で指摘する。
5. [assets/review-output-template.md](assets/review-output-template.md) の形式でレビュー結果を返す。重大あり→修正を促す、無し→ユーザー承認を求める。
6. `write-file` では保存先が明示されていればそのパスへ保存する。未指定なら、本文生成前にユーザーへ保存先を確認する（既定ディレクトリは設けず、特定ツール依存のパスも推定しない）。

詳細判断は [references/pbi-knowledge.md](references/pbi-knowledge.md) を参照する。

## 期待する出力

- PBI 下書き、またはレビュー結果（重大 / 提案 / 任意）
- `draft` / `write-file` 時は Web 検索で得た補足参照の統合
- `write-file` 時は保存先パスの明示

## 検証

- `SKILL.md` は workflow に留まり、詳細知識を `references/pbi-knowledge.md` に移している
- 判断基準とルール本文は `references/` を読めば追える
- 新規下書きは `assets/pbi-template.md`、レビュー返答は `assets/review-output-template.md` を起点にできる
- `description` は WHAT と WHEN を含み、trigger 語（PBI・バックログ・受入基準・ユーザーストーリー）と対象外（実装手順・コマンド検証主体の計画書）が見える
- 対象未指定時は新規 / 既存レビュー / 保存先のどれかを短く確認してから本文生成に入る
