# mise と CI の連携

入口: [SKILL.md](../SKILL.md)

ローカル開発と GitHub Actions で **同じゲート task** を使う。workflow YAML に lint/test を再実装しない。

## 原則

1. **コマンドの SSOT**: ゲートを mise task に定義。ローカル `mise run <gate>`、CI `mise run --skip-tools <gate>`。
2. **tool バージョンの SSOT**: pin は `mise.toml` `[tools]` のみ。
3. **CI では必要 tool だけ install**: `mise-action` の `install_args`。
4. **二重 install 禁止**: action 後は `--skip-tools`。

## 最小 workflow テンプレ

**既存 workflow を改変するときは `@v4` のようなタグ指定に戻さず、コミット SHA による固定（full commit SHA pin）を維持する。**

```yaml
name: check

on:
  pull_request:
    paths:
      - "src/**"
      - "mise.toml"
      - ".mise/tasks/**"              # ゲート定義 + file task 変更
      - ".github/workflows/check.yaml"

permissions:
  contents: read

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<full-commit-sha>  # 本番は SHA pin
      - uses: jdx/mise-action@<full-commit-sha>
        with:
          install_args: "go aqua:golangci/golangci-lint"
      - run: mise run --skip-tools check
```

`<gate>` / `paths` / `install_args` はプロジェクトに合わせて置換。`<gate>` の例: `check`、`api-check`。

## install_args ルール

| ルール | 例 |
| --- | --- |
| `[tools]` キーと **完全一致** | `"aqua:golangci/golangci-lint"` |
| registry 短縮名と backend prefix 付きは **別 tool 識別子** | `golangci-lint` ≠ `aqua:golangci/golangci-lint` |
| ゲートが使う tool のみ | 未使用 tool は省く |
| バージョン番号を書かない | `mise.toml` から解決 |

典型エラー: `No version is set for shim: golangci-lint` — `install_args` が `[tools]` キーと **識別子不一致**（短名 vs `aqua:` prefix）。`mise.toml` のキー文字列をそのまま `install_args` に使う。詳細は [tools.md](tools.md) の「backend prefix = tool の識別子」節。

## `--skip-tools`

`--skip-tools` を指定すると、`mise run` 実行前の tool install をスキップする。`mise-action` で tool を install 済みの場合に指定し、二重 install を防ぐ。省略すると `mise.toml` 全 `[tools]` の install が走り CI が遅くなる。

フラグは **task 名の前**に置く:

```bash
mise run --skip-tools check   # 正しい
mise run check --skip-tools   # task の引数として透過され、意図しない動作になる
```

## workflow の `paths` フィルタ

次の変更で workflow を走らせる:

- 検査対象ソース
- `mise.toml`
- `.mise/tasks/**`（TOML 分割・file task 含む）
- workflow 自身（YAML 内ロジック変更時）

## ゲート task の設計

```toml
# .mise/tasks/check.toml
[check]
description = "PR check gate"
quiet = true
shell = "bash -c"
depends = ["lint", "test-unit"]
run = "echo 'all checks passed'"
```

## workflow YAML に残すもの（再実装禁止の境界）

| 残す | 理由 |
| --- | --- |
| checkout、permissions、matrix | CI インフラ |
| CI secrets / token スコープ | ローカルに無い認証情報 |
| PR コメント、成果物（artifact）、カバレッジ抽出 | ゲート task 外の責務 |
| 生成物 diff ガード（`gen-*` 再実行 + diff） | ゲート task 外で完結するパターン |

**ゲート本体**（lint / test / build / fmt）は必ず `mise run <gate>` 内。

## ローカル ↔ CI 整合チェックリスト

```bash
mise run <gate>                 # 初回は tool を自動インストール
mise run --skip-tools <gate>    # CI 相当
```

ツールの事前取得のみが目的なら `mise install`（バージョン固定を兼ねる `mise use` とは別）。

## よくある失敗

| 症状 | 想定原因 |
| --- | --- |
| `No version is set for shim: golangci-lint` | `install_args` が `[tools]` キーと識別子不一致（上記 install_args ルール参照） |
| `No version is set for shim: aqua:golangci/golangci-lint` | ローカル `[tools]` に短名のみ、CI は prefix 付き |
| CI で 10+ tool install | `--skip-tools` 欠落 |
| ローカル OK、CI で pipefail エラー | CI ゲート task に `shell = "bash -c"` なし |
| tool バージョン不一致 | workflow にバージョン直書き |
| task だけ変えた PR が CI 未実行 | `paths` が特定 `.toml` 固定で file task 漏れ |

## mise-action の pin

本番ではコミット SHA で固定する。例:

```yaml
- uses: actions/checkout@<full-commit-sha>   # v6 系など
- uses: jdx/mise-action@<full-commit-sha>    # v4 系など
```

テンプレの `<full-commit-sha>` は説明用プレースホルダ。既存 workflow を改変するとき `@v4` のようなタグに戻さない。
