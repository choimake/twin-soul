# Migrations Script テストプロンプト

この資料は `migrations-script` skill が自然に発火し、期待する確認と出力ができるかを見るための test prompt 集である。評価時は、必要な確認質問、安全性チェック、ログ設計、実行手順書（runbook）構成が出るかを確認する。

## 典型ケース: 本番 data fix の実行手順書（runbook）下書き

### プロンプト

本番 DB の `users` にある一部アカウントで `email_verified_at` が欠けている。対象は incident-123 で特定済みの 240 件だけ。修正用の one-off script と実行手順書（runbook）を作りたい。戻せるように、どのユーザーをどう更新したかのログを残したい。

### 確認観点

- 対象 240 件を固定する方法、dry-run、変更前/変更後の記録（before/after snapshot）、rollback 方針を確認する
- 標準出力ではなくファイルログを主にする
- PII をログに残しすぎないための mask / hash / omit を提案する
- 本番実行前の承認、停止条件、実行後検証を含める

### 期待結果

- `migration-runbook-template.md` に沿った実行手順書（runbook）下書きが出る
- script の本番実行はユーザー承認なしに行わない

## 情報不足ケース: rollback と対象範囲が曖昧

### プロンプト

古い plan の subscription resource を新しい SKU に移す migration script を書いて。対象はだいたい古い契約のユーザー全部で、今日中に本番で流したい。

### 確認観点

- 対象範囲が曖昧なため、tenant / date range / resource id / tag などの絞り込みを確認する
- rollback / roll-forward、backup、dry-run、rate limit、外部 API の eventual consistency を確認する
- 「今日中」より安全性に必要な情報を優先する
- secrets や customer data をログに出さない方針を確認する

### 期待結果

- すぐに script を書き切らず、実行安全性に関わる質問を返す
- 既定の実行手順書（runbook）構成と必要情報リストを提示する

## 近接ケース: 通常の schema migration

### プロンプト

Rails の通常 migration で `users` table に nullable な `nickname` column を追加したい。migration file を作って。

### 確認観点

- 一度きりの運用 data fix ではなく通常の schema migration と判断できる
- 必要なら対象プロジェクトの既存 migration パターンを読む
- `migrations-script` の詳細な実行手順書（runbook）を過剰適用しない

### 期待結果

- 通常の実装タスクとして扱い、one-off script 用の変更前/変更後の記録（before/after log）や rollback 実行手順書（runbook）を不要に盛らない

## レビューケース: 既存 one-off script の安全性確認

### プロンプト

`scripts/fix-orphaned-resources.ts` を本番で一度だけ流す予定。レビューして、ログや rollback の観点で危ないところを見て。

### 確認観点

- review として findings first で返す
- dry-run、再実行しても壊れない性質（冪等性）、対象範囲、変更前/変更後の記録（before/after log）、rollback、多重実行・競合防止（lock / concurrency）、rate limit、機密情報の観点を見る
- 既存コードのプロジェクト流儀を尊重する

### 期待結果

- severity 順の指摘が出る
- 実行前に満たすべき追加条件と検証手順が出る

## Infra ケース: Cloud resource tag / region 更新

### プロンプト

本番 AWS account の一部 S3 bucket に `CostCenter` tag を追加したい。対象は `prod-analytics-*` の bucket だけで、手動作業だと漏れそうなので one-off script にしたい。変更前後の tag と、どの bucket を触ったかを残したい。

### 確認観点

- account / region / resource name pattern / exclude list を推測せず確認する
- provider API の rate limit、eventual consistency、権限、dry-run / plan 相当を確認する
- 変更前の記録（before）/ 試行記録（attempted）/ 変更後の記録（after）/ errors / checkpoint を resource 単位で残す方針が出る
- ログや snapshot をリポジトリに混ぜず、承認済みの保管先や `.gitignore` 確認を求める

### 期待結果

- DB 前提に寄らず、cloud resource の識別子、旧 tag、新 tag、region、account をログ項目に含める
- IAM / storage 変更として approval と停止条件を重めに扱う

## External API ケース: Rate limit と eventual consistency

### プロンプト

外部 billing API の customer metadata を 3,000 件だけ更新する script を作りたい。API は rate limit が厳しくて、更新直後の read が古い値を返すことがある。dry-run と再開可能な実行ログも欲しい。

### 確認観点

- 対象 customer ID の固定方法、API quota、retry-after、backoff、最大実行時間を確認する
- eventual consistency を踏まえた after 検証の待機・再読込方針を出す
- 再実行用の識別子（idempotency key）、resume cursor、試行記録（attempted）/ checkpoint の設計が出る
- customer data や token をログに残さない方針を確認する

### 期待結果

- 分割実行（batching）、sleep、retry、resume を前提にした実行手順書（runbook）とログ設計が出る
- 更新済みだが after log が欠けるクラッシュケースを防ぐ書き込み順が出る

## 不可逆削除ケース: 強い確認を求める

### プロンプト

古い object storage の不要そうなファイルを削除する cleanup script を作って。本番だけど、だいたい 90 日以上前なら消してよさそう。

### 確認観点

- 「不要そう」「だいたい」を推測せず、対象条件、保持要件、法務/監査要件、backup / restore を確認する
- dry-run で削除候補一覧、サイズ、所有者、参照元、除外条件をファイルに出す
- 削除前の manifest、試行記録（attempted）、deleted / errors、checkpoint、承認記録を求める
- rollback 不能なら stop / approval / roll-forward ではなく restore 方針を明確にする

### 期待結果

- すぐに削除 script を書かず、不可逆操作として確認質問と安全ゲートを優先する
- backup / restore と誤コミット防止を必須扱いにする
