# Tool バージョン管理

入口: [SKILL.md](../SKILL.md)

## ワークフロー

### 1. 現状確認

変更前に、すでに何が設定されているか把握する:

```bash
mise ls                    # インストール済み tool と有効バージョン
mise config ls             # 読み込まれる config と優先順位
mise current               # 現在有効な tool バージョン
```

### 2. 検索・発見

```bash
mise search <query>        # 名前で tool を検索
mise ls-remote <tool>      # 利用可能バージョン一覧
mise latest <tool>         # 最新 stable
mise outdated              # アップデート可能な tool
```

### 3. インストールと pin（固定）

**プロジェクト `[tools]` では x.y.z 完全一致 pin のみ**（例: `22.15.0`）。`latest` / `lts` / `prefix:` / 2 セグメント以下は [rules/version-pinning.md](../../../rules/version-pinning.md) に従い禁止。**ネスト表 `[tools.*]` も `version = "x.y.z"` 必須**（flat `[tools]` への統一を推奨）。

**プロジェクト単位**（カレントの `./mise.toml` に書き込む）:

```bash
mise use --pin node@22.15.0        # install + x.y.z pin
mise use --pin python@3.12.7
mise use --pin node@22.15.0 go@1.22.5   # 複数同時
```

`[settings] pin = true` を `mise.toml` に置くと、`mise use` がデフォルトで `--pin` 相当になる（mise 公式 setting。環境変数は `MISE_PIN=1`）。

| コマンド | `pin = false`（既定） | `pin = true` |
| --- | --- | --- |
| `mise use node@22` | `node = "22"`（fuzzy） | `node = "22.15.0"`（exact） |
| 上書き | — | `mise use --fuzzy node@22` で fuzzy に戻せる |

