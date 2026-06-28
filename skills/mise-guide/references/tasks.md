# Task ランナー

入口: [SKILL.md](../SKILL.md)

mise には make / npm scripts の代替となる task ランナーが組み込まれている。

**配置が不明なら** 先に [task-layout.md](task-layout.md)（A/B/B'/C）を読む。

## task キー記法（最重要）

| 置き場所 | 正しい記法 | 誤り |
| --- | --- | --- |
| ルート `mise.toml`（inline） | `[tasks.build]` | `[build]` |
| `.mise/tasks/*.toml`（includes 先） | `[api-check]` | `[tasks.api-check]` |

includes 先 TOML は `[tasks.]` プレフィックス **禁止**。mise 公式: included ファイルは `[tasks]` セクション相当のフラット形式。

## task の定義

### ルート mise.toml に inline

```toml
# ルート mise.toml（inline）— [tasks.] プレフィックス必須
[tasks.build]
run = "npm run build"
description = "Build the project"

[tasks.dev]
run = "npm run dev"
depends = ["build"]
description = "Start dev server"
```

### includes で TOML を分割

```toml
# ルート mise.toml
[task_config]
includes = [".mise/tasks/*.toml"]
```

```toml
# .mise/tasks/check.toml（includes 先）— [tasks.] なし
[lint-all]
description = "Run all linters"
quiet = true
run = "npm run lint"
```

### task オプション（ルート mise.toml / inline の例）

```toml
# ルート mise.toml（inline）— includes 先は [tasks.] プレフィックス禁止（上表参照）
[tasks.deploy]
run = "deploy.sh"
description = "Deploy to production"
depends = ["build", "test"]       # 先に実行。depends には env は渡らない（下記 footgun）
env = { NODE_ENV = "production" } # この task の run のみ。子 depends には継承されない
dir = "{{cwd}}"
sources = ["src/**/*"]
outputs = ["dist/**/*"]
quiet = false
shell = "bash -c"                 # CI ゲート task に限定（下記）
```

### depends と env の落とし穴

```toml
# .mise/tasks/footgun.toml（includes 先）— 親の env は子に継承されない
[parent]
env = { PROJECT_ID = "x" }
depends = ["child"]
run = "echo ok"

[child]
run = 'echo "$PROJECT_ID"'   # 空 — parent の env は継承されない
```

子 task が env を必要とする場合は `mise.local.toml`、共有 `[env]`、または structured `depends` の `env` キーで明示する。

```toml
# structured depends で env を明示する例
[parent]
depends = [{ task = "child", env = { PROJECT_ID = "x" } }]
run = "echo ok"
```

### file task（実行可能スクリプト形式）

```bash
#!/usr/bin/env bash
#MISE description="Build the project"
#MISE depends=["lint"]
#MISE quiet=true

set -euo pipefail
npm run build
```

`chmod +x` 必須。`task_config.includes` を設定している場合は file task のディレクトリを **明示列挙** しないと検出されない（[task-layout.md](task-layout.md)）。

## task の実行

```bash
mise run build
mise run build test
mise tasks ls
mise tasks info build
```

## task 引数（`usage` フィールド）

task **引数**としての `$1` / `$@` / 非推奨 `{{arg()}}` は使わない。env 展開 `$VAR` / `${VAR:?}` は可。

```toml
# includes 先の例
[deploy]
description = "Deploy to environment"
usage = '''
arg "<env>" help="Target environment" {
  choices "dev" "staging" "prod"
}
'''
run = '''
set -euo pipefail
./scripts/deploy.sh "${usage_env?}"
'''
```

## `quiet = true`

mise ラッパー echo（`[task] $ ...` 行）を抑止する。**`run` 内の `echo` はそのまま出る。**

| 場面 | quiet |
| --- | --- |
| CI ゲート、stdout パース task | `true` 推奨 |
| dev / 対話 task | 任意 |

CI デバッグ: 失敗時は exit code / stderr は残る。足りなければ一時的に `quiet` を外すか task を分割する。

## 集約 / ゲート task

```toml
# .mise/tasks/check.toml
[lint-fast]
description = "Fast lint"
quiet = true
run = "ruff check ."

[test-unit]
description = "Unit tests"
quiet = true
run = "pytest -m 'not integration'"

[check]
description = "CI gate"
quiet = true
depends = ["lint-fast", "test-unit"]
run = "echo 'all checks passed'"
```

leaf task（末端 task）にコマンド本体を置き、ゲート task は薄く保つ。ローカル `mise run check`、CI `mise run --skip-tools check`（[ci.md](ci.md)）。

## CI 向け shell 設定（CI ゲート task に限定）

GitHub Actions `ubuntu-latest` の `/bin/sh` は `dash` で `pipefail` が無い。**CI ゲート task**（`.mise/tasks/check.toml` 系）でのみ:

```toml
# .mise/tasks/check.toml（includes 先）
[api-check]
description = "Static analysis + tests"
quiet = true
shell = "bash -c"
run = """
set -euo pipefail
cd api
diff=$(gofmt -l .)
if [ -n "$diff" ]; then echo "$diff"; exit 1; fi
go test ./...
"""
```

ローカル専用 task（deploy / e2e 等）で macOS 既定 `sh` のまま動作するなら `shell` は省略してよい。bash 固有の記法を使う場合は CI ゲート task 側に寄せる。

## `$MISE_PROJECT_ROOT`

`dir` で cwd を移す task ではリポジトリルート相対に `$MISE_PROJECT_ROOT` を使う:

```toml
[gen-docs]
description = "Generate docs from tests"
quiet = true
dir = "packages/lib"
run = 'python3 -m pytest . --collect-only --out="$MISE_PROJECT_ROOT/docs/generated.md"'
```

## 必須 env ガード

```toml
run = """
: "${PROJECT_ID:?PROJECT_ID が未設定 — mise.local.toml [env] に設定してください}"
gcloud config set project "$PROJECT_ID"
"""
```

## ベストプラクティス

1. **`depends`** で順序を表現する。
2. **`sources` / `outputs`** で build 系を cache 可能にする。
3. **長いスクリプトは file task**（includes でディレクトリ明示が前提）。
4. **全 task に `description`** を付ける。
5. **引数は `usage`**（task 引数の `$1` / `$@` 禁止）。
6. **CI ゲートと機械可読出力に `quiet = true`**。
7. **`shell = "bash -c"`** は CI ゲート task に限定。
8. **`raw = true`** は stdin が要る対話 task のみ。
