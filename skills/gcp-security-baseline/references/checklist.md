# GCP 最低限のセキュリティ・コスト対策チェックリスト

確認日: 2026-11-03

小規模チーム・個人向け。環境構築時や見直し時に、各項目の設定と根拠を確認する。

軸にした公式ベストプラクティス文書:

- [A: MVSP チェックリスト](https://docs.cloud.google.com/docs/security/gcmvsp)
- [B: Secure enterprise foundation controls](https://docs.cloud.google.com/docs/security/security-best-practices-catalog/secure-enterprise-foundations)（[課金対策](https://docs.cloud.google.com/docs/security/security-best-practices-genai/billing-controls)）
- [C: Enterprise foundations blueprint — 予防的対策](https://docs.cloud.google.com/architecture/blueprints/security-foundations/preventative-controls)、[運用のベストプラクティス](https://docs.cloud.google.com/architecture/blueprints/security-foundations/operation-best-practices)
- [D: Secure by default 組織](https://docs.cloud.google.com/resource-manager/docs/secure-by-default-organizations)

`Terraform` のリソース・属性は `google` provider を対象とする。組織がない場合の組織ポリシー利用は未確認のため、以下のリソース側の代替で確認する。既定の設定だけで「済」とせず、対象の設定を確認する。

- [ ] **1. 予算と予算アラート** — 対象の費用に予算を設け、通知先と実績・予測の閾値を確認する。
  - 組織: 不要。
  - `Terraform`: `google_billing_budget` の `billing_account`、`budget_filter.projects`、`amount.specified_amount` / `last_period_amount`、`threshold_rules.threshold_percent`、`threshold_rules.spend_basis`（`CURRENT_SPEND` / `FORECASTED_SPEND`）、`all_updates_rule.monitoring_notification_channels`、`disable_default_iam_recipients`。
  - 注意: 予算では課金を止められない。既定は実績の 50 / 90 / 100%、通知先は課金管理者・課金ユーザー。カスタム期間では予測アラート不可。通知チャネルは最大 5。ユーザーの `ADC`（アプリケーションのデフォルト認証情報）で実行する場合、provider に `billing_project` と `user_project_override = true` が必要。
  - 公式: <https://docs.cloud.google.com/billing/docs/how-to/budgets>

- [ ] **2. コストの異常検知** — 課金アカウントの異常検知と通知設定を確認する。
  - 組織: 不要。課金アカウント単位。
  - 手作業: コンソールの「お支払い」→「費用管理」→「異常」→「Manage anomalies」。`Terraform` 対応は未確認。
  - 注意: 閾値は自動。既定で課金管理者にメール通知。閾値の変更は `roles/billing.admin` のみで、設定は課金アカウント全体に適用される。
  - 公式: <https://docs.cloud.google.com/billing/docs/how-to/manage-anomalies>

- [ ] **3. 課金の自動停止（任意）** — 自動停止を採用する場合、通知から停止までの構成と停止時の影響を確認する。
  - 組織: 要否は未確認。
  - `Terraform`: 予算の `all_updates_rule.pubsub_topic` まで。停止処理は `Pub/Sub` と関数で構成する。
  - 注意: 公式では推奨していない。全サービス停止やリソースの復元不能な削除があり得る。通知の遅延で予算を超過する場合もある。
  - 公式: <https://docs.cloud.google.com/billing/docs/how-to/disable-billing-with-notifications>

- [ ] **4. 人への基本ロール付与と最小権限** — 人の役割に合う権限を付与し、基本ロールの付与を見直す。
  - 組織: 不要。デフォルトの作成者ロール剥奪は組織が前提。
  - `Terraform`: `google_project_iam_member` / `google_project_iam_binding`。
  - 注意: 本番では代替がない場合を除き基本ロールを付与しない。`google_project_iam_policy` では既存ポリシーを丸ごと置換するため締め出しに注意し、`google_project_iam_member` / `google_project_iam_binding` / `google_project_iam_audit_config` と併用しない。
  - 公式: <https://docs.cloud.google.com/iam/docs/roles-overview>

- [ ] **5. SA キーの作成・アップロード禁止と WIF** — SA キーを使わない認証を検討し、キーの作成・アップロード制限を確認する。
  - 組織: 組織ポリシーで禁止する場合は必要。組織なしではキーの利用状況と認証方法をユーザーに確認する。
  - `Terraform`: `google_org_policy_policy` の `spec.rules.enforce` を `"TRUE"` にする。制約は `iam.managed.disableServiceAccountKeyCreation`（優先）と `iam.disableServiceAccountKeyUpload`。`WIF`（Workload Identity Federation）の `Terraform` 対応は未確認。
  - 注意: 上記の禁止制約は 2024-05-03 以降作成の組織では既定で強制。キーを使う場合は 90 日以内にローテーションする。従来の制約 `iam.disableServiceAccountKeyCreation` では `HMAC` キー作成も禁止される。
  - 公式: <https://docs.cloud.google.com/organization-policy/reference/org-policy-constraints>、[A]

- [ ] **6. デフォルト SA の Editor 権限** — デフォルト SA への `Editor` 自動付与を無効にし、既存の付与も確認する。
  - 組織: 不要。組織ありでは `google_org_policy_policy` で `iam.automaticIamGrantsForDefaultServiceAccounts` を確認する。
  - 組織なしの `Terraform`: `google_project_default_service_accounts` の `action = "DEPRIVILEGE"`。`DELETE` より推奨だがベストエフォートで、import 不可。
  - 注意: 自動付与を無効にしても、既に付与した `Editor` は消えない。
  - 公式: <https://docs.cloud.google.com/iam/docs/service-account-types>

- [ ] **7. ドメイン制限共有** — 許可したドメインへの共有制限と、既存の権限付与を確認する。
  - 組織: 必要。組織なしは対象外。
  - `Terraform`: `google_org_policy_policy` の `spec.rules.values.allowed_values` で `iam.allowedPolicyMemberDomains` を設定する。
  - 注意: 2024-05-03 以降作成の組織では既定で強制。既存の付与には遡らない。公式では `iam.managed.allowedPolicyMembers` を推奨しているが、この制約の `Terraform` 対応は未確認。
  - 公式: <https://docs.cloud.google.com/organization-policy/domain-restricted-sharing>

- [ ] **8. バケットの均一アクセスと公開アクセス防止** — `Cloud Storage` のバケットで均一バケットレベルアクセスと公開アクセス防止を確認する。
  - 組織: バケット単位なら不要。
  - `Terraform`: `google_storage_bucket` の `uniform_bucket_level_access = true`、`public_access_prevention = "enforced"`。組織側の制約は `storage.uniformBucketLevelAccess` と `storage.publicAccessPrevention`。
  - 注意: バケット属性の既定はそれぞれ `false` と `"inherited"`。均一アクセスの制約は 2024-05-03 以降作成の組織で既定で強制されるが、公開アクセス防止は既定の制約に含まれない。
  - 公式: <https://docs.cloud.google.com/storage/docs/public-access-prevention>

- [ ] **9. 監査ログ** — 監査ログの種類を確認し、用途に応じて `Data Access` の有効化と除外対象を確認する。
  - 組織: 不要。
  - `Terraform`: `google_project_iam_audit_config` の `service`（`"allServices"` 可）、`audit_log_config.log_type`（`DATA_READ` / `DATA_WRITE` / `ADMIN_READ`）、`exempted_members`。
  - 注意: `Admin Activity` と `System Event` は無効にできない。`Data Access` は `BigQuery` 以外では既定で無効。有効化でログ料金がかかる場合がある。
  - 公式: <https://docs.cloud.google.com/logging/docs/audit>

- [ ] **10. API キーの制限と未使用キー削除** — `API` キーの用途・呼び出し元を制限し、未使用キーを削除しているか確認する。
  - 組織: 不要。
  - `Terraform`: `google_apikeys_key` の `restrictions.api_targets.service`、`browser_key_restrictions.allowed_referrers`、`server_key_restrictions.allowed_ips`、`android_key_restrictions`、`ios_key_restrictions`。
  - 注意: キーは URL やコードに入れず、定期的にローテーションする。
  - 公式: <https://docs.cloud.google.com/docs/authentication/api-keys-best-practices>

- [ ] **11. 2 段階認証と複数の管理者** — 利用者の 2 段階認証と、管理者を複数用意しているか確認する。
  - 組織: 個人アカウントでも確認する。組織ではアカウント管理方式に応じて確認する。
  - 手作業: `Cloud Identity` はコンソールの「組織」ページの「Enforce 2SV」、`Workspace` は管理コンソール（詳細手順は未確認）。`SSO` では `IdP` 側の `MFA` を確認する。`Terraform` 対応は未確認。
  - 注意: 個人の `Google` アカウントでは 2025-05-12 以降必須。管理者にはハードウェアキーを推奨。
  - 公式: <https://docs.cloud.google.com/docs/authentication/mfa-requirement>、[A]

- [ ] **12. デフォルト VPC と不要な API** — デフォルトの `VPC` を作らない設定と、不要な `API` を有効にしていないか確認する。
  - 組織: 不要。組織ありでは制約 `compute.skipDefaultNetworkCreation` を確認する。
  - 組織なしの `Terraform`: `google_project` の `auto_create_network = false`（既定 `true`）。`google_project_service` での `API` 管理は未確認のため、必要性はユーザーに確認する。
  - 注意: `auto_create_network = false` では作成直後にネットワークを削除する。`Compute API` は有効のまま残る。可能なら組織の制約を使う。
  - 公式: <https://docs.cloud.google.com/docs/security/gcmvsp/network-security>

- [ ] **13. `Security Command Center` の `Standard` ティア** — 組織で `Security Command Center` の `Standard` ティアを有効化しているか確認する。
  - 組織: 必要。組織なしは対象外。
  - 手作業: コンソールの「`Security Command Center`」。`Terraform` 対応は未確認。
  - 注意: `Standard` は追加料金なし。脅威検出は含まれない。
  - 公式: <https://docs.cloud.google.com/security-command-center/docs/service-tiers>

- [ ] **14. 課金データの `BigQuery` エクスポート（任意）** — エクスポートを採用する場合、課金データの出力設定を確認する。
  - 組織: 不要。
  - 手作業: コンソールの「お支払い」→「課金データのエクスポート」。`Terraform` 対応は未確認。
  - 注意: 原則は有効化時点以降のデータのみ。マルチリージョンでは当月と前月を遡る。`BigQuery` 料金がかかる。
  - 公式: <https://docs.cloud.google.com/billing/docs/how-to/export-data-bigquery-setup>

- [ ] **15. `Essential Contacts`** — 課金・法務・セキュリティなどの通知を受け取る連絡先を確認する。
  - 組織: 不要。プロジェクト単位で設定可。公式では課金・法務・セキュリティの連絡先を組織レベルに置くことを推奨。
  - `Terraform`: `google_essential_contacts_contact` の `parent`、`email`、`language_tag`、`notification_category_subscriptions`。
  - 注意: 個人よりグループアドレスを推奨。ユーザーの `ADC` で実行する場合、provider に `billing_project` と `user_project_override` が必要。
  - 公式: <https://docs.cloud.google.com/resource-manager/docs/managing-notification-contacts>

[A]: https://docs.cloud.google.com/docs/security/gcmvsp
