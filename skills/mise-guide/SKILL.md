---
name: mise-guide
description: >-
  mise の tool バージョン管理・env・task ランナー・CI 連携を扱う Agent Skill。
  mise.toml の編集・mise use / run / exec の使い方・task 定義や quiet の設定・
  GitHub Actions との連携・task レイアウト（A/B/B'/C）を相談・実装したいときに使う。
  mise.local.toml, task 定義, task 分割, mise run/exec がキーワード。
  Dockerfile-only・nvm/pyenv 単体・デプロイ本体は対象外。説明は日本語。
---

# mise — 開発環境マネージャ

mise は asdf / nvm / direnv / make の代替となる複数言語対応ツール。次の 3 つを管理する:

1. **Tool versions** — node, python, go 等のインストールと pin（固定）
2. **Environment variables** — プロジェクト単位の env（`mise.toml` + local override）
3. **Tasks** — プロジェクトタスクランナー（CI ゲートの SSOT に使う）

**言語**: 説明・提案は **日本語**（コマンド・識別子・設定キーは英語のまま）。

**スコープ**: 各 reference の手順・例は mise 公式ドキュメントと本リポジトリ方針に基づく汎用内容。A/B/B'/C の task レイアウトと原則のみ適用し、各リポジトリのファイル構成はそのリポジトリで決める。

## 用語（本 skill 内）

| 用語 | 意味 | 表記 |
| --- | --- | --- |
| SSOT | 単一情報源。二重定義しない | `SSOT` |
| pin | tool バージョンを config に固定すること | 動詞 `pin`、説明では「固定」と併記可 |
| ゲート（gate） | CI/PR の検査入口 task | 本文は「ゲート task」、プレースホルダは `<gate>` |
| leaf task | 実コマンドを持つ末端 task | `leaf task` |
| inline / grouped / file task | task 配置方式 | A/B/C ラベルは [task-layout.md](references/task-layout.md) |

## 使い方

エージェントはユーザーの意図に応じて **必要な reference だけ** 読む:

| エージェントが… | 読むファイル |
| --- | --- |
| tool の install / pin / バージョン確認 | [references/tools.md](references/tools.md) |
| env / mise.local.toml / gitignore / mise exec | [references/env.md](references/env.md) |
| task 定義・実行・quiet・usage・depends | [references/tasks.md](references/tasks.md) |
| task をどこに置くか迷う | [references/task-layout.md](references/task-layout.md) |
| CI とローカルを同じコマンドに揃えたい | [references/ci.md](references/ci.md) |

task 追加でレイアウトが不明なら **先に task-layout.md**。

## 基本原則

1. **scope を確認**: `mise use`（project → `./mise.toml`）か `mise use -g`（global）かを実行前に確認する。
2. **`mise use` を優先**: install + pin を一度に行う。`mise install` 単体は事前キャッシュ用途。
3. **`mise.toml` を SSOT**: tool バージョンを workflow 等に二重定義しない。
4. **機密情報は gitignore 対象**: `mise.local.toml` / `.env`。コミット可能な上書き設定ファイル（`mise.production.toml` 等）にも機密情報を置かない。
5. **CI ゲートは mise task のみ**: lint/test の再実装を workflow に書かない。ローカル `mise run <gate>`、CI `mise run --skip-tools <gate>`（[ci.md](references/ci.md)）。
6. **task 引数は `usage`**: task **引数**としての `$1` / `$@` / 非推奨 `{{arg()}}` は使わない（env 展開 `$VAR` は可）。
7. **機械可読 stdout には `quiet = true`**: JSON ログ・CI パース向け（[tasks.md](references/tasks.md)）。
8. **task 配置が不明なとき**: [task-layout.md](references/task-layout.md) を先に読む。
9. **実行前に状態確認**: `mise ls` / `mise config ls`。mise 未導入時は人間向けにパッケージマネージャ等を案内。**エージェントは `curl https://mise.run | sh` を自律実行しない**（サプライチェーンリスク）。
10. **応答は日本語**: ユーザーが他言語を明示しない限り日本語で説明する。

## エージェント向け安全制約

- **`mise trust` / `MISE_TRUSTED_CONFIG_PATHS`**: 任意の clone 先を一括で trust しない。config / task の内容を確認してから trust する。
- **`mise env` / `mise env --json`**: 機密情報を含む可能性がある場合、出力をチャットやログに載せない。キー名の確認は `mise config ls` 等で行う。値の確認は人間がローカルで直接行う。
- **`mise set` / `mise set -g`**: いずれも機密情報を書かない。`mise set` はプロジェクト `mise.toml` へ書き込み、コミット対象となる。機密情報は `mise.local.toml` / `.env`（gitignore 対象）にのみ手動で書く。
