# 環境変数管理

入口: [SKILL.md](../SKILL.md)

mise はプロジェクト単位の環境変数を管理できる（direnv の代替）。

## 設定のレイヤー（重ね合わせ）

**チーム共有**と**個人・秘密**を分ける:

| ファイル | commit | 典型的な内容 |
| --- | --- | --- |
| `mise.toml` | Yes | `[tools]`、`[task_config]`、非秘密の `[env]` |
| `mise.local.toml` | No | 個人の上書き設定、機密情報（公式サポートのファイル名） |
| `.env` | No | dotenv（`[env]._.file` で読み込み） |
| `mise.development.toml` 等 | Yes（任意） | 非機密の上書き設定（`MISE_ENV=development`） |

原則:

- **code / config 分離**: 開発者・マシンごとに異なる値は gitignore 対象へ。
- **`mise.toml` が SSOT**: tool バージョンとチーム共有 env のデフォルト。
- **コミット可能な上書き設定ファイルにも機密情報を置かない**（`mise.production.toml` 等）。本番の機密情報は Secret Manager / CI secrets のみ。
- **ローカル開発の機密情報は `mise.local.toml` / `.env`**（gitignore 対象）のみ。`mise.toml` には置かない。
- プレースホルダであっても機密情報を `mise.toml` にコミットしない。

### gitignore テンプレ

```gitignore
mise.local.toml
.env
.env.local
```

## 環境変数の設定

### mise.toml（共有）

```toml
# mise.toml
[env]
NODE_ENV = "development"
LOG_LEVEL = "info"
```

### mise.local.toml（個人・秘密）

```toml
# mise.local.toml — gitignore 対象
[env]
GITHUB_TOKEN = "<your-token>"   # 例。実際の値はコミットしない
PROJECT_ID = "my-dev-project"
```

必須キーは README / runbook に列挙し、値は書かない。**`mise set -g` で機密情報をグローバル config に書かない。**

### .env から読み込む

```toml
# 単一ファイル
[env]
_.file = ".env"

# または複数（後勝ち）
[env]
_.file = [".env", ".env.local"]
```

### PATH 操作

```toml
[env]
_.path = ["./bin", "./node_modules/.bin"]
```

### 条件・計算値

```toml
[env]
PROJECT_ROOT = "{{cwd}}"
LOG_DIR = "{{env.PROJECT_ROOT}}/logs"
```

### 環境別 config

```
mise.toml
mise.development.toml
mise.production.toml
mise.local.toml            # gitignore
```

```bash
MISE_ENV=development mise ...
mise -E development ...
```

## `mise exec --`（プロジェクト env を随時コマンドに載せる）

`mise run` は **定義済み task** 向け。`gh` や `git push` などで `mise.local.toml` の機密情報が必要なら:

```bash
mise exec -- gh issue list --limit 50
mise exec -- git pull origin main --ff-only
```

`git` / `gh` などに `mise.local.toml` の機密情報を注入したい場合は `mise exec --` を前置する。利用先リポジトリの方針に従うこと。

## 便利なコマンド

```bash
mise env
mise env --json            # 機密情報含有時はエージェント出力に使わない
mise set KEY=VALUE         # プロジェクト mise.toml（コミット対象 — 機密情報禁止）
mise set -g KEY=VALUE      # グローバル（機密情報禁止）
mise unset KEY
mise config ls
```

## セキュリティ

- 新規 config から env を読む前に `mise trust` が必要な場合がある。**trust 前に config / task の内容を確認する。**
- `MISE_TRUSTED_CONFIG_PATHS` は信頼済み・固定パスのみ。任意の clone 先を一括で自動 trust しない。
- `mise.local.toml` / `.env` は gitignore 対象にする。

## ベストプラクティス

1. 非機密の環境変数は `mise.toml` をコミットして共有する。
2. 機密情報は `mise.local.toml` / `.env` のみに書く。
3. `_.file = ".env"` で dotenv ファイルをまとめて読み込める。
4. 環境別ファイルで分岐ロジックを避ける（上書き設定ファイルに機密情報を載せない）。
5. 必須の環境変数キーは README に列挙し、値は書かない。
