# custom 手書きルール

template がない tool は、`gitignore.io` の候補とは別に custom 手書きルールとして足す。繰り返し使う block は `assets/` に置き、`draft` や `write-file` ではそこを起点にする。

## `mise`

`mise.toml` や `mise.<env>.toml` は共有設定として commit 対象に残す。ignore したいのは local override 系である。

推奨ルールは [../assets/mise-local-overrides.gitignore](../assets/mise-local-overrides.gitignore) を使う。

意図:

- `mise.toml` は project 設定なので ignore しない
- `mise.<env>.toml` も共有したい環境設定なら ignore しない
- `mise.local.toml` と `mise.<env>.local.toml` はローカル専用なので ignore する
- `.mise.*` 系は標準運用としては広げず、必要なリポジトリでだけ個別に足す

skill が `mise` を扱うときは、`gitignore.io` の本文に後付けの custom block として足す。

## `memory`

エージェント作業のローカル記録は共有の source of truth ではない。ディレクトリごと ignore する。

推奨ルールは [../assets/memory.gitignore](../assets/memory.gitignore) を使う。

意図:

- `memory/` 配下の学び・申し送り・作業メモはローカル専用なので ignore する
- `.gitkeep` は置かない。クローン後は手順で再作成する
- Claude Code Auto Memory（`~/.claude/projects/.../memory/`）とは別物として扱う

skill がエージェント作業領域を扱うときは、`gitignore.io` の本文に後付けの custom block として足す。

## `worktrees`

変更作業用の git worktree は共有の source of truth ではない。ディレクトリごと ignore する。

推奨ルールは [../assets/worktrees.gitignore](../assets/worktrees.gitignore) を使う。

意図:

- `.worktrees/` 配下はローカルの隔離 checkout なので ignore する
- Cursor 標準の `~/.cursor/worktrees` とは別物として扱う
- 手順の正は `rules/worktree-workflow.md` に置く

skill がエージェント作業領域を扱うときは、`gitignore.io` の本文に後付けの custom block として足す。
