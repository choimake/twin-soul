# Worktree ワークフロー

## 目的

git worktree を使った並列開発フローの推奨パターンを定める。使うかはプロジェクト次第。

## 背景

main ブランチ上で直接作業すると、調査中の変更と実装中の変更が混ざり、クリーンな状態を保てない。worktree を使えば main を司令塔（調査・plan 作成）として保ちつつ、変更作業を隔離できる。

## 基本ルール

worktree を採用する場合は、次のルールを守る。

- **worktree 推奨**: コード・インフラ・ドキュメントを問わず、変更作業は worktree で行う
- **1 worktree = 1 ブランチ = 1 PR**
- **main で直接変更しない**

## ディレクトリ配置

リポジトリ内の `.worktrees/` に配置する（`.gitignore` で除外する）。

```
.worktrees/
  wt-feat-add-auth/
  wt-docs-update-readme/
```

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
4. 全て pass した状態でユーザーに報告

### マージ後の片付け

```bash
cd <root-path>
git pull origin main
git worktree remove .worktrees/wt-<name>
git branch -d <scope>/<short-name>
git remote prune origin
```

PR merge とリモートブランチ削除は人間が確認して実行する。人間が `gh pr merge --delete-branch` を使う場合は、merge とリモートブランチ削除を同時に行える。

### 定期クリーンアップ

```bash
git worktree prune
git worktree list
```

## 並列作業の制約

- **並列上限**: 2 推奨。3 は関心事が完全分離している場合のみ
- **高リスクファイルの同時編集を避ける**: CI 設定、ルートの設定ファイル、共通ドキュメント等
- **マージ後**: 他の worktree で `git rebase origin/main` を実行して追従

## Hook による自動ブロック（任意）

main worktree 上の PR 対象ファイルへの直接編集を hook で自動ブロックすると効果的。許可パターン（worktree 内、作業領域）と禁止パターン（それ以外すべて）を定義する。

実装は各プロジェクトの環境・ツールに合わせる（例: Claude Code の PreToolUse hook、Git の pre-commit hook 等）。
