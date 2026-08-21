# Worktree ワークフロー

## 目的

変更作業を main checkout から隔離し、調査・plan と実装を混ぜない。

## 背景

main ブランチ上で直接作業すると、調査中の変更と実装中の変更が混ざり、クリーンな状態を保てない。worktree を使えば main を司令塔（調査・plan 作成）として保ちつつ、変更作業を隔離できる。

ドキュメントだけの推奨では読まれず破られる。twin-soul では hook で、許可か拒否かではっきり分かれる禁止を止める。

## 基本ルール

twin-soul では必須。

- コード・インフラ・ドキュメントを問わず、変更作業は `.worktrees/` の git worktree で進める
- **1 worktree = 1 ブランチ = 1 PR**
- **main checkout では編集しない**

main でよいもの:

- 調査と読み取り
- plan 作成（`.cursor/plans/`）
- `memory/` への作業記録
- `git worktree add|list|prune|remove`

## ディレクトリ配置

リポジトリ内の `.worktrees/` に置く（`.gitignore` で除外する）。

```
.worktrees/
  wt-feat-add-auth/
  wt-docs-update-readme/
```

Cursor 標準の `/worktree`（`~/.cursor/worktrees`）は正本にしない。配置先が違い、Cursor の自動 cleanup 対象にもなり得る。隔離だけなら使ってよいが、このリポジトリの正本は `.worktrees/` である。

## ブランチ命名

```
<scope>/<short-name>
```

| scope      | 用途             |
| ---------- | ---------------- |
| `feat`     | 新機能           |
| `fix`      | バグ修正         |
| `docs`     | ドキュメント     |
| `bump`     | バージョン更新   |
| `refactor` | リファクタリング |

`short-name` はケバブケース、3-5 語。

## 手順

### 作成

```bash
git worktree add .worktrees/wt-<name> -b <scope>/<short-name>
```

### PR 作成準備

```bash
cd .worktrees/wt-<name>
git add <files>
git commit -m "<scope>: 説明"
git push -u origin <scope>/<short-name>
```

Agent は PR title / description の下書きまでを作成する。PR 作成そのものは、人間が確認して実行するか、GitHub Actions / GitHub App / executor などの分離された仕組みで扱う。

### PR 作成後の CI 確認（必須）

PR 作成後、CI が通ることを確認してから報告する。

1. `gh run watch --exit-status` で CI 完了を待つ
2. CI が失敗した場合:
   - `gh run view --log-failed` でログを確認し原因を特定
   - 修正コミットを push
   - 再度 `gh run watch --exit-status` で確認
   - **最大 3 回**まで修正ループを繰り返す
3. 3 回修正しても解決しない場合はユーザーに報告して判断を仰ぐ
4. すべて合格した状態でユーザーに報告

### マージ後の片付け

```bash
cd <root-path>
git pull origin main
git worktree remove .worktrees/wt-<name>
git branch -d <scope>/<short-name>
git remote prune origin
```

PR merge とリモートブランチ削除は人間が確認して実行する。人間が `gh pr merge --delete-branch` を使う場合は、merge とリモートブランチ削除を同時にできる。

### 定期クリーンアップ

```bash
git worktree prune
git worktree list
```

## 並列作業の制約

- **並列上限**: 2 を推奨。3 は関心事が完全分離している場合のみ
- **高リスクファイルの同時編集を避ける**: CI 設定、ルートの設定ファイル、共通ドキュメント等
- **マージ後**: 他の worktree で `git rebase origin/main` を実行して追従

## Hook

twin-soul では必須。判定の正本は [../scripts/hooks/guard-main-checkout.py](../scripts/hooks/guard-main-checkout.py)。

入口:

- Cursor: [../.cursor/hooks.json](../.cursor/hooks.json) の `preToolUse` と `beforeShellExecution`
- Claude Code: [../.claude/settings.json](../.claude/settings.json) の `PreToolUse`
- Codex: [../.codex/hooks.json](../.codex/hooks.json) の `PreToolUse`（`apply_patch` と `Bash`）

拒否するもの:

- main checkout 上の、許可リスト外ファイルへの Write / StrReplace / Delete（Claude 側は Edit / Write / MultiEdit）
- main 上の `git add` / `commit` / `push` / `rebase` / `merge`
- worktree セッションから親 checkout への漏れ書き

許可するもの:

- `memory/`、`.cursor/plans/`、`.worktrees/` 配下
- 読み取り専用 git と `git worktree add|list|prune|remove`
- worktree 内での編集と git 書き込み

hook が壊れたとき、または `python3` が無いときは fail-open（許可して警告）する。作業を止めないため。

他の rule を hook に足すのは、例外がなく、許可か拒否かではっきり分かれ、ツール入力だけで判定でき、ドキュメントにしたあと繰り返して破られたときだけ。判断が要る本文は索引と `rules/` に残す。

ローカル Cursor CLI（`agent -p`）は IDE より hook が狭い。`beforeShellExecution` は確認済みの前提。`preToolUse` が飛ばない場合、Write 拒否は IDE 側で効く。判定ロジック自体は `python3 scripts/hooks/guard-main-checkout.py --self-test` で確認する。

## 残リスク

- `cat > file` や `tee` など、shell 経由のファイル書き込みは file hook を迂回する
- Cursor 標準 worktree の自動 cleanup は manager 外の worktree も対象になり得る。`.worktrees/` を `~/.cursor/worktrees` と混ぜない

## ローカル確認

```bash
python3 scripts/hooks/guard-main-checkout.py --self-test
bash scripts/hooks/smoke-hook-stdin.sh
bash scripts/hooks/smoke-codex-cli.sh
bash scripts/hooks/smoke-cursor-cli.sh
```

`smoke-hook-stdin.sh` は Cursor と同じ JSON を hook に流して deny/allow を見る。認証は不要。

`smoke-codex-cli.sh` は `mktemp` した使い捨て repo で `codex exec` を回す。`codex login` が要る。CI には入れない。

`smoke-cursor-cli.sh` は同じく使い捨て repo で `agent -p` を回す。`agent login` または `CURSOR_API_KEY` が要る。CI には入れない。