**役割分担**: `pin = true` は `mise use` 経由の書き込みを exact にしやすくする補助。直接編集や既存 fuzzy 行は直さない。本体のガードは [check-tool-pins](#pin-検証check-tool-pins) と CI。

**グローバル**（`~/.config/mise/config.toml` に書き込む）:

```bash
mise use -g --pin node@22.15.0
mise use -g --pin python@3.12.7
```

### 4. バージョン指定子

mise CLI では fuzzy 指定子が使える。**プロジェクト `mise.toml` `[tools]` への書き込みでは x.y.z のみ**（下表の fuzzy 行は config 禁止）。

| 指定子 | 意味 | 例 | `[tools]` への書き込み |
| --- | --- | --- | --- |
| `22.1.0` | 完全一致 | `node@22.1.0` | 可 |
| `22.1` | minor 一致の最新 | `node@22.1` → 22.1.x | 不可 |
| `22` | major 一致の最新 | `node@22` → 22.x.x | 不可 |
| `latest` | 最新 stable | `node@latest` | 不可 |
| `lts` | 最新 LTS | `node@lts` | 不可 |
| `prefix:1.19` | prefix 一致 | `go@prefix:1.19` | 不可 |
| `sub-1:lts` | LTS の 1 つ前 | `node@sub-1:lts` | 不可 |

### 5. 複数バージョン

**プロジェクト `[tools]` では配列形式は使わない**（x.y.z 1 tool 1 バージョン）。mise 一般機能としての複数バージョン例:

先頭がデフォルト:

```toml
# 参考: 本 skill の x.y.z pin 方針では非推奨
[tools]
python = ["3.12.7", "3.11.9"]
```

### 6. その他のコマンド

```bash
mise install               # config 記載分を install（新規 pin はしない）
mise install node@22.15.0  # 一時 install（config には書かない）
mise uninstall node@22
mise unuse node
mise upgrade
mise prune
mise which node
mise where node@22
mise exec node@20 -- node -v  # 一時的に特定 tool 版で実行（下表参照）
mise shell node@20
mise reshim
```

### 7. config ファイル形式

```toml
# 例 A: 文字列指定（x.y.z）
[tools]
node = "22.15.0"
python = "3.12.7"
go = "1.22.5"

# 例 B: postinstall 付き（version は x.y.z）
[tools]
node = { version = "22.15.0", postinstall = "corepack enable" }

"npm:typescript" = "5.7.2"
"aqua:golangci/golangci-lint" = "2.12.2"
```

### 8. パッケージ backend（Package backend）

```bash
mise use --pin "npm:typescript@5.7.2"
mise use --pin "pipx:black@24.10.0"
mise use --pin "github:BurntSushi/ripgrep@14.1.1"
mise use --pin "aqua:golangci/golangci-lint@2.12.2"
```

### backend prefix = tool の識別子

`[tools]` で backend prefix 付きで宣言した場合、**キー文字列全体**が識別子になる。短縮名とは別の tool として扱われる。

```toml
[tools]
"aqua:golangci/golangci-lint" = "2.12.2"
```

- CI の `install_args`、`mise which`、shim 解決は同じ文字列を使う。
- `golangci-lint` だけ渡すと別 tool になり、`No version is set for shim: golangci-lint` で落ちる。
- **tool バージョンの正本は `mise.toml` `[tools]` のみ**。workflow にバージョン番号を書かない。

### pin 検証（check-tool-pins）

`[tools]` が x.y.z pin か機械検証する script:

```bash
bash scripts/check-tool-pins.sh                    # skill ルートから（[tools] を含む mise*.toml のみ。env-only は skip）
bash scripts/check-tool-pins.sh path/to/mise.toml  # 明示パス
bash scripts/run-check-tool-pins-tests.sh          # fixture 一括
```

利用先リポジトリ（twin-soul 等）では `mise.toml` task 経由を正本とする:

```bash
mise run ci:lint:mise-tools
```

CI 組み込み例:

```toml
[tasks."ci:lint:mise-tools"]
description = "mise.toml [tools] が x.y.z pin か検証する"
run = "bash skills/mise-guide/scripts/check-tool-pins.sh"
```

推奨 setting（補助。検証の代替ではない）:

```toml
[settings]
pin = true   # mise use 時に --pin をデフォルト化（--fuzzy で上書き可）
```

### `mise exec` の 2 用法（混同注意）

| 形式 | 用途 | 例 |
| --- | --- | --- |
| `mise exec <tool>@<ver> -- <cmd>` | 一時的に特定 tool 版で実行 | `mise exec node@20 -- node -v` |
| `mise exec -- <cmd>` | プロジェクト env（`mise.local.toml` 等）を載せて随時実行 | `mise exec -- gh issue list` |

`--` の有無で意味が変わる。git/gh 向けは [env.md](env.md) を参照。

## 言語別メモ

### Node.js

- `.nvmrc` / `.node-version`（`mise settings add idiomatic_version_file_enable_tools node`）
- デフォルト npm パッケージ: `~/.default-npm-packages`（非推奨。2026.11 から警告、2027.11 廃止予定。代替: `"npm:typescript" = "5.7.2"` のように npm バックエンド + x.y.z pin）
- corepack: `node.corepack = true`（設定）または `postinstall = "corepack enable"` — **postinstall に機密情報や未確認の `curl | sh` を書かない**

### Python

- 既定はコンパイル済みバイナリ（precompiled binary）
- venv 設定例（`[env]._.python.venv` を使う。旧 `[tools.python.virtualenv]` は廃止済み）:

  ```toml
  [tools]
  python = "3.12.7"

  [env]
  _.python.venv = { path = ".venv", create = true }
  ```

- uv プロジェクト（`uv.lock` あり）では `[settings] python.uv_venv_auto = "create|source"` を使う
- `mise settings python.compile=1` でソースからコンパイル

### Go

- Go ≤1.20 の取得は `mise use --pin go@1.20.7` 等で x.y.z を指定（`prefix:` は config 禁止）
- `.go-version` を読める

## トラブルシュート

```bash
mise doctor
mise config ls
mise settings ls
mise self-update
```
