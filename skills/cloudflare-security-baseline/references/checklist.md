# Cloudflare 構築時の最低限チェックリスト

サービス仕様の確認日: 2026-11-03。2026-11-08 に追加・変更した項目: 2（アカウントとドメインの継続管理）、6（Budget alert）、10（SSL/TLS の設定値）。

Terraform provider の確認元: cloudflare/cloudflare v5.28.1。

小規模チーム・個人が、アカウント・ゾーンの初期設定を確認するために使う。各項目を「済 / 要対応 / 要確認 / 対象外」で判定し、根拠を残す。設定は自動適用しない。

軸にした公式文書:

- [A: Account and domain management best practices](https://developers.cloudflare.com/fundamentals/reference/best-practices/)
- B: Secure your website の学習パス（[アカウントの 2FA](https://developers.cloudflare.com/learning-paths/application-security/account-security/set-up-2fa/)、[DNSSEC](https://developers.cloudflare.com/learning-paths/application-security/default-traffic-security/dnssec/)、[マネージドルール](https://developers.cloudflare.com/learning-paths/application-security/firewall/managed-rules/)）
- [C: Protect your origin server](https://developers.cloudflare.com/fundamentals/security/protect-your-origin-server/)
- [Terraform best practices](https://developers.cloudflare.com/terraform/advanced-topics/best-practices/)

不明点は「公式に記載なし（調べた範囲）」と「未確認（調べていない）」を区別する。公式に推奨値が無い場合は、運用上の判断と分けて記録する。

## アカウントと認証

- [ ] **1. 2FA 強制**: 済: SSO を使わない全メンバーへの 2FA が強制され、バックアップコードを保管している。SSO を使うメンバーは IdP 側で多要素認証を使っている。
  - IaC: `cloudflare_account` の `settings.enforce_twofactor`（Boolean）。
  - 手作業: バックアップコードの保管の有無と保管方法を確認する。値は集めない。場所は「Profile > Security & Authentication > Backup codes」。SSO の導入そのものは求めない。個人設定は「My Profile > Authentication」。強制画面の場所は未確認（調べていない）。
  - 注意: 有効化は `Super Administrator`（以下 `Super Admin`）のみ。SSO ユーザーは 2FA を設定できない。
  - 公式: [2FA 設定](https://developers.cloudflare.com/learning-paths/application-security/account-security/set-up-2fa/)、[2FA](https://developers.cloudflare.com/fundamentals/user-profiles/2fa/)

- [ ] **2. アカウントとドメインの継続管理**: 済: 支払情報を最新に保ち、本人が管理できなくなったときの手順がある。事業で使う場合は加えて、ドメインの登録名義とベンダーのアカウントが組織名であり、連絡用メールがそのドメインに頼らない。
  - 手作業: 支払情報の更新状況と本人不在時の手順を確認する。事業向けの名義・連絡用メールの条件は、個人利用には一律に求めない。
  - 公式: [アカウントとドメイン管理のベストプラクティス](https://developers.cloudflare.com/fundamentals/reference/best-practices/)

- [ ] **3. メンバーとロール**: 済: アカウントへのアクセスを 1 人に集中させず、不要なメンバー・権限がない（権限の範囲は運用上の判断）。
  - IaC: `cloudflare_account_member` の `roles`、`policies`（`access` / `permission_groups` / `resource_groups`）、`status`。
  - 手作業:「Members」。
  - 公式の記述: アカウントへのアクセスを 1 人に集中させない。人数・最小権限の明示推奨は無い。
  - 運用上の判断: 締め出し回避のため `Super Admin` は 2 人以上を検討し、それ以外の権限は必要な範囲に絞る。
  - 注意: `Super Admin` は課金・メンバー・アカウント所有トークンを操作でき、他の `Super Admin` の権限も取り消せる。
  - 公式: [ベストプラクティス](https://developers.cloudflare.com/fundamentals/reference/best-practices/)、[メンバー追加](https://developers.cloudflare.com/learning-paths/application-security/account-security/add-other-members/)、[ロール](https://developers.cloudflare.com/fundamentals/manage-members/roles/)

- [ ] **4. API トークン**: 済: Global API Key を使わず、トークンの権限範囲・IP 制限・期限の採否を確認し、必要な範囲に絞っている（範囲と制限の採否は運用上の判断）。
  - IaC: `cloudflare_api_token`（ユーザー所有）/ `cloudflare_account_token`（アカウント所有）の `policies`、`condition.request_ip.in` / `not_in`、`expires_on`、`not_before`、`status`。provider 認証は `api_token`（環境変数 `CLOUDFLARE_API_TOKEN`）。
  - 手作業:「My Profile > API Tokens」、またはアカウントの「API Tokens」。
  - 注意: 既定では IP 制限・期限なし。provider の `api_key` は legacy。アカウント所有トークンは一部製品で使えない。
  - 公式: [Global API Key](https://developers.cloudflare.com/fundamentals/api/get-started/keys/)、[トークン制限](https://developers.cloudflare.com/fundamentals/api/how-to/restrict-tokens/)、[アカウント所有トークン](https://developers.cloudflare.com/fundamentals/api/get-started/account-owned-tokens/)

- [ ] **5. state と認証情報**: 済: 認証情報を平文で保存せず、Terraform state を暗号化し、アクセスを制限している。
  - IaC: backend 設定を確認。
  - 手作業: 認証情報の保管方法を確認。公式ではローカルに `cf-vault`、CI に secret manager を挙げている。
  - 注意: `cloudflare_api_token` / `cloudflare_account_token` の `value` は Read-only かつ Sensitive。Sensitive は表示を伏せるだけで、state には平文で残る。provider 属性の ephemeral / write-only 対応は未確認（調べていない）。値自体は読まない。
  - 公式: [Terraform best practices](https://developers.cloudflare.com/terraform/advanced-topics/best-practices/)、[機密データの管理](https://developer.hashicorp.com/terraform/language/manage-sensitive-data)

## コストと運用の通知

- [ ] **6. Budget alert**: 済: 金額しきい値と通知先を設定している（しきい値は運用上の判断）。
  - 対象プラン: Pay-as-you-go アカウント限定。Enterprise 契約は対象外。Free での扱いは公式に記載なし（調べた範囲: Budget alerts のページと既定のアラートの changelog）。
  - 手作業:「Manage Account > Billing > Billable Usage > Create budget alert」。Terraform 対応は未確認（調べていない）。
  - 注意: 既存の Budget alert がない対象アカウントには、既定の $10 のアラートを順次適用し、次の請求サイクルの切り替わりから有効にする。通知だけで利用は止めない。Workers Paid などの月額固定費は含まれない。当期の累計で評価する。使用量は 1 日 1 回集計するため、通知はしきい値に達した翌日に届く。
  - 公式: [Budget alerts](https://developers.cloudflare.com/billing/manage/budget-alerts/)、[既定のアラート](https://developers.cloudflare.com/changelog/post/2026-06-15-budget-alerts-default-on/)

- [ ] **7. Usage Based Billing 通知**: 済: 対象製品の使用量しきい値を設定し、請求先メールを確認している（しきい値は運用上の判断）。
  - 対象プラン: Pro 以上かつ Pay-as-you-go 限定。Free 不可。
  - IaC: `cloudflare_notification_policy` の `alert_type = "billing_usage_alert"`、`filters.product` / `filters.limit`。
  - 手作業:「Notifications > Add > Billable Usage」。
  - 注意: 公式の例は Argo と Load Balancing のみ。選べる製品は Notifications の画面で確認する。送り先は請求先メール。
  - 公式: [Usage Based Billing](https://developers.cloudflare.com/billing/understand/usage-based-billing/)、[通知一覧](https://developers.cloudflare.com/notifications/notification-available/)

- [ ] **8. Workers CPU 上限**: 済: Workers の CPU 上限を設定し、請求通知と組み合わせている（上限値は運用上の判断）。
  - 対象プラン: Workers Paid（Standard）。Free は 1 日 10 万リクエスト超で Error 1027 となり停止する。
  - IaC: `cloudflare_workers_script` の `limits.cpu_ms`、`limits.subrequests`。`wrangler` は `limits.cpu_ms`。
  - 手作業:「Workers & Pages > 対象 Worker > Settings > CPU Limits」。
  - 注意: デプロイ後だけ効く。リクエスト数自体は制限できないため Budget alert と組み合わせる。
  - 公式: [料金](https://developers.cloudflare.com/workers/platform/pricing/)、[上限](https://developers.cloudflare.com/workers/platform/limits/)

- [ ] **9. 監査ログとセッション**: 済: 監査ログとセッションの見る場所を知っていて、直近に確認した日を答えられる（運用上の判断）。
  - 手作業:「Manage Account > Audit Logs」、「My Profile > Sessions」。確認作業のため Terraform では判定しない。
  - 注意: Audit Logs v1 は全プラン。v2 の対象プランは未確認（調べていない）。不審な操作が無いことの保証や監査は求めない。
  - 公式: [監査ログの確認](https://developers.cloudflare.com/learning-paths/application-security/account-security/review-audit-logs/)、[監査ログ](https://developers.cloudflare.com/fundamentals/account/account-security/audit-logs/)、[セッションの確認](https://developers.cloudflare.com/learning-paths/application-security/account-security/review-active-sessions/)

## ゾーンとオリジン

- [ ] **10. SSL/TLS**: 済: 実際の暗号化モードが Full または Full (strict) であり、Automatic SSL/TLS を選んでいるかを把握し、Always Use HTTPS、最小 TLS、HSTS の採否と設定を確認している（採否は運用上の判断）。
  - IaC: `cloudflare_zone_setting` の `setting_id` / `value`。`setting_id` は `ssl`、`always_use_https`、`min_tls_version`、`security_header`（`strict_transport_security` の `max_age` / `include_subdomains` / `preload` / `nosniff`）。Full (strict) は `setting_id = "ssl"`、`value = "strict"`。
  - 手作業: Automatic SSL/TLS の選択と実際の暗号化モードを分けて確認する。実際のモードが `flexible` なら「要対応」。「SSL/TLS Overview」（暗号化モード）、「Edge Certificates」（HTTPS・最小 TLS・HSTS）。
  - 公式の記述: Full または Full (strict) を強く推奨。最小 TLS の既定は 1.0、一般には 1.3、PCI 対象なら 1.2 を推奨。
  - 運用上の判断: オリジン証明書の条件を満たすか確認し、Full (strict) の採用を判断する。
  - 注意: Always Use HTTPS、HSTS、最小 TLS は全プラン。Full (strict) の対象プランは未確認（調べていない）。Full (strict) には期限内・信頼 CA（Origin CA 可）・ホスト名一致の証明書が必要。不適合なら 526。HSTS は HTTPS を外すと `max-age` の間アクセスできなくなる。`preload` は `max-age` 12 か月以上。
  - 公式: [暗号化モード](https://developers.cloudflare.com/ssl/origin-configuration/ssl-modes/)、[Full (strict)](https://developers.cloudflare.com/ssl/origin-configuration/ssl-modes/full-strict/)、[HTTPS](https://developers.cloudflare.com/ssl/edge-certificates/additional-options/always-use-https/)、[最小 TLS](https://developers.cloudflare.com/ssl/edge-certificates/additional-options/minimum-tls/)、[HSTS](https://developers.cloudflare.com/ssl/edge-certificates/additional-options/http-strict-transport-security/)

- [ ] **11. DNS プロキシ**: 済: Web 用レコードをプロキシし、DNS-only レコードからのオリジン IP 露出を確認している。
  - IaC: `cloudflare_dns_record` の `proxied`。
  - 手作業:「DNS > Records」。
  - 注意: SPF/TXT や同居メールから IP が漏れる。過去の DNS 履歴は残るため、公式ではオンボード後のオリジン IP 変更を推奨。
  - 公式: [オリジン保護](https://developers.cloudflare.com/fundamentals/security/protect-your-origin-server/)、[DDoS への事前対策](https://developers.cloudflare.com/ddos-protection/best-practices/proactive-defense/)

- [ ] **12. DNSSEC**: 済: DNSSEC が有効で、レジストラに DS が登録されている。
  - IaC: `cloudflare_zone_dnssec` の `status = "active"`。`ds` などは出力値。
  - 手作業:「DNS > Settings > DNSSEC」とレジストラでの DS 登録（Cloudflare Registrar なら自動）。
  - 注意: ネームサーバー移行前に移行元の DNSSEC を無効にし、SERVFAIL を避ける。
  - 公式: [DNSSEC 設定](https://developers.cloudflare.com/learning-paths/application-security/default-traffic-security/dnssec/)、[DNSSEC](https://developers.cloudflare.com/dns/dnssec/)

- [ ] **13. オリジン保護**: 済: AOP・Tunnel・IP 許可リストのどれか 1 つ以上を採用し、オリジンが Cloudflare 以外からの直接接続を拒否している（または公開経路を持たない）。
  - IaC: ゾーン単位の `cloudflare_authenticated_origin_pulls_settings.enabled`。自前証明書リソースは未確認（調べていない）。Tunnel は `cloudflare_zero_trust_tunnel_cloudflared`（`config_src`、`tunnel_secret`。後者は Sensitive）。
  - 手作業: オリジン側ファイアウォールは Cloudflare の外で確認する。Cloudflare 側の設定だけでは「済」にしない。
  - 注意: Global AOP の証明書は全顧客共有で、他顧客からも通る。ゾーン・ホスト名単位の自前証明書を検討する。AOP は Full か Full (strict) でないと効かない。
  - 公式: [オリジン保護](https://developers.cloudflare.com/fundamentals/security/protect-your-origin-server/)、[Authenticated Origin Pulls](https://developers.cloudflare.com/ssl/origin-configuration/authenticated-origin-pull/)

- [ ] **14. WAF と DDoS**: 済: プランに合うマネージドルールが有効で、DDoS 防御が常時有効であることを確認している。
  - 対象プラン: Free Managed Ruleset は全プラン、Cloudflare Managed Ruleset と OWASP は Pro 以上。DDoS は常時有効。
  - IaC: `cloudflare_ruleset` の `phase`（`http_request_firewall_managed` / `ddos_l7`）、`action = "execute"`、`action_parameters.id`。具体的な組み合わせは未確認（調べていない）。
  - 手作業:「Security > Settings」（「Web application exploits」）。
  - 注意: Free Managed Ruleset が既定で有効かは公式に記載なし（調べた範囲: WAF マネージドルールのページ）。ダッシュボードで実際の状態を確認する。コード例は組み合わせを推測して補わない。
  - 公式: [マネージドルール](https://developers.cloudflare.com/waf/managed-rules/)、[学習パス](https://developers.cloudflare.com/learning-paths/application-security/firewall/managed-rules/)、[DDoS への事前対策](https://developers.cloudflare.com/ddos-protection/best-practices/proactive-defense/)

- [ ] **15. セキュリティ・障害の通知**: 済: DDoS・SSL・障害・メンテナンスの通知と送り先を設定している。
  - IaC: `cloudflare_notification_policy` の `alert_type`、`mechanisms.email` / `webhooks` / `pagerduty`、`filters`。候補は `dos_attack_l7`、`universal_ssl_event_type`、`incident_alert`（`filters.incident_impact` / `affected_components`）、`maintenance_event_notification`。表示名と `alert_type` の対応は未確認（調べていない）。
  - 手作業:「Notifications > Add」。
  - 注意: 既定で有効かは公式に記載なし（調べた範囲: 通知一覧・DDoS アラート・通知設定）。
  - 公式: [通知一覧](https://developers.cloudflare.com/notifications/notification-available/)、[DDoS アラート](https://developers.cloudflare.com/ddos-protection/reference/alerts/)、[通知設定](https://developers.cloudflare.com/notifications/get-started/)

## 参考（チェックしない）

### Dashboard SSO の導入

SSO の導入そのものは求めない。全プラン無料。自社メールドメイン（gmail.com 不可）、Zero Trust 組織（Free 可）、`Super Admin` が必要。

Zero Trust で IdP 設定 →「Members」で SSO ドメイン追加 → TXT 検証 →「Enable」。Terraform 対応は未確認（調べていない）。

公式: [Dashboard SSO](https://developers.cloudflare.com/fundamentals/manage-members/dashboard-sso/)
