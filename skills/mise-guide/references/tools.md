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

**プロジェクト単位**（カレントの `./mise.toml` に書き込む）:

```bash
mise use node@22           # node 22 を install + pin
mise use python@3.12
mise use node@22 go@1.22   # 複数同時
```

**グローバル**（`~/.config/mise/config.toml` に書き込む）:

```bash
mise use -g node@22
mise use -g python@3.12
```

### 4. バージョン指定子

| 指定子 | 意味 | 例 |
| --- | --- | --- |
| `22` | major 一致の最新 | `node@22` → 22.x.x |
| `22.1` | minor 一致の最新 | `node@22.1` → 22.1.x |
| `22.1.0` | 完全一致 | `node@22.1.0` |
| `latest` | 最新 stable | `node@latest` |
| `lts` | 最新 LTS | `node@lts` |
| `prefix:1.19` | prefix 一致 | `go@prefix:1.19` |
| `sub-1:lts` | LTS の 1 つ前 | `node@sub-1:lts` |

### 5. 複数バージョン

先頭がデフォルト:

```toml
# mise.toml
[tools]
python = ["3.12", "3.11"]
```

### 6. その他のコマンド

```bash
mise install               # config 記載分を install（pin しない）
mise install node@22
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
# 例 A: 文字列指定（いずれか一方の書き方）
[tools]
node = "22"
python = "3.12"
go = "1.22"

# 例 B: postinstall 付き（例 A と同じキーを重複定義しない）
[tools]
node = { version = "22", postinstall = "corepack enable" }

"npm:typescript" = "latest"
"aqua:golangci/golangci-lint" = "2.12.2"
```

### 8. パッケージ backend（Package backend）

```bash
mise use "npm:typescript"
mise use "pipx:black"
mise use "github:BurntSushi/ripgrep"
mise use "aqua:golangci/golangci-lint"
```

### backend prefix = tool の識別子

`[tools]` で backend prefix 付きで宣言した場合、**キー文字列全体**が識別子になる。短縮名とは別の tool として扱われる。

```toml
[tools]
"aqua:golangci/golangci-lint" = "2.12.2"
```

- CI の `install_args`、`mise which`、shim 解決は同じ文字列を使う。
- `golangci-lint` だけ渡すと別 tool になり、`No version is set for shim: golangci-lint` で落ちる。
- **tool バージョンの SSOT は `mise.toml` `[tools]` のみ**。workflow にバージョン番号を書かない。

### `mise exec` の 2 用法（混同注意）

| 形式 | 用途 | 例 |
| --- | --- | --- |
| `mise exec <tool>@<ver> -- <cmd>` | 一時的に特定 tool 版で実行 | `mise exec node@20 -- node -v` |
| `mise exec -- <cmd>` | プロジェクト env（`mise.local.toml` 等）を載せて随時実行 | `mise exec -- gh issue list` |

`--` の有無で意味が変わる。git/gh 向けは [env.md](env.md) を参照。

## 言語別メモ

### Node.js

- `.nvmrc` / `.node-version`（`mise settings add idiomatic_version_file_enable_tools node`）
- デフォルト npm パッケージ: `~/.default-npm-packages`（非推奨。2026.11 から警告、2027.11 廃止予定。代替: `"npm:typescript" = "latest"` のように npm バックエンドを使う）
- corepack: `node.corepack = true`（設定）または `postinstall = "corepack enable"` — **postinstall に機密情報や未確認の `curl | sh` を書かない**

### Python

- 既定はコンパイル済みバイナリ（precompiled binary）
- venv 設定例（`[env]._.python.venv` を使う。旧 `[tools.python.virtualenv]` は廃止済み）:

  ```toml
  [tools]
  python = "3.12"

  [env]
  _.python.venv = { path = ".venv", create = true }
  ```

- uv プロジェクト（`uv.lock` あり）では `[settings] python.uv_venv_auto = "create|source"` を使う
- `mise settings python.compile=1` でソースからコンパイル

### Go

- Go ≤1.20 は `go@prefix:1.20`
- `.go-version` を読める

## トラブルシュート

```bash
mise doctor
mise config ls
mise settings ls
mise self-update
```
