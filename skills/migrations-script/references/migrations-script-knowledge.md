# Migrations Script 判断知識

この資料は `migrations-script` skill の判断知識をまとめたものである。`SKILL.md` は使い方に留め、migration script の安全性判断、レビュー観点、ログ設計、rollback 方針はこの資料とテンプレートを起点にする。

テンプレート:

- [../assets/migration-runbook-template.md](../assets/migration-runbook-template.md)
- [../assets/test-prompt-template.md](../assets/test-prompt-template.md)

## この skill の役割

- 運用中システムで一度きり実行する data / infra migration script の計画、作成、レビューを支援する
- script 本体だけでなく、事前確認、実行ログ、変更前後の記録、rollback、実行後検証を成果物に含める
- 本番実行そのものは扱わない。実行はユーザー承認と対象プロジェクトの運用手順に従う

## 呼び出し側が渡せる入力

- 対象システム、環境、tenant / project / account / region などのスコープ
- 更新対象の DB table、record、外部 API resource、cloud resource、設定値
- 期待する出力モード: `review` / `draft` / `write-file`
- 既存 script や実行手順書の `@path`
- ログ保存先、backup 方法、rollback / 補正して進める方針
- `--dry-run` の結果、対象件数、代表サンプル、監視指標

未指定の場合でも、低リスクな出力形式、章立て、ログファイル名の例だけ既定値を使ってよい。対象範囲、環境、事前確認の可否、rollback 方針、backup、ログ保存先、secrets、PII の扱いなど実行安全性に関わる値は推測で埋めず、必ず確認する。

## 対象と探索の絞り方

1. `@path` がある場合は、その script、実行手順書、migration 関連ファイルを優先して読む。
2. 対象が DB か infra か外部 API かを分類し、それぞれの識別子と旧状態・新状態の取り方を確認する。
3. 影響範囲が広い場合は、全件ではなく tenant、project、date range、primary key range、tag、region などで絞る提案をする。
4. 情報不足が実行安全性に関わる場合は、推測で埋めず確認する。特に対象範囲、環境、事前確認の可否、rollback、backup、本番実行、secrets、PII、ログ保存先は確認対象にする。
5. 既存プロジェクトの migration / script パターンがある場合は、その流儀を優先し、ない場合だけ汎用テンプレートを使う。

## 必須ゲート

### 1. 目的と停止条件

- 何を、なぜ、いつ、誰が、どの環境で更新するかを書く
- 成功条件と停止条件を事前に決める
- 影響範囲、想定実行時間、連絡先、承認者を明記する

### 2. 事前確認

- 本更新前に、変更せず対象件数と差分を出すモードを用意する（コマンドは `--dry-run` など）
- 事前確認は対象 ID、旧値、予定新値、件数、skip 理由、エラー候補をファイルへ出す
- infra では plan / diff、DB では SELECT / transaction rollback、外部 API では読み取り専用の呼び出しや sandbox を使う
- 事前確認できない場合は、その理由、代替検証、リスク受容者を明記する

### 3. 冪等

- 同じ script を再実行しても二重更新、二重作成、重複削除にならないようにする
- 既存状態の確認、自然キー、再実行用の識別子、処理済みマーカー、upsert、比較してから書く、を検討する
- 中断後に再開できるよう、再開位置や処理済み ID の記録を用意する
- 冪等にできない処理は transaction、backup、明示的な再実行禁止、手動復旧手順で補う

### 4. クラッシュ地点からの再実行

クラッシュは起きる前提にする。列挙した地点から再実行し、同じ終状態に収束するかを見る。収束しなければ冪等ではない。

既定の 4 点:

1. 更新前（`before` を書き切った直後、更新はまだ）
2. 試行記録の直後（`attempted` を書いた直後、更新の成否は未確定）
3. 変更後の書き込み前（更新は終わったが `after` がまだ）
4. バッチ境界（そのバッチの変更前後と再開位置を書いた直後）

各点で「前回がここで落ちた」状態を置き、同じ script を再実行する。終わる状態（件数、対象の値、ログの突合）が同じなら合格。地点ごとに結果が変わるなら、再開位置か冪等の設計を直す。

無限に地点を増やさない。上記 4 点が既定。対象システムの都合で足すなら、実行手順書に理由を書く。

### 5. 変更前後の記録とログ

標準出力は補足扱いにする。監査、復旧、レビューに使う情報はファイルへ残す。

最低限のログ項目:

- 実行 ID、script name、script version、commit SHA、実行者、実行環境、開始/終了時刻
- 事前確認 / 実行の mode、対象スコープ、入力条件、対象件数
- 対象の識別子、旧状態、予定新状態、実行後状態、skip 理由、error
- 成功件数、失敗件数、未処理件数、再試行件数、停止理由
- backup の場所、rollback / 補正して進めるのに必要な情報、実行後検証結果

書き込み順:

- 更新前に、対象ごとの識別子と旧状態を `before` に保存して書き切る
- 更新を呼び出す直前に `attempted` を書き、途中クラッシュ時も「どこまで試したか」を追えるようにする。空振り（試した記録があるが未更新）が出ても、呼び出し後に記録が欠けるより監査上扱いやすい
- 更新後は対象ごとに `after` または `error` をすぐ書き、必要ならディスクへ書き切る
- 1 バッチの終わりごとに、そのバッチの変更前後、件数、次の再開位置を残す。実行全体の要約だけでは足りない
- 実行後は `attempted` と `after` / `error` の差分を照合し、ログにない更新済み対象が残らないよう検証する

ログ形式の既定値:

- 機械処理しやすい JSON Lines または CSV を優先する
- 概要用に summary JSON / Markdown を別ファイルで残してよい
- ファイル名には実行 ID、環境、日時、事前確認 / 実行を含める
- 大量データでは 1 ファイルに詰め込みすぎず、chunk 番号や batch 番号で分ける

