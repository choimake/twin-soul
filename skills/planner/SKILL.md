---
name: planner
description: >-
  plan file の品質を保証する。必須項目（受け入れ条件、ベストプラクティス参照、検証手順）の強制、AI 自動レビュー、Web 検索統合を含む。plan mode 開始時、既存 plan のレビュー時、plan テンプレートから下書きを作りたいとき、方針相談・方法論整理時、plan file の完成度を高めたいときに使う。
---

# Planner

## 目的

品質ゲート: 受け入れ条件・検証手順の欠落は重大として扱う。網羅性より「手戻りを防ぐ最小限の品質」を優先する。

## 使う場面

- plan mode 開始時
- 既存 plan file レビュー時
- plan テンプレートからの下書き作成
- 方針相談・方法論整理（実装 plan はスコープ外）
- 必須項目（受け入れ条件・ベストプラクティス参照・検証手順）の確認
- ベストプラクティス検索・plan への統合

## 手順

1. 対象 plan を特定。既存 plan file の `@path` があれば優先、なければ新規作成として扱う。
2. 依頼が相談・方法論系か実装 plan 系かを判定。相談系は [references/planner-knowledge.md](references/planner-knowledge.md) の方法論フローに従い、実装 plan・変更ファイル一覧はスコープ外と明示する。
3. `review` / `draft` / `write-file` を判定。未指定なら既存 plan file あり→`review`、なし→`draft`。
4. `draft` / `write-file` の場合、タスク内容から Web 検索キーワードを抽出しベストプラクティスを検索。
5. 実装 plan 系のみ [assets/plan-template.md](assets/plan-template.md) を起点に必須セクション（背景, 目的, 受け入れ条件, ベストプラクティス, 実装方針, 変更対象ファイル, 検証, リスクと対策）を埋める。
6. `references/rules/` 配下のルールをファイル名順で適用し品質チェック。
7. [assets/review-output-template.md](assets/review-output-template.md) の形式でレビュー結果を返す。重大指摘あり→修正促す、なし→ユーザー承認を求める。
8. `write-file` では保存先が明示されていればそのパスへ保存する。未指定なら、本文生成前にユーザーへ保存先を確認する。

詳細判断は [references/planner-knowledge.md](references/planner-knowledge.md) を参照。

## 期待する出力

- plan file 下書きまたはレビュー結果
- AI 自動レビューによる品質チェック結果（重大 / 提案 / 任意）
- Web 検索で取得したベストプラクティスの統合
- 保存先の明示（write-file モード時）
