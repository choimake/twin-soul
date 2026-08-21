# 変更作業は `.worktrees/` の git worktree で行い、許可か拒否かではっきり分かれる禁止は hook で強制する

## ステータス

採用済み (2026-08-21)

## 背景

[rules/worktree-workflow.md](../rules/worktree-workflow.md) は worktree 隔離を書いていたが、「使うかはプロジェクト次第」で任意だった。`rules/` は正本だが実行環境に自動注入されないため、エージェントが読まず main checkout で編集する例が多かった。

候補は次だった。

- Cursor 標準の `/worktree` と `.cursor/worktrees.json`（配置は通常 `~/.cursor/worktrees`）
- 既存方針どおりリポジトリ内 `.worktrees/` + `git worktree add`
- `.cursor/rules/` を再導入して本文を always-on 注入する
- 文書と skill だけ足して強制はしない

## 判断

twin-soul の変更作業は `.worktrees/` の git worktree で行う。

- Cursor と Claude Code で同じ手順にするため、製品固有の `/worktree` は本経にしない
- 許可か拒否かではっきり分かれる禁止（main で編集しない、main で `git add` / `commit` / `push` しない）は hook で止める
- どの rule を読むかは [AGENTS.md](../AGENTS.md) の短い索引だけにする。本文は `rules/` に残す
- [0005-rules-and-specs-boundaries.md](0005-rules-and-specs-boundaries.md) は維持する。`.cursor/rules/` と `.claude/rules/` は再導入しない
- worktree 用 skill は作らない。利用先リポジトリへはこの運用を自動展開しない
- hook に移すのは、許可か拒否かではっきり分かれる禁止だけ。判断が要る rule 本文は移さない。同じ破れが繰り返されたら、次の同じ種類の禁止を検討する

hook の入口は Cursor が `.cursor/hooks.json`、Claude Code が `.claude/settings.json`、Codex が `.codex/hooks.json`。判定は `scripts/hooks/guard-main-checkout.py` に一本化する。Codex のファイル編集は `apply_patch` なので、パッチ本文から対象パスを読む。

## 影響

メリット:

- main checkout を調査と plan の司令塔として保てる
- 破られやすい禁止を、プロンプトではなく実行時に止められる
- rule 本文の正本が割れない

デメリット:

- hook 破損や `python3` 未導入時は fail-open なので、止めきれない
- ローカル Cursor CLI は `preToolUse` を飛ばすことがあり、Write 拒否は IDE 側が本経になる
- shell のリダイレクト書き込みは file hook を迂回する

影響:

- `.worktrees/` は gitignore する
- 許可リストは `memory/`、`.cursor/plans/`、`.worktrees/` 配下
- Cursor 標準 worktree の自動 cleanup と混ぜない

## 関連する DR

- 関連: [0005-rules-and-specs-boundaries.md](0005-rules-and-specs-boundaries.md)
- 関連: [0009-use-memory-for-local-working-notes.md](0009-use-memory-for-local-working-notes.md)
