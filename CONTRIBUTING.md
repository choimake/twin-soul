# 貢献ガイド

`twin-soul` は、AI エージェント用 `skill` と運用ルールの正本リポジトリです。変更は小さく、レビューしやすく、`AGENTS.md` と `specs/document-boundaries.md` に書かれた文書境界に沿って進めてください。

## 正本

- `skill` は `skills/<skill-name>/` を編集する
- `.agents/skills/`、`.claude/skills/`、`.cursor/skills/` は APM 展開物として扱い、直接編集・コミットしない
- リポジトリ横断の方針は `AGENTS.md` またはトップレベルの `rules/` に置く
- `.cursor/rules/` や `.claude/rules/` は再導入しない。トップレベルの `rules/` を正本にする
- 詳細仕様は `specs/`、判断履歴は `decisions/` に置く

## セットアップ

```bash
mise install
```

## 検証

プルリクエストを開く前に、ローカルで次を実行します。

```bash
mise run ci:lint
mise run ci:apm
```

ローカルでの編集互換のために展開済み `skill` のコピーを更新する場合は、次を実行します。

```bash
APM_LEGACY_SKILL_PATHS=1 apm install --target cursor,claude
```

期待結果:

- gitleaks、actionlint、ShellCheck、typos、mise.toml tool pin 検証が成功する
- APM の `skill` 同期（`apm install`）と監査が成功する
- このリポジトリでは組織共通の APM 監査ポリシーを使わないため、`--no-policy` を指定する
- 生成された `skill` ディレクトリは `skills/` の正本から再生成でき、Git 管理外のまま残る

## プルリクエストの期待値

- PR 本文は [`.github/pull_request_template.md`](.github/pull_request_template.md) に従う（詳細は [`rules/github-pr-workflow.md`](rules/github-pr-workflow.md)）
- なぜ変更が必要かを説明する
- 関連する仕様、判断記録、Issue があればリンクする
- 実行した検証コマンドを含める
- `skill` を利用する下流プロジェクトへの影響があるかを書く
- 機密情報、ローカル認証情報、`.env` ファイル、非公開プロジェクトのデータをコミットしない

## セキュリティ

脆弱性は `SECURITY.md` に従って報告してください。攻撃手順の詳細や機密情報を公開 Issue に書かないでください。
