---
name: migrations-script
description: >-
  運用中システムで一度きり実行する migration script、data fix、backfill、infra resource 更新、one-off script の計画・作成・レビューを支援する。dry-run、再実行しても壊れない性質（冪等性）、変更前/変更後の記録（before/after log）、rollback、監査ログ、実行後検証が必要なときに使う。
---

# Migrations Script

## 目的

一度きりのデータ更新やインフラリソース更新を、復旧と監査が残る migration script / 実行手順書として整理する。

## 使う場面

- 本番または本番相当環境で data fix、backfill、一度きりの migration script を作るとき
- DB record、外部 API resource、cloud resource、設定値などを限定的に更新するとき
- 事前確認、変更前後の記録、rollback、実行ログ、実行後検証を含む実行手順書が必要なとき
- 既存 migration script の安全性、ログ粒度、復旧のしやすさをレビューするとき

## 手順

1. 対象、環境、変更目的、実行タイミング、影響範囲、保存したい証跡を特定する。
2. 依頼種別を `review` / `draft` / `write-file` に分類する。保存先が明示された場合だけ `write-file` として扱う。
3. 情報不足なら、対象範囲、事前確認の可否、rollback 方針、ログ保存先、機密情報の扱いに絞って確認する。
4. [references/migrations-script-knowledge.md](references/migrations-script-knowledge.md) の必須ゲートで、事前確認、冪等、対象範囲、分割実行、多重実行の防止、backup、rollback、監視、承認、機密情報、検証を確認する。列挙したクラッシュ地点（更新前 / 試行記録の直後 / 変更後の書き込み前 / バッチ境界）から再実行し、同じ終状態に収束するかを見る。1 バッチごとに変更前後を残す。
5. `draft` / `write-file` では [assets/migration-runbook-template.md](assets/migration-runbook-template.md) を起点に、script 本体だけでなく実行手順書、ログ設計、検証手順を組み立てる。
6. ログは標準出力を補助扱いにし、実行者、時刻、script version、対象、旧状態、新状態、件数、失敗、停止理由、検証結果をファイルへ残す方針にする。
7. 本番実行は自動で行わない。実行コマンド、停止条件、rollback / 補正して進める手順、承認者、実行後確認を明示してユーザー承認を待つ。

詳細判断とレビュー観点は knowledge を参照する。

## 期待する出力

- migration script / 実行手順書の下書き、または既存 script のレビュー結果
- 事前確認、変更前後の記録、rollback、実行後検証を含む安全性チェック
- ログファイルに残すべき項目と、機密情報を残さないための mask / hash / omit 方針
- 実行前の確認質問、停止条件、承認ゲート、実行後の検証手順
- クラッシュ地点からの再実行で収束するかの確認

## 検証

- `SKILL.md` 自体は使い方に留まり、詳細知識を抱え込んでいない
- 詳細な判断は `references/` を読めば追える
- 実行手順書の下書きでは `assets/` のテンプレートを起点にできる
- YAML frontmatter の `description` は `>-` を使い、plain scalar にしていない
- `description` は WHAT と WHEN を含み、trigger 語と境界が見える
- migration script の本番実行を、ユーザー承認なしに進めない境界が明確である
- クラッシュ地点からの再実行と、バッチごとの変更前後が必須ゲートにある
