---
name: gitignore
description: >-
  `.gitignore` の新規作成、既存 `.gitignore` の見直し、`gitignore.io` からのテンプレート取得、リポジトリからの template 自動推定、OS・言語・IDE ごとの ignore 項目整理を扱う。`gitignore.io` を使って必要なものを集めたいときや、`mise` のように template がない tool の手書き ignore を足したいときに使う。project ルートの `.gitignore` 作成・見直しに限定し、`.gitattributes` や git hook 設定は対象外。
compatibility: Requires network access for gitignore.io
---

# Gitignore

## 目的

生成由来と手書きの境界を壊さない。追跡すべきソースや機密の ignore 漏れはコスト大。粒度より境界の明確さを優先。

## 使う場面

- `.gitignore` 新規作成時
- 既存 `.gitignore` の不足・過剰項目の見直し時
- `gitignore.io` から OS・言語・IDE テンプレート取得時
- リポジトリの手掛かりから ignore 候補を自動推定したいとき
- `gitignore.io` にない tool 用の custom ignore 追加時
- ローカル成果物の ignore 範囲整理時

## 手順

1. 対象リポジトリ・保存先・技術スタック・作業環境を確認。曖昧なら `@path` や用途を確認。
2. `review` / `draft` / `write-file` を判定。未指定なら既存 `.gitignore` あり→`review`、なし→`draft`。
3. 既存 `.gitignore` と判断に必要な最小限の手掛かりだけ読む。必要なら `scripts/fetch-gitignore.sh detect <target-path>` で候補を先出し。詳細は [references/auto-detection.md](references/auto-detection.md) を参照。
4. ユーザー指定・リポジトリの手掛かり・自動推定結果をもとに `gitignore.io` テンプレート候補を決定。取得には [references/helper-script.md](references/helper-script.md) の `detect|auto|list` を使用。template 選定は [references/template-selection.md](references/template-selection.md)、custom ルールは [references/custom-rules.md](references/custom-rules.md) を参照。
5. 出力生成: `review`→不足・過剰・推奨テンプレート一覧と必要なら custom ルールを返す。`draft`→テンプレート取得結果に custom block を追加して file-ready な `.gitignore` 案を返す。既存 file 更新は [references/existing-gitignore.md](references/existing-gitignore.md)、出力形式は [references/output-modes.md](references/output-modes.md) を参照。
6. 自動レビュー（`review` および `draft` 時）: `references/rules/` をファイル名順で適用し、[assets/review-output-template.md](assets/review-output-template.md) 形式で結果を添付。重大指摘あり→本文案を修正して同一ターン内で再レビュー（最大 2 回）。重大なし→「レビュー合格。ユーザー承認を求めます」。
7. `write-file`→保存先が明示された場合のみ実行。保存前に rules レビュー合格を確認。既存手書きルールを保持して更新。generated block と custom block の由来が混ざらない書き方を優先。
8. 取得失敗・template 不明時は使えそうな template 名・fallback 方針・追加確認事項だけ返す。

詳細判断は [references/gitignore-knowledge.md](references/gitignore-knowledge.md) を参照。

## 期待する出力

- リポジトリから自動推定した template 候補と妥当性確認
- `gitignore.io` テンプレート名と選定理由
- `gitignore.io` にない tool の custom ignore ルール
- 既存 `.gitignore` を壊しにくい更新方針または file-ready な本文案
- `references/rules/` に基づくレビュー結果（重大 / 提案 / 任意）
- 取得失敗時の fallback と追加確認事項

## 検証

- `SKILL.md` は workflow に留まり、詳細知識を `references/` へ逃がしている
- hub から各 reference へリンクが通る
- `references/rules/` を辞書順で適用できる
- 新規下書き・レビュー返答は `assets/review-output-template.md` を起点にできる
- `description` は WHAT と WHEN を含み、trigger 語（`.gitignore`、`gitignore.io`、`mise`）が見える
