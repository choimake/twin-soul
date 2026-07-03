# バージョン pin 方針

## 目的

tool・依存・コンテナイメージのバージョンを可変参照のままにせず、再現可能な環境と CI を保つ。

## 背景

`latest` や major のみの指定は、取得タイミングで中身が変わり、ローカルと CI・メンバー間で差分が出る。AI エージェントが「とりあえず latest」を提案しやすいため、リポジトリ横断の禁止事項として明文化する。

## 禁止

- `latest` / `@latest` / タグのみの可変参照
- major のみ pin（例: `node = "22"`、`go@1.22`）
- workflow や Dockerfile に tool バージョンを二重定義し、`mise.toml` 等の SSOT とずらすこと

## 推奨

- tool・ランタイム・CLI・Docker イメージは **具体版で pin** する
- mise 利用プロジェクトでは `mise.toml` `[tools]` を **完全一致 pin** する（詳細手順は [`skills/mise-guide/references/tools.md`](../skills/mise-guide/references/tools.md)）
- GitHub Actions の `uses:` は **full commit SHA pin** する（[`skills/mise-guide/references/ci.md`](../skills/mise-guide/references/ci.md)）
- ドキュメントに版や数値を書く場合は **時点**（例: 2026-07 時点）を併記する

## 例

### 悪い例

```toml
[tools]
node = "22"
"golangci-lint" = "latest"
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

- [`skills/mise-guide`](../skills/mise-guide/SKILL.md) — mise における pin と CI identity
- [`rules/document-consistency.md`](document-consistency.md) — コード変更とドキュメントの同期
