# バージョン pin 方針

## 目的

mise 管理下の tool・ランタイム、Docker ベースイメージ、GitHub Actions のバージョンを可変参照のままにせず、再現可能な環境と CI を保つ。

## 背景

`latest` や major のみの指定は、取得タイミングで中身が変わり、ローカル / CI / メンバー間で差分が出る。AI エージェントが「とりあえず latest」を提案しやすいため、リポジトリ横断の禁止事項として明文化する。

## 対象と対象外

| 対象 | 対象外 |
| --- | --- |
| `mise.toml` `[tools]` の tool / ランタイム | lockfile で管理するアプリ依存（`package.json`、`go.mod` 等）の semver range |
| Docker ベースイメージ | npm backend（`npm:` prefix）で pin する npm パッケージ（`tools.md` 参照。本番では exact pin を推奨） |
| GitHub Actions `uses:` | — |

## 禁止

- `latest` / `@latest` / タグのみの可変参照（npm backend の運用例外は上表）
- major のみ pin（例: `node = "22"`、`go@1.22`）
- workflow や Dockerfile に tool バージョンを二重定義して `mise.toml` 等の SSOT からずらすこと

## 推奨

- tool・ランタイム・CLI・Docker イメージは **具体的なバージョンで pin** する
- mise 利用プロジェクトでは `mise.toml` `[tools]` を **完全一致 pin** する（詳細手順は [`skills/mise-guide/references/tools.md`](../skills/mise-guide/references/tools.md)）
- GitHub Actions の `uses:` は **full commit SHA pin** する（[`skills/mise-guide/references/ci.md`](../skills/mise-guide/references/ci.md)）
- ドキュメントに版や数値を書く場合は **時点**（例: 2026-07 時点）を併記する
- pin した版は定期的に更新する（例: `mise outdated`、Dependabot）

## 既知のギャップ

本リポジトリの `.github/workflows/ci.yml` は Actions をタグ pin（`@v6` / `@v4`）のままである。SHA pin への移行は別 PR で対応する。新規 workflow 追加時は最初から SHA pin とする。

## 例

### 悪い例

```toml
[tools]
node = "22"
"aqua:golangci/golangci-lint" = "latest"
```

```dockerfile
FROM node:latest
```

### 良い例

```toml
[tools]
node = "22.21.1"
"aqua:golangci/golangci-lint" = "2.12.2"
```

```dockerfile
FROM node:22.21.1-bookworm-slim
```

## 関連

- [`skills/mise-guide`](../skills/mise-guide/SKILL.md) — mise における pin と CI 識別子
- [`rules/document-consistency.md`](document-consistency.md) — コード変更とドキュメントの同期
