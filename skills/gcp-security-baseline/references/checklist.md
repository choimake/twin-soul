# GCP 最低限のセキュリティ・コスト対策チェックリスト

サービス仕様の確認日: 2026-11-03。今回の追加・変更分: 2026-11-08。

Terraform の確認元: hashicorp/terraform-provider-google の main ブランチのドキュメント。

小規模チーム・個人向け。環境構築時や見直し時に、各項目の設定と根拠を確認する。

軸にした公式ベストプラクティス文書:

- [A: MVSP チェックリスト](https://docs.cloud.google.com/docs/security/gcmvsp)
- [B: Secure enterprise foundation controls](https://docs.cloud.google.com/docs/security/security-best-practices-catalog/secure-enterprise-foundations)（[課金対策](https://docs.cloud.google.com/docs/security/security-best-practices-genai/billing-controls)）
- [C: Enterprise foundations blueprint — 予防的対策](https://docs.cloud.google.com/architecture/blueprints/security-foundations/preventative-controls)、[運用のベストプラクティス](https://docs.cloud.google.com/architecture/blueprints/security-foundations/operation-best-practices)
- [D: Secure by default 組織](https://docs.cloud.google.com/resource-manager/docs/secure-by-default-organizations)

Terraform のリソース・属性は google provider を対象とする。組織がない場合の組織ポリシー利用は未確認（調べていない）のため、以下のリソース側の代替で確認する。既定の設定だけで「済」とせず、対象の設定を確認する。

## お金と連絡先

- [ ] **1. 予算と予算アラート** — 済: 対象の費用に予算があり、通知先と、利用可能な実績・予測の閾値が設定されている。
  - 組織: 不要。
  - Terraform: `google_billing_budget` の `billing_account`、`budget_filter.projects`、`amount.specified_amount` / `last_period_amount`、`threshold_rules.threshold_percent`（1.0 = 100%）、`threshold_rules.spend_basis`（`CURRENT_SPEND` / `FORECASTED_SPEND`）、`all_updates_rule.monitoring_notification_channels`、`disable_default_iam_recipients`。
  - 注意: 予算では課金を止められない。既定の通知先は課金管理者・課金ユーザー。カスタム期間では予測アラート不可。
  - 公式: <https://docs.cloud.google.com/billing/docs/how-to/budgets>

- [ ] **2. コストの異常検知** — 済: 課金アカウントの異常検知と通知が設定されている。
  - 組織: 不要。課金アカウント単位。
  - 手作業: コンソールの「お支払い」→「費用管理」→「異常」→「Manage anomalies」。Terraform 対応は未確認（調べていない）。
  - 注意: 閾値は自動。既定で課金管理者にメール通知。閾値の変更は `roles/billing.admin` のみで、設定は課金アカウント全体に適用される。
  - 公式: <https://docs.cloud.google.com/billing/docs/how-to/manage-anomalies>

- [ ] **3. Essential Contacts** — 済: 課金・法務・セキュリティなどの通知を受け取る連絡先が設定されている。
  - 組織: 不要。プロジェクト単位で設定可。公式では課金・法務・セキュリティの連絡先を組織レベルに置くことを推奨。
  - Terraform: `google_essential_contacts_contact` の `parent`、`email`、`language_tag`、`notification_category_subscriptions`。
  - 注意: 個人よりグループアドレスを推奨。
  - 公式: <https://docs.cloud.google.com/resource-manager/docs/managing-notification-contacts>

## 権限と認証

- [ ] **4. Terraform state の保護** — 済: remote backend（Cloud Storage を推奨）を使い、state の bucket に触れる主体をビルドの仕組みと強い権限の管理者に絞り、state を暗号化し、リポジトリに入れず、可能な範囲で秘密を state に置かない。
  - 確認: backend の構成、bucket のアクセス権、暗号化、リポジトリへの混入、秘密の有無と保管方法を確認する。秘密の値や state 内の値は読まない。
  - 注意: Cloud Storage の bucket は保存時に暗号化済み。追加の鍵は一律必須にしない。
  - 公式: <https://docs.cloud.google.com/docs/terraform/best-practices/security>

- [ ] **5. 人への基本ロール付与と最小権限** — 済: 人の役割に合う権限が付与され、本番では代替がない場合を除き基本ロールが付与されていない。
  - 組織: 不要。デフォルトの作成者ロール剥奪は組織が前提。
  - Terraform: `google_project_iam_member` / `google_project_iam_binding`。
  - 注意: 本番では代替がない場合を除き基本ロールを付与しない。`google_project_iam_policy` では既存ポリシーを丸ごと置換するため締め出しに注意し、`google_project_iam_member` / `google_project_iam_binding` / `google_project_iam_audit_config` と併用しない。
  - 公式: <https://docs.cloud.google.com/iam/docs/roles-overview>

- [ ] **6. SA キーと WIF** — 済: SA キーを使っていない、または使う理由があり 90 日以内にローテーションしている。
  - 組織: 組織ポリシーで禁止する場合は必要。組織なしではキーの利用状況と認証方法をユーザーに確認する。
  - Terraform: `google_org_policy_policy` の `spec.rules.enforce` を `"TRUE"` にする。制約は `iam.managed.disableServiceAccountKeyCreation`（優先）と `iam.disableServiceAccountKeyUpload`。WIF（Workload Identity Federation）は `google_iam_workload_identity_pool` / `google_iam_workload_identity_pool_provider` を探す。pool があるだけでは「済」にしない。
  - 注意: 上記の禁止制約は 2024-05-03 以降作成の組織では既定で強制。キーを使う場合は 90 日以内にローテーションする。従来の制約 `iam.disableServiceAccountKeyCreation` では HMAC キー作成も禁止される。
  - 公式: <https://docs.cloud.google.com/organization-policy/reference/org-policy-constraints>、[A]

- [ ] **7. デフォルト SA の `Editor`** — 済: デフォルト SA への `Editor` 自動付与が無効で、既存の `Editor` 付与も除かれている。
  - 組織: 不要。組織ありでは `google_org_policy_policy` で `iam.automaticIamGrantsForDefaultServiceAccounts` を確認する。
  - 組織なしの Terraform: `google_project_default_service_accounts` の `action = "DEPRIVILEGE"`。`DELETE` より推奨だが、確実に処理される保証はない。`import` 不可。
  - 注意: 自動付与を無効にしても、既に付与した `Editor` は消えない。
  - 公式: <https://docs.cloud.google.com/iam/docs/service-account-types>

- [ ] **8. ドメイン制限共有** — 済: 許可したドメインへの共有制限が設定され、既存の権限付与もその範囲に収まっている。
  - 組織: 必要。組織なしは対象外。
  - Terraform: `google_org_policy_policy` の `spec.rules.values.allowed_values` で `iam.allowedPolicyMemberDomains` を設定する。
  - 注意: 2024-05-03 以降作成の組織では既定で強制。既存の付与には遡らない。公式では `iam.managed.allowedPolicyMembers` を推奨しているが、この制約の Terraform 対応は未確認（調べていない）。
  - 公式: <https://docs.cloud.google.com/organization-policy/domain-restricted-sharing>

- [ ] **9. API キーの制限と未使用キー削除** — 済: API キーの用途・呼び出し元が制限され、未使用キーが削除されている。
  - 組織: 不要。
  - Terraform: `google_apikeys_key` の `restrictions.api_targets.service`、`browser_key_restrictions.allowed_referrers`、`server_key_restrictions.allowed_ips`、`android_key_restrictions`、`ios_key_restrictions`。
  - 注意: キーは URL やコードに入れず、定期的にローテーションする。
  - 公式: <https://docs.cloud.google.com/docs/authentication/api-keys-best-practices>

- [ ] **10. 2 段階認証と複数の管理者** — 済: 利用者が 2 段階認証を使い、管理者を複数用意している。
  - 組織: 個人アカウントでも確認する。組織ではアカウント管理方式に応じて確認する。
  - 手作業: Cloud Identity はコンソールの「組織」ページの「Enforce 2SV」、Workspace は管理コンソール（詳細手順: 未確認（調べていない））。SSO では IdP 側の MFA を確認する。Terraform 対応は未確認（調べていない）。
  - 注意: 個人の Google アカウントで Google Cloud を使う場合、2025-05-12 以降必須。Cloud Identity（SSO なし）では、2026-08-03 より前に作った組織は 2026-10-20 以降、2026-08-03 以降に作った組織は作成 30 日後から 2 段階認証が必須。管理者にはハードウェアキーを推奨。
  - 公式: <https://docs.cloud.google.com/docs/authentication/mfa-requirement>、[冗長な管理者: MVSP-CO-1.7（Basic）](https://docs.cloud.google.com/docs/security/gcmvsp/authentication-authorization)、[A]

## リソースと記録

- [ ] **11. バケットの均一アクセスと公開アクセス防止** — 済: Cloud Storage のバケットで均一バケットレベルアクセスと公開アクセス防止が有効になっている。
  - 組織: バケット単位なら不要。
  - Terraform: `google_storage_bucket` の `uniform_bucket_level_access = true`、`public_access_prevention = "enforced"`。組織側の制約は `storage.uniformBucketLevelAccess` と `storage.publicAccessPrevention`。
  - 注意: バケット属性の既定はそれぞれ `false` と `"inherited"`。均一アクセスの制約は 2024-05-03 以降作成の組織で既定で強制されるが、公開アクセス防止は既定の制約に含まれない。
  - 公式: <https://docs.cloud.google.com/storage/docs/public-access-prevention>

- [ ] **12. デフォルト VPC** — 済: デフォルト VPC を作らない設定があり、既存の `default` ネットワークの有無を確認して扱いを決めている（既存ネットワークの扱いは運用上の判断）。
  - 組織: 不要。組織ありでは制約 `compute.skipDefaultNetworkCreation` を確認する。
  - 組織なしの Terraform: `google_project` の `auto_create_network = false`（既定 `true`）。
  - 手作業: コンソールや `gcloud` で作成した既存プロジェクトも含め、`default` ネットワークが残っていないか確認する。
  - 注意: `auto_create_network = false` にすると、Terraform が既定ネットワークを作成直後に削除する。Compute API は有効のまま残る。可能なら組織の制約を使う。
  - 公式の推奨: `default` ネットワークは本番に推奨される構成ではなく、SSH・RDP を許可する受信ルールが最初から含まれる。本番では custom mode VPC を推奨している。
  - 運用判断: 公式に記載なし（調べた範囲）: 既存の `default` ネットワークを削除する明示的な推奨。削除するかは運用上の判断とする。制約 `compute.skipDefaultNetworkCreation` が既存ネットワークに遡及するかは未確認（調べていない）。
  - 公式: <https://docs.cloud.google.com/docs/security/gcmvsp/network-security>、<https://docs.cloud.google.com/vpc/docs/vpc>

- [ ] **13. SSH / RDP の受信制限** — 済: 22・3389 番への受信の許可元が必要な範囲に絞られ、IAP を使う場合は許可元が IAP の範囲になっている。
  - 対象: VM が無ければ対象外。
  - Terraform: `google_compute_firewall` を確認する。
  - 運用上の判断: MVSP-CO-1.51 は Intermediate。最低限の確認項目に含める判断は本チェックリストの運用上の判断とする。
  - 公式に記載なし（調べた範囲）: 参照先ページの IAP の具体的な IP 範囲。
  - 公式: <https://docs.cloud.google.com/docs/security/gcmvsp/network-security>

- [ ] **14. 監査ログ** — 済: 監査ログの種類を把握し、用途に応じて Data Access の有効化と除外対象を決め、設定している（運用上の判断）。
  - 組織: 不要。
  - Terraform: `google_project_iam_audit_config` の `service`（`"allServices"` 可）、`audit_log_config.log_type`（`DATA_READ` / `DATA_WRITE` / `ADMIN_READ`）、`exempted_members`。
  - 注意: Admin Activity と System Event は無効にできない。Data Access は BigQuery 以外では既定で無効。有効化でログ料金がかかる場合がある。
  - 公式: <https://docs.cloud.google.com/logging/docs/audit>

- [ ] **15. Security Command Center の Standard ティア** — 済: 組織で Security Command Center の Standard ティアが有効になっている。
  - 組織: 必要。組織なしは対象外。
  - 手作業: コンソールの「Security Command Center」。Terraform 対応は未確認（調べていない）。
  - 注意: Standard は追加料金なし。脅威検出は含まれない。
  - 公式: <https://docs.cloud.google.com/security-command-center/docs/service-tiers>

## 参考（チェックしない）

- 課金の自動停止: 予算の `all_updates_rule.pubsub_topic` と Pub/Sub・関数で構成する。停止すると全サービスが止まり、リソースが復元できない形で消えることがある。通知が遅れて予算を超えることがある。
  - 公式: <https://docs.cloud.google.com/billing/docs/how-to/disable-billing-with-notifications>
- 課金データの BigQuery エクスポート: 原則は有効化時点以降のデータのみ。マルチリージョンでは当月と前月を遡る。BigQuery 料金がかかる。
  - 公式: <https://docs.cloud.google.com/billing/docs/how-to/export-data-bigquery-setup>
- 不要な API: 有効にした API の必要性はユーザーに確認する。`google_project_service` での API 管理は未確認（調べていない）。

[A]: https://docs.cloud.google.com/docs/security/gcmvsp
