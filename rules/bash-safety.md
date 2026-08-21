# Bash コマンド安全性の判断基準

## 目的

Bash ツールで実行するコマンドを安全性でカテゴリ分けし、判断基準を明確にする。実際の強制は各プロジェクトで hooks 等を使う。

## 背景

AI エージェントがシェルコマンドを実行する際、復旧困難な操作やセキュリティリスクのある操作を誤って実行するリスクがある。4 段階の分類で判断基準を共有し、プロジェクトごとの hooks や permissions で強制する土台にする。

## 安全な読み取り専用操作（常に許可）

システム状態を変更しないため、安全に実行可能。

### ファイルシステム

```bash
ls, tree, pwd, which, type
```

### Git（読み取り）

```bash
git status, git log, git diff, git show, git branch, git remote -v
```

### GitHub CLI（読み取り）

```bash
gh pr list, gh pr view, gh issue list, gh issue view, gh repo view
```

## 確認が必要な操作

実行前にユーザー確認を推奨。可逆性が低い、または外部に影響を与えるため。

### Git（書き込み）

```bash
git commit, git push, git push origin <branch>
```

### GitHub CLI（書き込み）

```bash
gh pr create, gh pr merge, gh issue create, gh issue close
```

Agent が読めるローカル shell に GitHub write token を置いて実行する運用は標準案内しない。Issue / PR 本文やコメントの下書きは Agent が作成してよいが、GitHub write は人間が確認して実行するか、GitHub Actions / GitHub App / executor などの分離された仕組みで扱う。

判断理由は `decisions/0007-withdraw-local-gh-agent-write.md` を参照する。

### パッケージ管理

```bash
mise install, mise run ci:apm, pipx install, apm install
```

### Docker

```bash
docker build, docker run, docker push, docker rm
```

## 禁止されている操作

復旧困難、セキュリティリスクがあるため実行禁止。

### 破壊的操作

```bash
git reset --hard           # 作業を失う危険
git clean -fd              # 未追跡ファイル削除
rm -rf /                   # システム破壊
```

### 危険な Git 操作

```bash
git push --force main      # main ブランチの強制プッシュ
git push --force master    # master ブランチの強制プッシュ
```

### 秘密情報の漏洩

```bash
echo "SECRET=..." > .env   # 秘密の書き込み
cat .env                   # 秘密の表示
```

### セキュリティリスク

```bash
chmod -R 777               # 過剰な権限付与
```

### 外部通信（プロジェクトの deny パターンで制限を推奨）

```bash
curl, wget
```

## 条件付き許可

条件を満たす場合のみ許可。

### rm -rf

- **許可**: 作業ディレクトリが明確（一時ディレクトリ等）で、Git 未追跡ファイルのみが対象
- **禁止**: ルートディレクトリでの実行、Git 追跡ファイルの削除

### git push --force

- **許可**: 対象がフィーチャーブランチ（main/master 以外）で、ユーザーが明示的に承認
- **禁止**: main / master ブランチ、他の人が使用中のブランチ

### git rebase -i

- **Agent 実行は禁止**: 対話入力が必要で、途中状態の把握や復旧が難しい
- **人間の手動実行のみ許可**: ローカルコミットのみ（未プッシュ）で、フィーチャーブランチ上
- **禁止**: 公開済みコミット（プッシュ済み）、main / master ブランチ

## 推奨ツール

Bash の代わりに専用ツールを優先する。ユーザーが作業をレビューしやすくなる。

- **Grep** — `grep` や `rg` の代わりに
- **Glob** — `find` や `ls` の代わりに
- **Read** — `cat`, `head`, `tail` の代わりに
- **Edit** — `sed` や `awk` の代わりに
- **Write** — `echo >` や `cat <<EOF` の代わりに

## エラー時の対応

1. **deny パターンによるブロック**: プロジェクトの permissions 設定を確認
2. **手動実行の提案**: ユーザーに手動実行を提案
3. **代替手段の検討**: より安全な方法がないか検討
