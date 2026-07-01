# Gitignore Skill

`gitignore` skill は、`.gitignore` の新規作成、既存 `.gitignore` の見直し、`gitignore.io` テンプレートの取得、リポジトリからの template 候補の自動推定をまとめて扱います。`gitignore.io` にない tool についても、custom 手書きルールを足す前提で扱えます。

## 概要

- `.gitignore` の `review` / `draft` / `write-file` を整理して進める
- `gitignore.io` の template 候補を選び、必要なら helper script で取得する
- リポジトリ内の手掛かりから OS、言語、IDE、tool の候補を自動推定する
- `mise` のような template がない tool は custom ignore block として扱う

## なぜ必要か

- `gitignore.io` を毎回手で見に行かなくても、候補出しから本文作成まで進めやすい
- 既存 `.gitignore` の generated block と手書き block を混同しにくい
- リポジトリの構成に合わせて template を絞れるので、過不足のある `.gitignore` になりにくい
- custom ルールも `assets/` と `references/` に分けて保守できる

## はじめ方

前提:

- `skills/gitignore/` 配下のファイルを参照できること
- `gitignore.io` 取得を使う場合は `curl` など helper script の前提コマンドがあること

最短手順:

1. `gitignore` skill を呼ぶ
2. 対象リポジトリと、`review` / `draft` / `write-file` のどれかを伝える
3. 必要なら `gitignore.io` template 候補の自動推定や custom ルール追加も一緒に頼む

依頼例:

```text
このリポジトリの .gitignore を見直したい。リポジトリを見て template 候補を自動推定して、必要なら draft して。
```

helper script を直接使う場合:

```bash
bash skills/gitignore/scripts/fetch-gitignore.sh detect .
bash skills/gitignore/scripts/fetch-gitignore.sh auto .
```

期待する結果:

- 推奨 template 名と、その選定理由が分かる
- 必要なら file-ready な `.gitignore` 案が返る
- custom 手書き block が必要な場合でも、generated block と分けて扱える

## サポート

- Skill 本体: [`SKILL.md`](SKILL.md)
- 判断知識 hub: [`references/gitignore-knowledge.md`](references/gitignore-knowledge.md)
- レビュールール: [`references/rules/`](references/rules/)
- レビュー出力テンプレート: [`assets/review-output-template.md`](assets/review-output-template.md)
- custom block 例: [`assets/mise-local-overrides.gitignore`](assets/mise-local-overrides.gitignore)
- 検証用 prompt: [`assets/test-prompts.md`](assets/test-prompts.md)
- helper script: [`scripts/fetch-gitignore.sh`](scripts/fetch-gitignore.sh)
