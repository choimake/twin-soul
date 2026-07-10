# GitHub Pull Request ワークフロー

## 目的

PR 本文の書式をリポジトリのテンプレートに揃え、レビューと公開前チェックの抜け漏れを防ぐ。

## 背景

エージェントや作業者が独自の Summary / Test plan 形式で PR を作ると、テンプレートの検証項目や公開リポジトリチェックリストが落ちる。本リポジトリでは `.github/pull_request_template.md` を正本とする。

## PR 本文はテンプレートに従う

PR を作成・更新するときは、[`.github/pull_request_template.md`](../.github/pull_request_template.md) の見出しとチェックリストをそのまま使う。独自のセクション構成（例: `## Summary` / `## Test plan` のみ）に置き換えない。

必須セクション:

1. **概要** — なぜ必要か、何を変えたかを短く書く。関連 Issue / DR / specs があればリンクする
2. **検証** — テンプレートのコマンドを、実行済みなら `[x]`、未実行なら `[ ]` のまま残す。追加の検証があれば同じ節に追記してよい
3. **公開リポジトリチェックリスト** — 機密情報・生成 skill 反映・下流影響の各項目を埋める

### 良い例（骨格）

```markdown
## 概要

- 〈変更の要点〉
- 〈下流 skill への影響があれば書く〉

## 検証

- [x] `mise run ci:lint`
- [x] `mise run ci:apm`

## 公開リポジトリチェックリスト

- [x] 機密情報、認証情報、非公開 URL、非公開プロジェクトのデータを含めていない
- [x] `skills/` の変更が必要に応じて生成済み `skill` ディレクトリに反映されている
- [x] `skill` の挙動が変わる場合、下流プロジェクトへの影響を説明している
```

### 悪い例

- テンプレートを無視して `## Summary` / `## Test plan` だけにする
- 検証コマンドを実行していないのにすべて `[x]` にする
- 公開リポジトリチェックリストを削除する

## Issue / PR の作成とコメント

Agent は PR 本文の下書きまでを基本とする。GitHub write（`gh pr create` 等）は人間が確認して実行するか、分離された仕組みで扱う。詳細は [github-issue-workflow.md](github-issue-workflow.md) と `decisions/0007-withdraw-local-gh-agent-write.md` を参照する。

## 関連

- [`.github/pull_request_template.md`](../.github/pull_request_template.md) — PR 本文の正本
- [CONTRIBUTING.md](../CONTRIBUTING.md) — プルリクエストの期待値
- [github-issue-workflow.md](github-issue-workflow.md) — Issue 側の運用
