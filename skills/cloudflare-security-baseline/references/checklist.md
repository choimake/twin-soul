# Cloudflare 構築時の最低限チェックリスト

確認日: 2026-11-03。確認した cloudflare/cloudflare provider: v5.28.1。

小規模チーム・個人が、アカウント・ゾーンの初期設定を確認するために使う。各項目を「済 / 未 / 対象外 / 要確認」で判定し、根拠を残す。設定は自動適用しない。

軸にした公式文書:

- [A: Account and domain management best practices](https://developers.cloudflare.com/fundamentals/reference/best-practices/)
- B: Secure your website の学習パス（[アカウントの 2FA](https://developers.cloudflare.com/learning-paths/application-security/account-security/set-up-2fa/)、[DNSSEC](https://developers.cloudflare.com/learning-paths/application-security/default-traffic-security/dnssec/)、[マネージドルール](https://developers.cloudflare.com/learning-paths/application-security/firewall/managed-rules/)）
- [C: Protect your origin server](https://developers.cloudflare.com/fundamentals/security/protect-your-origin-server/)
- [Terraform best practices](https://developers.cloudflare.com/terraform/advanced-topics/best-practices/)

プランの記載が無いものは利用可否を断定しない。公式に推奨値が無い場合は、運用上の判断と分けて記録する。

## アカウントと認証

- [ ] **1. 2FA 強制**: 全メンバーへの 2FA 強制を確認する。
  - 対象プラン: 公式にプランの記載なし（未確認）。
  - IaC: `cloudflare_account` の `settings.enforce_twofactor`（Boolean）。手作業: 個人設定は「My Profile > Authentication」。強制画面の場所は未確認。
  - 注意: 有効化は Super Administrator（以下 Super Admin）のみ。SSO ユーザーは 2FA を設定できない。
  - 公式: [2FA 設定](https://developers.cloudflare.com/learning-paths/application-security/account-security/set-up-2fa/)、[2FA](https://developers.cloudflare.com/fundamentals/user-profiles/2fa/)

- [ ] **2. バックアップコード**: 2FA のバックアップコードを保管しているか確認する。
  - 対象プラン: 公式にプランの記載なし（未確認）。
  - 手作業:「Profile > Security & Authentication > Backup codes」。Terraform では扱わない。
  - 注意: コードの値は収集せず、保管の有無を確認する。
  - 公式: [アカウント管理のベストプラクティス](https://developers.cloudflare.com/fundamentals/reference/best-practices/)、[2FA 設定](https://developers.cloudflare.com/learning-paths/application-security/account-security/set-up-2fa/)

- [ ] **3. Dashboard SSO（任意）**: チームでの採否と、採用時の設定を確認する。
  - 対象プラン: 全プラン無料。自社メールドメイン（gmail.com 不可）、Zero Trust 組織（Free 可）、Super Admin が必要。
  - 手作業: Zero Trust で IdP 設定 →「Members」で SSO ドメイン追加 → TXT 検証 →「Enable」。Terraform 対応は未確認。
  - 公式: [Dashboard SSO](https://developers.cloudflare.com/fundamentals/manage-members/dashboard-sso/)

- [ ] **4. メンバーとロール**: 締め出しを避ける体制と、不要なメンバー・権限がないかを確認する。
  - 対象プラン: 公式にプランの記載なし（未確認）。
  - IaC: `cloudflare_account_member` の `roles`、`policies`（`access` / `permission_groups` / `resource_groups`）、`status`。手作業:「Members」。
  - 公式の記述: アカウントへのアクセスを 1 人に集中させない。人数・最小権限の明示推奨は無い。
  - 運用上の判断: 締め出し回避のため Super Admin は 2 人以上を検討し、それ以外の権限は必要な範囲に絞る。
  - 注意: Super Admin は課金・メンバー・アカウント所有トークンを操作でき、他の Super Admin の権限も取り消せる。
  - 公式: [ベストプラクティス](https://developers.cloudflare.com/fundamentals/reference/best-practices/)、[メンバー追加](https://developers.cloudflare.com/learning-paths/application-security/account-security/add-other-members/)、[ロール](https://developers.cloudflare.com/fundamentals/manage-members/roles/)

- [ ] **5. API トークン**: Global API Key の利用を避け、トークンの権限範囲・IP 制限・期限を確認する。
  - 対象プラン: 公式にプランの記載なし（未確認）。
  - IaC: `cloudflare_api_token`（ユーザー所有）/ `cloudflare_account_token`（アカウント所有）の `policies`、`condition.request_ip.in` / `not_in`、`expires_on`、`not_before`、`status`。provider 認証は `api_token`（環境変数 `CLOUDFLARE_API_TOKEN`）。
  - 手作業:「My Profile > API Tokens」、またはアカウントの「API Tokens」。
  - 注意: 既定では IP 制限・期限なし。provider の `api_key` は legacy。アカウント所有トークンは一部製品で使えない。
  - 公式: [Global API Key](https://developers.cloudflare.com/fundamentals/api/get-started/keys/)、[トークン制限](https://developers.cloudflare.com/fundamentals/api/how-to/restrict-tokens/)、[アカウント所有トークン](https://developers.cloudflare.com/fundamentals/api/get-started/account-owned-tokens/)

- [ ] **6. state と認証情報**: 認証情報の平文保存を避け、Terraform state の暗号化・アクセス制限を確認する。
  - 対象プラン: プランによらない管理上の確認。
  - IaC・手作業: backend 設定と認証情報の保管方法を確認。公式ではローカルに `cf-vault`、CI に secret manager を挙げている。
  - 注意: `cloudflare_api_token` / `cloudflare_account_token` の `value` は Read-only かつ Sensitive。Sensitive は表示を伏せるだけで、state には平文で残る。provider 属性の ephemeral / write-only 対応は未確認。値自体は読まない。
  - 公式: [Terraform best practices](https://developers.cloudflare.com/terraform/advanced-topics/best-practices/)、[機密データの管理](https://developer.hashicorp.com/terraform/language/manage-sensitive-data)

## コストと運用の通知

- [ ] **7. Budget alert**: 金額しきい値と通知設定を確認する。
  - 対象プラン: Pay-as-you-go アカウント限定。Enterprise 契約は対象外。Free での扱いは未確認。
  - 手作業:「Manage Account > Billing > Billable Usage > Create budget alert」。Terraform 対応は未確認。
  - 注意: 2026-06-15 から対象アカウントに既定で $10 のアラート。通知だけで利用は止めない。Workers Paid などの月額固定費は含まれない。累計か予測かは公式文書間で記述が食い違うため断定しない。
  - 公式: [Budget alerts](https://developers.cloudflare.com/billing/manage/budget-alerts/)、[既定のアラート](https://developers.cloudflare.com/changelog/post/2026-06-15-budget-alerts-default-on/)

- [ ] **8. Usage Based Billing 通知**: 対象製品の使用量しきい値と請求先メールを確認する。
  - 対象プラン: Pro 以上かつ Pay-as-you-go 限定。Free 不可。
  - IaC: `cloudflare_notification_policy` の `alert_type = "billing_usage_alert"`、`filters.product` / `filters.limit`。手作業:「Notifications > Add > Billable Usage」。
  - 注意: 公式の例は Argo と Load Balancing のみ。Workers / R2 が対象かは未確認。送り先は請求先メール。
  - 公式: [Usage Based Billing](https://developers.cloudflare.com/billing/understand/usage-based-billing/)、[通知一覧](https://developers.cloudflare.com/notifications/notification-available/)

- [ ] **9. Workers CPU 上限**: Workers を使う場合、CPU 上限と請求通知の組み合わせを確認する。
  - 対象プラン: Workers Paid（Standard）。Free は 1 日 10 万リクエスト超で Error 1027 となり停止する。
  - IaC: `cloudflare_workers_script` の `limits.cpu_ms`、`limits.subrequests`。`wrangler` は `limits.cpu_ms`。手作業:「Workers & Pages > 対象 Worker > Settings > CPU Limits」。
  - 注意: CPU 上限の既定は 30 秒、最大 5 分（300,000 ms）。デプロイ後だけ効く。リクエスト数自体は制限できないため Budget alert と組み合わせる。
  - 公式: [料金](https://developers.cloudflare.com/workers/platform/pricing/)、[上限](https://developers.cloudflare.com/workers/platform/limits/)

- [ ] **10. 監査ログとセッション**: 監査ログとアクティブセッションに不審な操作・接続がないか確認する。
  - 対象プラン: Audit Logs v1 は全プラン。v2 の対象プランは未確認。
  - 手作業:「Manage Account > Audit Logs」、「My Profile > Sessions」。確認作業のため Terraform では判定しない。
  - 注意: v2 の保持は 18 か月、ダッシュボードは直近 90 日。セッションは 72 時間無操作で切れる。
  - 公式: [監査ログの確認](https://developers.cloudflare.com/learning-paths/application-security/account-security/review-audit-logs/)、[監査ログ](https://developers.cloudflare.com/fundamentals/account/account-security/audit-logs/)、[セッションの確認](https://developers.cloudflare.com/learning-paths/application-security/account-security/review-active-sessions/)

## ゾーンとオリジン

- [ ] **11. SSL/TLS**: 暗号化モード、Always Use HTTPS、最小 TLS、HSTS の採否と設定を確認する。
  - 対象プラン: Always Use HTTPS、HSTS、最小 TLS は全プラン。Full (strict) の対象プランは未確認。
  - IaC: `cloudflare_zone_setting` の `setting_id` / `value`。`setting_id` は `ssl`、`always_use_https`、`min_tls_version`、`security_header`（`strict_transport_security` の `max_age` / `include_subdomains` / `preload` / `nosniff`）。Full (strict) にする `ssl` の値は未確認。
  - 手作業:「SSL/TLS Overview」（暗号化モード）、「Edge Certificates」（HTTPS・最小 TLS・HSTS）。
  - 公式の記述: Full または Full (strict) を強く推奨。最小 TLS の既定は 1.0、一般には 1.3、PCI 対象なら 1.2 を推奨。
  - 運用上の判断: オリジン証明書の条件を満たすか確認し、Full (strict) の採用を判断する。
  - 注意: Full (strict) には期限内・信頼 CA（Origin CA 可）・ホスト名一致の証明書が必要。不適合なら 526。HSTS は HTTPS を外すと `max-age` の間アクセスできなくなる。`preload` は `max-age` 12 か月以上。
  - 公式: [暗号化モード](https://developers.cloudflare.com/ssl/origin-configuration/ssl-modes/)、[Full (strict)](https://developers.cloudflare.com/ssl/origin-configuration/ssl-modes/full-strict/)、[HTTPS](https://developers.cloudflare.com/ssl/edge-certificates/additional-options/always-use-https/)、[最小 TLS](https://developers.cloudflare.com/ssl/edge-certificates/additional-options/minimum-tls/)、[HSTS](https://developers.cloudflare.com/ssl/edge-certificates/additional-options/http-strict-transport-security/)

- [ ] **12. DNS プロキシ**: Web 用レコードをプロキシし、DNS-only レコードからのオリジン IP 露出も確認する。
  - 対象プラン: 公式にプランの記載なし（未確認）。
  - IaC: `cloudflare_dns_record` の `proxied`。手作業:「DNS > Records」。
  - 注意: SPF/TXT や同居メールから IP が漏れる。過去の DNS 履歴は残るため、公式ではオンボード後のオリジン IP 変更を推奨。
  - 公式: [オリジン保護](https://developers.cloudflare.com/fundamentals/security/protect-your-origin-server/)、[DDoS への事前対策](https://developers.cloudflare.com/ddos-protection/best-practices/proactive-defense/)

- [ ] **13. DNSSEC**: 有効化とレジストラへの DS 登録を確認する。
  - 対象プラン: 公式にプランの記載なし（未確認）。
  - IaC: `cloudflare_zone_dnssec` の `status = "active"`。`ds` などは出力値。手作業:「DNS > Settings > DNSSEC」とレジストラでの DS 登録（Cloudflare Registrar なら自動）。
  - 注意: ネームサーバー移行前に移行元の DNSSEC を無効にし、SERVFAIL を避ける。
  - 公式: [DNSSEC 設定](https://developers.cloudflare.com/learning-paths/application-security/default-traffic-security/dnssec/)、[DNSSEC](https://developers.cloudflare.com/dns/dnssec/)

- [ ] **14. オリジン保護**: AOP・Tunnel・IP 許可リストによるオリジンへの直接アクセス対策を確認する。
  - 対象プラン: 全プラン。
  - IaC: ゾーン単位の `cloudflare_authenticated_origin_pulls_settings.enabled`。自前証明書リソースは未確認。Tunnel は `cloudflare_zero_trust_tunnel_cloudflared`（`config_src`、`tunnel_secret`。後者は Sensitive）。オリジン側ファイアウォールは Cloudflare の外で確認する。
  - 注意: Global AOP の証明書は全顧客共有で、他顧客からも通る。ゾーン・ホスト名単位の自前証明書を検討する。AOP は Full か Full (strict) でないと効かない。
  - 公式: [オリジン保護](https://developers.cloudflare.com/fundamentals/security/protect-your-origin-server/)、[Authenticated Origin Pulls](https://developers.cloudflare.com/ssl/origin-configuration/authenticated-origin-pull/)

- [ ] **15. WAF と DDoS**: プランに合うマネージドルールの利用状況と DDoS 防御の既定を確認する。
  - 対象プラン: Free Managed Ruleset は全プラン、Cloudflare Managed Ruleset と OWASP は Pro 以上。DDoS は常時有効。
  - IaC: `cloudflare_ruleset` の `phase`（`http_request_firewall_managed` / `ddos_l7`）、`action = "execute"`、`action_parameters.id`。具体的な組み合わせは未確認。手作業:「Security > Settings」（「Web application exploits」）。
  - 注意: Free Managed Ruleset が既定で有効かは未確認。コード例は組み合わせを推測して補わない。
  - 公式: [マネージドルール](https://developers.cloudflare.com/waf/managed-rules/)、[学習パス](https://developers.cloudflare.com/learning-paths/application-security/firewall/managed-rules/)、[DDoS への事前対策](https://developers.cloudflare.com/ddos-protection/best-practices/proactive-defense/)

- [ ] **16. セキュリティ・障害の通知**: DDoS・SSL・障害・メンテナンスの通知設定と送り先を確認する。
  - 対象プラン: 全プラン。
  - IaC: `cloudflare_notification_policy` の `alert_type`、`mechanisms.email` / `webhooks` / `pagerduty`、`filters`。候補は `dos_attack_l7`、`universal_ssl_event_type`、`incident_alert`（`filters.incident_impact` / `affected_components`）、`maintenance_event_notification`。表示名と `alert_type` の対応は未確認。
  - 手作業:「Notifications > Add」。
  - 注意: 既定で有効かは記載なし。HTTP DDoS Alert は 100 rps 超の攻撃を緩和したときに送られる。
  - 公式: [通知一覧](https://developers.cloudflare.com/notifications/notification-available/)、[DDoS アラート](https://developers.cloudflare.com/ddos-protection/reference/alerts/)、[通知設定](https://developers.cloudflare.com/notifications/get-started/)
