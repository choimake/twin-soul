# Task レイアウト — どこに置くか

入口: [SKILL.md](../SKILL.md)

よく混同される 4 方式（A / B / B' / C）。1 プロジェクト内で共存できるが、**`task_config.includes` のセマンティクス**に注意。

他 reference では **B = grouped TOML**、**B' = TOML 1 ファイル 1 task**、**C = 実行可能スクリプト形式** と呼ぶ。

## 早見表

| 方式 | 物理形 | 1 task = 1 file? | 向いている場面 |
| --- | --- | --- | --- |
| **A. Inline** | ルート `mise.toml` の `[tasks.x]` | No | 少数（≤5）、試作 |
| **B. Grouped TOML** | `.mise/tasks/check.toml` に複数 task セクション（例: `[lint-all]`） | No | ドメイン単位、コメント共有 |
| **B'. Split TOML** | `.mise/tasks/lint-all.toml` に `[lint-all]` のみ | Yes（TOML） | TOML のまま task を増やす |
| **C. File task** | `.mise/tasks/lint-all` 実行可能スクリプト | Yes（スクリプト） | 長い bash、複雑な分岐 |

**「1 task 1 file」** は多く **C** を指す。B' は「TOML 1 ファイル 1 task」で別概念。

## `includes` の重要な挙動（必須の知識）

`task_config.includes` を設定すると、**既定の file task 探索ディレクトリは置き換わる**（追加ではない）。

- 既定: `.mise/tasks/` 等の実行可能ファイルが自動検出される
- `includes = [".mise/tasks/*.toml"]` のみ → **`.toml` だけ**が対象。実行可能ファイルは **検出されない**

file task（C）を使う場合は対象ディレクトリを **明示列挙**する:

```toml
[task_config]
includes = [
  ".mise/tasks/*.toml",
  ".mise/tasks",   # file task を使う場合のみ
]
```

出典: [mise task configuration — task_config.includes](https://mise.jdx.dev/tasks/task-configuration.html)（2026-06-28 確認）

## 決定フロー

```
新しい task が必要？
│
├─ run が 1 行？
│   └─ A または B（grouped TOML）
│
├─ task は多いが TOML 宣言のまま？
│   └─ B'（1 TOML 1 task）
│
└─ 長い bash / 複雑な分岐？
    └─ C — ただし includes に directory 明示が前提
```

**行数だけでは移行理由にならない。** 長い run script を grouped TOML のまま維持してもよい。

## A. Inline（ルート mise.toml）

```toml
[tasks.dev]
description = "Start dev server"
run = "pnpm dev"
```

小規模の間だけ。肥大化前に `.mise/tasks/` へ移す。

## B. Grouped TOML

```toml
# mise.toml
[task_config]
includes = [".mise/tasks/*.toml"]
```

```toml
# .mise/tasks/check.toml
[lint-all]
description = "Lint"
quiet = true
run = "pnpm lint"

[typecheck]
description = "Typecheck"
quiet = true
run = "pnpm typecheck"

[check]
description = "CI gate"
quiet = true
depends = ["lint-all", "typecheck"]
run = "echo 'ok'"
```

- **利点**: 関連 task を同ファイルにまとめられる。ドメイン説明をファイル先頭コメントに書ける。
- **欠点**: ファイルが肥大化する。「1 task 1 file」ではない。

命名: ドメイン prefix（`tf-plan`、`app-tf-plan`）で衝突を避ける。

## B'. TOML 1 ファイル 1 task

```
.mise/tasks/
├── lint-all.toml
├── typecheck.toml
└── check.toml
```

- **利点**: diff が小さい。task 単位の所有が明確。
- **欠点**: ファイル数が増える。

## C. 実行可能スクリプト形式（File task）

```
.mise/tasks/
├── lint-all      # chmod +x
└── check
```

- **利点**: 通常のスクリプト編集。TOML の複数行エスケープが不要。
- **欠点**: `chmod +x` が必須。`includes` にディレクトリの明示列挙が必要。

### B と C の混在（Grouped TOML と実行可能スクリプト）

```toml
[task_config]
includes = [
  ".mise/tasks/*.toml",
  ".mise/tasks",
]
```

**同名 task を TOML と file の両方に置かない。** 変更後は `mise tasks ls` で確認。

## 長い TOML の run を実行可能スクリプトへ移行（任意）

実施する場合:

1. `includes` に `.mise/tasks` ディレクトリを追加
2. `.mise/tasks/<name>` にシバン行付きのスクリプトを作成
3. TOML 側 `[<name>]` を削除
4. `chmod +x` → `mise tasks info <name>` で確認

## やってはいけないこと

- commit する task の `run` や `env` ブロックに secrets を埋め込まない（SSOT 違反かつ漏洩リスク）
- workflow YAML と task の両方に同じ lint/test を書かない（[ci.md](ci.md)）
- includes 先に `[tasks.xxx]` と書く（動かない）
- `includes` を設定しているのに「実行可能ファイルも自動検出される」と想定する
