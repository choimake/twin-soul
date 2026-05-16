# ローカルトークンでエージェントに GitHub 書き込み操作を任せる運用を撤回する

## ステータス

採用済み (2026-05-14)

## 背景

`decisions/0006-local-gh-agent-write.md` では、個人運用の速さを優先し、ローカル `.env` に GitHub トークンを置いて Cursor エージェントが `gh` を直実行できる運用を採用した。

その後、類似する OSS の運用を確認したところ、GitHub トークンを `.env.example` に明示する例は一部あるものの、エージェントに GitHub 書き込み操作を任せる運用では GitHub Actions secrets、GitHub App、runner トークン、専用ツールなどに寄せる例が目立った。ローカル `.env` + トークンは導入が軽い一方で、エージェントが読めるシェルに書き込み権限付きトークンを置くため、誤操作やプロンプトインジェクションに対する境界が弱い。

このリポジトリは `skill` と運用ルールの正本として使うため、便利さよりも「初見の作業者が真似しても危険が広がりにくい」案内を優先する。

## 判断

`twin-soul` では、ローカル `.env` に `GH_TOKEN` / `GH_REPO` / `GH_PROMPT_DISABLED` を置き、エージェントに `gh` 書き込み操作を直実行させる運用を撤回する。

具体的には次を行う。

- `.env.example` に GitHub 書き込み用トークンの設定例を置かない
- README / CONTRIBUTING / rules から、ローカル `.env` を読み込んで、エージェントに GitHub 書き込み操作を任せる手順を撤去する
- エージェントは Issue / PR 本文、コメント、PR 説明の下書きまでを基本とする
- Issue 作成、Issue クローズ、PR 作成、PR merge、リリース、ワークフロー、機密情報、ルールセット変更などの GitHub 書き込み操作は、人間が確認して実行するか、GitHub Actions / GitHub App / 実行基盤などの分離された仕組みで扱う

なお、個人がローカルで環境変数を持つ手段まで禁止するものではない。任意運用としては、Git 管理しない `mise.local.toml` に `[env]` を置き、`mise run` / `mise exec` / mise を有効化したシェルの範囲で `GH_TOKEN` などを渡す方法は成立する。ただしこれはローカルの利便性のための手段であり、書き込み権限付きトークンをエージェントが読める環境に置くリスク自体をなくすものではないため、標準手順として案内しない。

将来、エージェントに GitHub 書き込み操作を任せる必要が再び出た場合は、ローカルトークン直渡しではなく、権限・監査・実行境界を持つ仕組みを先に設計する。

## 影響

メリット:

- エージェントが読めるローカルシェルに GitHub 書き込み用トークンを置く運用を標準案内しなくなる
- `.env.example` からトークン用プレースホルダーを消し、実トークンの誤コミットやログ混入を誘発しにくくなる
- 公開リポジトリとして、利用者が安易に書き込み権限付きトークンをエージェントに渡す導線を減らせる

デメリット:

- ローカルで Issue / PR 操作をエージェントに即時実行させる導入の速さは失われる
- GitHub 書き込み操作を自動化したい場合は、人間確認または分離実行の設計が別途必要になる

影響:

- `decisions/0006-local-gh-agent-write.md` は置き換え済みとして履歴に残す
- `README.md`、`CONTRIBUTING.md`、`rules/` からローカルトークン直渡しの運用説明を撤去する

## 関連する DR

- 置き換え元: [0006-local-gh-agent-write.md](0006-local-gh-agent-write.md)
- 関連: [0003-deprecate-ai-skill-security-toolchain.md](0003-deprecate-ai-skill-security-toolchain.md)
- 関連: [0005-rules-and-specs-boundaries.md](0005-rules-and-specs-boundaries.md)