ログ保存先:

- 原則として、承認された外部保管先、暗号化 storage、監査ログ基盤などリポジトリ外の保存先を使う
- リポジトリ配下に一時出力する場合は、実行前に `.gitignore` 対象であることを確認する
- 変更前の記録、変更後の記録、backup、rollback 入力は PII や復旧情報を含みやすいため、誤コミット防止を必須ゲートとして扱う
- ログ保存先にはアクセス制御、保管期間、暗号化、削除期限、閲覧者を明記する

### 6. 機密情報と個人情報

- secrets、token、credential、private key は script、引数、ログ、snapshot に残さない
- PII や秘匿値は復旧に必要な最小限だけ扱い、mask、hash、omit のいずれかを選ぶ
- 復旧に平文が必要な場合は、通常ログではなく暗号化された保管先、アクセス制御、保存期間を明記する
- ログの完全性と情報漏えい防止が衝突する場合は、復旧責任者と監査要件を確認する

### 7. backup と rollback / 補正して進める

- backup / restore と rollback script は別物として扱う
- 破壊的変更、削除、不可逆変換では、事前 backup と restore 可能性を確認する
- rollback は「何をいつまで戻せるか」を具体化する
- 補正して進める方が安全な場合は、補正 migration の作成条件と検証条件を書く
- どちらでも、必要な入力が変更前後の記録に残っているか確認する

### 8. 分割実行、rate limit、実行時間

- 大量更新は分割単位のサイズ、sleep、最大実行時間、再開位置を設計する
- DB replication lag、lock wait、API quota、queue backlog、error rate を監視する
- 1 回の実行で完了させる前提にせず、途中停止と再開ができる構造を優先する
- 外部 API や cloud resource では provider の制限、遅れのある反映、retry-after を尊重する

### 9. 多重実行の防止

- 同じ script の多重実行を防ぐ
- scheduler、worker、application write、別 migration との競合を確認する
- DB の advisory lock、分散ロック、メンテナンスフラグ、対象行の楽観ロックなど、多重実行を防ぐ仕組みを検討する
- lock を取る場合は、取得失敗時の終了、timeout、解放失敗時の復旧を明記する

### 10. 監視と承認

- 実行中に見る metrics、log、alert、dashboard を事前に決める
- latency、error rate、DB load、replication lag、queue backlog、API failure、resource saturation を候補にする
- 本番 data fix、IAM / network / DB 変更、削除、不可逆変換は review / 承認を必須にする
- 緊急対応では事後レビューと証跡保存を明記する

### 11. 実行後検証

- 対象件数と更新件数の一致を確認する
- サンプル record / resource の変更前後を確認する
- アプリケーション動作、関連 job、監視指標、エラー率が正常であることを確認する
- 未処理、skip、failure、retry が残る場合は追跡チケットや次アクションを作る
- ログファイル、backup、実行手順書、承認記録の保存先を残す

## 出力モードごとの期待

### `review`

- 既存 script / 実行手順書の安全性、復旧のしやすさ、ログ粒度、機密情報リスクを指摘する
- 指摘は重大度順に返し、対象範囲、事前確認、冪等、クラッシュ地点からの再実行、rollback、変更前後の記録の欠落を優先する
- 実行可否を断定しすぎず、残リスクと追加確認事項を明示する

### `draft`

- まず対象範囲と前提を短く要約する
- 実行手順書、script の擬似構成、ログファイル設計、事前確認 / 実行の流れを提示する
- 必要な確認質問がある場合は、実装本文を作り込みすぎず質問を優先する
- [../assets/migration-runbook-template.md](../assets/migration-runbook-template.md) の章立てを起点にする
- クラッシュ地点 4 点からの再実行と、バッチごとの変更前後が本文に無い下書きは不合格

### `write-file`

- 保存先が明示された場合だけファイルを作成・更新する
- 対象プロジェクトの言語、script 配置、ログディレクトリ、テスト流儀に合わせる
- 実ファイルを書いた後、lint / test / 事前確認相当の検証を提案または実行する
- 本番実行コマンドは提示しても、ユーザー承認なしに実行しない

## 判断の補助

### 確認質問を優先する条件

- 本番環境かどうか不明
- 更新対象を一意に絞れない
- 事前確認が可能か不明
- ログ保存先がリポジトリ配下か外部保管先か不明
- 旧状態を取得できない
- rollback / backup が未定
- secrets / PII をログに含みそう
- 影響範囲が大きく、実行時間や rate limit が読めない

### scripts を追加しない既定

この skill 自体には `scripts/` を原則追加しない。対象プロジェクトごとに言語、DB、cloud provider、ログ形式が異なるため、まずは手順、判断基準、実行手順書テンプレートとして提供する。繰り返し同じ形式の migration script を生成・検証する必要が出た時点で、補助 script の追加を検討する。

## 参考にしたベストプラクティス

- [AWS Well-Architected: Use runbooks](https://docs.aws.amazon.com/wellarchitected/latest/operational-excellence-pillar/ops_ready_to_support_use_runbooks.html)
- [Terraform CLI workflow](https://developer.hashicorp.com/terraform/cli/run)
- [GitLab Batching best practices](https://docs.gitlab.com/development/database/batching_best_practices/) - 分割実行と、クラッシュ後の再開
- [GitLab Avoiding downtime in migrations](https://docs.gitlab.com/development/database/avoiding_downtime_in_migrations/)
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [Google SRE: Monitoring distributed systems](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Redgate Flyway rollback strategy](https://documentation.red-gate.com/flyway/deploying-database-changes-using-flyway/implementing-a-roll-back-strategy)
