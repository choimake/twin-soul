# [Migration Script / Data Fix Name]

## 概要

- 目的:
- 担当者:
- レビュー担当 / 承認者:
- 実行者:
- 環境:
- 実行予定時間:
- 関連 issue / incident / request:
- script の場所（Script path）:
- script version / commit SHA:

## 対象範囲

- 対象システム:
- 対象データ / リソース:
- 対象を絞る条件:
- 想定対象件数:
- 対象外:
- 依存関係:

## リスク分類

- リスクレベル:
- ユーザー影響:
- データ消失リスク:
- 元に戻せるか:
- メンテナンス時間帯が必要か:
- 承認が必要か:

## 事前条件

- [ ] 対象環境が確定している
- [ ] script version / commit SHA が固定されている
- [ ] 必要な backup または restore point が用意されている
- [ ] 認証情報は承認済みの secret storage から取得する
- [ ] ログと記録に secrets や不要な PII が出ない
- [ ] 監視 dashboard / alert が用意されている
- [ ] 停止条件に合意している
- [ ] rollback / roll-forward の担当者が対応可能である

## 事前確認実行（dry-run）

### コマンド

```bash
# 例。実際のプロジェクトに合わせたコマンドへ置き換える。
command --dry-run --scope "[scope]" --log-dir "[log-dir]"
```

### 期待する出力

- 対象件数:
- 変更予定:
- skip 件数と理由:
- エラー候補:
- 変更前の記録ファイル:
- 変更予定後の記録ファイル:
- summary file（概要ファイル）:

### 事前確認結果

- 実行日時:
- 実行者:
- コマンド:
- ログディレクトリ:
- 概要:
- 判断: proceed / revise / stop

## ログ設計

標準出力は補足扱いにする。主たる監査証跡はファイルに書き出す。

### ログディレクトリ

- Path（保存先パス）:
- 保存先: approved external storage / encrypted bucket / audit log system / temporary local path
- リポジトリ配下に置く場合、`.gitignore` 確認済み: yes / no / not applicable
- 保存期間:
- アクセス制御:
- 暗号化要否:
- 閲覧可能な人:
- 削除期限:

### 必要ファイル

- `run-summary.json` or `run-summary.md`: 実行 ID（run id）、mode、environment、executor、script version、件数、結果
- `before.jsonl` or `before.csv`: 検証 / rollback に必要な対象識別子と変更前の状態
- `planned-after.jsonl` or `planned-after.csv`: dry-run で確認した変更予定後の状態
- `attempted.jsonl`: 更新を試みた対象識別子、試行時刻、分割単位 ID（batch id）、resume cursor
- `after.jsonl` or `after.csv`: 実行後の実際の状態
- `errors.jsonl`: 失敗した対象、エラーメッセージ、retry 可否、次アクション
- `checkpoint.json`: 最後に永続化できた分割単位（batch）、件数、resume cursor、未完了項目
- `verification.md`: 実行後検証の結果

### 書き込みタイミングと永続化

- mutation 前に、対象識別子と変更前の状態を `before` へ書き込み flush する。
- mutation 呼び出しの直前に、`attempted` へ書き込み flush する。
- mutation 結果が返った直後に、`after` または `errors` へ書き込み flush する。
- 分割単位（batch）の終わりごとに、件数と次の resume cursor を `checkpoint` に書き込む。
- 実行後に `attempted` と `after` / `errors` を照合し、終了状態のログがない対象を調査する。
- 一時的にローカルファイルを使った場合は、run を閉じる前に承認済みの保管先へアップロードする。

### 秘匿情報の扱い

- Secrets（秘匿情報）:
- PII:
- mask する値:
- hash する値:
- omit する値:
- 生値が必要な場合の例外承認:

## 再実行しても壊れない性質（冪等性）と再開

- 再実行しても壊れないようにする方針（idempotency strategy）:
- 二重実行された場合の挙動:
- 処理済み marker / 再実行用の識別子（idempotency key）:
- 再開位置（resume cursor）:
- 部分失敗時の扱い:
- 再試行方針（retry policy）:

## 多重実行・競合防止（lock / concurrency）と API 制限

- 多重実行・競合防止の方針（lock strategy）:
- 競合しうる書き込み処理 / jobs:
- 分割単位のサイズ（batch size）:
- 分割実行の間隔（sleep between batches）:
- 最大実行時間:
- API / provider の rate limit:
- replication lag や整合性に関する考慮:

## 実行計画

### コマンド

```bash
# 例。明示的な承認なしに本番実行しない。
command --execute --scope "[scope]" --log-dir "[log-dir]"
```

### 手順

1. 開始を周知し、承認済みであることを確認する。
2. 環境、commit SHA、対象範囲、ログディレクトリを確認する。
3. 最新の dry-run 結果が想定対象範囲と一致していることを確認する。
4. 監視を開始する。
5. 実行コマンドを実行する。
6. 実行中は停止条件に該当しないか確認する。
7. ログと記録ファイルを保全する。
8. 実行後検証を行う。
9. 完了または停止理由を周知する。

## 停止条件

- 想定外の対象件数:
- エラー件数の閾値:
- latency / error rate の閾値:
- DB load / replication lag の閾値:
- API rate limit / provider error の閾値:
- ログ / 記録ファイルの欠落:
- 手動中止時の連絡先:

## 復旧方針（Rollback / Roll-forward）

### 方針

- 採用する方針: rollback / roll-forward / restore from backup / manual remediation
- 判断理由:
- rollback 可能な期限:
- 変更前/変更後の記録（before/after logs）から必要な入力:
- 担当者:

### Rollback コマンドまたは手順

```bash
# 例。手動 rollback の場合は置き換えるか削除する。
command --rollback --input "[before-log]" --log-dir "[rollback-log-dir]"
```

### Roll-forward 手順

- 補正内容:
- 検証:
- 連絡:

## 実行後検証

- [ ] 対象件数が想定と一致している
- [ ] 更新件数、skip 件数、失敗件数を説明できる
- [ ] 代表的な record / resource が期待する変更後状態になっている
- [ ] アプリケーション動作が正常である
- [ ] 監視 metrics が正常に戻っている
- [ ] error logs と alerts を確認済み
- [ ] 残った失敗に担当者と次アクションがある
- [ ] ログ、記録ファイル、承認、検証メモが保存されている

## 最終報告

- Run id（実行 ID）:
- 結果: success / partial / failed / rolled back / rolled forward
- 開始日時:
- 終了日時:
- 実行者:
- 承認者:
- ログディレクトリ:
- 概要:
- フォローアップ:
