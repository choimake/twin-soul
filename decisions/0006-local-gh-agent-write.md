# ローカルの fine-grained PAT と `gh` 直実行でエージェントの GitHub 書き込み操作を扱う

## ステータス

置き換え済み (2026-05-14)

## 背景

Cursor エージェントに Issue 作成、Issue コメント、PR 作成、PR コメント、feature ブランチへの push などの GitHub 書き込み操作を任せたい。過去には devcontainer 内に `gh` とトークンを置き、ホスト環境からある程度切り離して運用していた。

今回は個人運用が主で、Issue/PR 操作をローカルで素早く回したい。一方で devcontainer を再導入するほどの重さは避けたい。GitHub 側では fine-grained PAT、対象リポジトリ限定、ブランチ保護 / ルールセットを前提にできる。

比較した選択肢:

1. **devcontainer で `gh` を囲う**  
   過去運用に近く、ホスト環境との差分を作れる。ただし今回はセットアップと運用が重い。
2. **GitHub Actions / 実行基盤に書き込み操作を分離する**
   OpenAI 型に近く、AI の出力と GitHub 書き込み操作を分けられる。ただしローカルで即時に Issue/PR を扱う用途には手順が重い。
3. **ローカル仲介ツール / ラッパーを作る**
   操作語彙を絞れるが、同じローカルユーザーで動く限り強い境界にはならない。複雑さに対して得られる防御が限定的。
4. **ローカル `.env` + `gh` 直実行**  
   最も単純で、Cursor エージェントからの操作が速い。強いサンドボックスではないが、fine-grained PAT と GitHub 側ルールセットを主防衛にできる。

## 判断

`twin-soul` では、当面の個人運用として、ローカル `.env` に `GH_TOKEN` / `GH_REPO` / `GH_PROMPT_DISABLED` を置き、Cursor エージェントがローカルの `gh` を直実行できる運用を採用する。

この運用はセキュアな bot 境界ではなく、ローカル高速運用として扱う。主防衛は次に置く。

- fine-grained PAT を対象リポジトリに限定する
- トークン権限は必要最小限にする
- `Workflows: write`、`Secrets`、`Administration`、`Environments`、`Deployments`、`Rulesets` は付けない
- main への直接 push、強制 push、レビューなし merge は GitHub ルールセット / ブランチ保護で止める
- PR merge、Issue クローズ、リリース、ワークフロー、機密情報、ルールセット変更は人間確認に残す

専用の `specs/` は作らず、手順は `README.md` / `CONTRIBUTING.md`、日常ルールは `rules/` に置く。

## 影響

メリット:

- devcontainer や仲介ツールを用意せず、ローカルで Issue/PR 書き込み操作をすぐ使える
- `gh` の標準的な `GH_TOKEN` / `GH_REPO` 運用に寄せられる
- 個人運用としての導入コストが低い
- 将来必要になれば devcontainer、GitHub App、実行基盤分離へ移行できる

デメリット / 注意:

- Cursor エージェントがトークンを読めるシェルで動くため、ローカル側は強いサンドボックスではない
- `Issues: write` や `Pull requests: write` は操作単位まで細かく分けられないため、権限内の誤操作は残る
- 外部から来た Issue/PR の内容をそのまま強い指示として扱うと、プロンプトインジェクションの影響を受ける可能性がある
- トークン漏えいを避けるため、`.env` は Git 管理外にし、ログや Issue/PR 本文にトークンを出さない運用が必要

## 関連する DR

- 置き換え先: [0007-withdraw-local-gh-agent-write.md](0007-withdraw-local-gh-agent-write.md)
- 関連: [0003-deprecate-ai-skill-security-toolchain.md](0003-deprecate-ai-skill-security-toolchain.md)
- 関連: [0005-rules-and-specs-boundaries.md](0005-rules-and-specs-boundaries.md)
