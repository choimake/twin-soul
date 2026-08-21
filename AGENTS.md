# Project Instructions

このファイルは、このリポジトリで実際に守る共通方針の正本です。Cursor は `AGENTS.md` として読み、Claude Code は symlink された `CLAUDE.md` から同じ内容を読みます。

トップレベルの `rules/` はリポジトリ全体に効く横断方針の正本として扱います。

## 優先順位

文書がぶつかったら次の順で見ます。

1. `AGENTS.md` とトップレベル `rules/`
2. `skills/`
3. `specs/`
4. `README.md`
5. `decisions/`

## 基本方針

- 原則日本語で書き、日本語で応答する
- skill の導入・更新は Microsoft APM（Agent Package Manager）を使う
- このリポジトリを skill の正本として扱い、skill の更新はここで行う
- 技術選定や設計判断で Decision Record が必要な基準は `rules/when-to-create-decision-records.md` を参照する
- `decisions/` の新規作成・更新では `skills/decision-records` を使う
- 小規模プロダクトの要求定義の書式・層・属性の整理は `skills/requirements-definition` を参照する
- 実行補助が必要なときだけ `scripts/` を足す

## 役割

- `skills/`: 実務で使う workflow
- `rules/`: リポジトリ横断で守る方針
- `specs/`: 現在の構成と仕様
- `README.md`: 使い方の導線
- `decisions/`: 判断理由の記録
- `memory/`: エージェント作業のローカル記録（gitignore、正本ではない）

## 作業メモリ

- `memory/` は gitignore。共有の source of truth ではない
- 作業開始時に `memory/lessons.md` と `memory/handoff.md` を読む。無ければ作る
- 今回の作業に関係する `memory/notes/` だけ追加で読む
- 作業終了時、または長い作業の区切りで残す。学びは `lessons.md`、申し送りは `handoff.md`、作業メモは `notes/`
- 書かないもの: 秘密情報、会話の全文、正式文書のコピー
- チーム運用に効く知見は `memory/` に溜めず、`rules/` / `specs/` / `decisions/` / skill へ昇格する
- 雛形と詳細判断は `rules/working-memory.md`

## 変更作業

- 変更は `.worktrees/` の git worktree で行う。main checkout では編集しない
- 例外: `memory/` と調査・plan 作成（`.cursor/plans/`）
- hook が main 上の編集と `git add` / `commit` / `push` を止める
- 手順は `rules/worktree-workflow.md`

## 関連する rule の読み方

今回の作業に関係する `rules/` だけ先に読む。全部は読まない。

- ファイルを変更する → `rules/worktree-workflow.md`
- 文書を足す / 直す → `rules/documentation-standards.md`, `rules/document-consistency.md`
- DR が要るか迷う → `rules/when-to-create-decision-records.md`
- 破壊的な shell → `rules/bash-safety.md`
- Issue → `rules/github-issue-workflow.md`
- PR → `rules/github-pr-workflow.md`

hook に移すのは、絶対・二進・ツール入力だけで判定でき、文書にしたあと繰り返して破られた禁止だけ。判断が要る本文は `rules/` に残す。品質は `mise run ci:lint` / `ci:apm` で見る。

## 外部プロジェクトへの導入

- 他プロジェクトへ全 skill を入れるときは、利用先リポジトリで `apm install choimake/twin-soul#<ref> --target cursor,claude` を実行するか、`apm.yml` に `choimake/twin-soul#<ref>` を宣言して `apm install` を実行する
- 一部の skill だけを入れるときは、`choimake/twin-soul/skills/<skill-name>#<ref>` の subdirectory package を指定する
- `apm.lock.yaml` は利用先リポジトリでコミットし、全員・CI が同じ resolved commit を使う
- プライベートリポジトリとして使う場合は `GITHUB_APM_PAT`、`GITHUB_APM_PAT_{ORG}`、または `gh auth login` などの Git 認証を用意する
- 利用先リポジトリでは project 固有 skill を併置してよい
- 利用先リポジトリの skill は直接編集せず、このリポジトリ側を更新して `apm install --update` または `apm deps update` を実行する
- 詳しい導入手順は `specs/installing-shared-skills.md` を参照する

## 変更手順

1. `skills/`、`rules/`、`AGENTS.md`、必要なら `specs/` を編集する
2. このリポジトリで `mise run ci:lint`、`mise run ci:apm` を実行して静的チェックと APM 配布前提を確認する（`ci:apm` は展開先を実際に同期したうえで audit する）
3. skill を使っている利用先リポジトリでは `apm install --update`、`apm update`、または `apm deps update` を実行する
4. README や補助資料が古くなったら更新する

## Runtime Notes

- `skills/` は APM の Skill collection としてまとめて導入できる
- `skills/<skill-name>/` は APM の subdirectory package として個別に導入する
- Cursor 向け skill は APM 標準の `.agents/skills/` へ展開される
- Claude Code 向け skill は APM 標準の `.claude/skills/` へ展開される

## 完了条件

- 追加した `skill` に用途と手順がある
- APM で導入できる単位として `skills/<skill-name>/SKILL.md` が成立している
- 初見の作業者が読んで用途を追える
