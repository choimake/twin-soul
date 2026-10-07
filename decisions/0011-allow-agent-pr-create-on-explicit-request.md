# ユーザーが PR 作成を明示したときは、エージェントが `gh pr create` まで実行する

## ステータス

採用済み (2026-10-07)

## 背景

`decisions/0007-withdraw-local-gh-agent-write.md` では、エージェントが読めるシェルに GitHub 書き込み用トークンを置く運用を撤回した。PR 作成を含む GitHub 書き込みは、人間が実行するか、分離された仕組みで扱うことにした。

実際の運用では、作業者が「PR を出して」と指示し、エージェントが push のあと `gh pr create` まで実行していた。rule は「PR 作成は人間」のままで、指示と rule が食い違っていた。

PR 作成は、push 済みのブランチに説明を付けるだけの操作で、閉じれば取り消せる。push は rule で毎回確認を取っている。ここで人間に手作業を戻しても、確認の段階は増えない。

## 判断

作業者が PR 作成を明示したときは、エージェントが `gh pr create` を実行してよい。

- 実行前に PR のタイトルと本文を見せ、作業者の承認を取る
- 作成後は `gh pr view` などで PR が実在することを確かめてから報告する
- `gh` の認証は作業者の環境にあるものを使う。トークンの置き方はこのリポジトリで案内しない

0007 のうち、次は変えない。

- PR merge、Issue 作成・クローズ、リリース、ワークフロー、機密情報、ルールセット変更などの GitHub 書き込みは、人間が実行するか、分離された仕組みで扱う
- `.env.example` や README に GitHub 書き込み用トークンの設定例を置かない

## 影響

メリット:

- 作業者の指示と rule が一致する
- PR を出すまでの手作業が減る

デメリット:

- `gh pr create` を実行できる環境では、書き込み権限付きのトークンがエージェントから読める。0007 が挙げた、誤操作やプロンプトインジェクションへの弱さは残る
- `gh` の認証が PR 作成以外の書き込みにも使えるため、PR 作成だけに限る仕組みは無い。PR 作成以外の書き込みをしないことは rule で守る

影響:

- `rules/worktree-workflow.md`、`rules/github-pr-workflow.md`、`rules/github-issue-workflow.md`、`rules/bash-safety.md` の PR 作成の扱いをこの判断に合わせる

## 関連する DR

- 一部変更する DR: [0007-withdraw-local-gh-agent-write.md](0007-withdraw-local-gh-agent-write.md)（PR 作成の扱いのみ）
- 関連: [0010-use-worktrees-and-hooks-for-isolated-changes.md](0010-use-worktrees-and-hooks-for-isolated-changes.md)
