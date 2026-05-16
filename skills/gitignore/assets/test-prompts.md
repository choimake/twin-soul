# Gitignore テストプロンプト

最初は 3-4 件に絞る。

## セット確認

- Coverage: リポジトリ 自動推定、新規作成、既存更新、custom 手書きルールをそれぞれ見られるようにする
- Diversity check: 言語、OS、依頼の粒度を変え、同じ言い換えだけの prompt 群にしない
- Overfitting risk: Node 系の定番ケースだけに最適化して、曖昧なリポジトリ や既存 `.gitignore` 更新を落とさないかを見る

## プロンプト 1

- Type: 自動推定ケース
- 目的: リポジトリの手掛かりから template 候補を自動推定し、必要なら `auto` 取得までつなげられるか確認する
- 理由: この拡張で一番楽にしたい流れだから
- Prompt:

```text
このリポジトリの .gitignore を作りたい。まずリポジトリを見て `gitignore.io` の template 候補を自動で出して、よさそうならそのまま draft して。
```

- Success signals:
  - リポジトリの手掛かりと `detect` / `auto` の利用方針を自然に選べる
  - 候補 template 名だけで終わらず、必要なら file-ready な `.gitignore` 本文案まで返せる
  - 自動推定結果が弱いときだけ追加確認に進める
- Overfitting risk: script 前提に寄りすぎて、明示情報だけで十分なケースでも遠回りしないか

## プロンプト 2

- Type: 境界ケース
- 目的: 情報不足のときに、断定せず短い確認質問へ寄せられるか確認する
- 理由: 実際には stack や IDE が曖昧な依頼も多いため
- Prompt:

```text
このリポジトリの .gitignore を見直したい。今のやつが足りてるか不安。
```

- Success signals:
  - 既存 `.gitignore` の有無を確認するか、リポジトリ内の手掛かりや `detect` 結果を最小限見る方針を取れる
  - いきなり template を決め打ちせず、必要な確認だけ返せる
  - `review` を既定にする流れが自然
- Overfitting risk: 質問ばかり増やして前に進めなくなると、典型ケースでの速度を損なう

## プロンプト 3

- Type: 更新ケース
- 目的: 既存 `.gitignore` の手書きルールを壊しにくい更新方針を取れるか確認する
- 理由: 現実のリポジトリでは新規作成より更新の方が危険なことが多いため
- Prompt:

```text
今の .gitignore は Python 用っぽいんだけど、最近 Terraform も入った。既存の手書きルールは残したいので、何を足すべきか review して、必要なら update 案も出して。
```

- Success signals:
  - `review` と `draft` を分けて扱える
  - `python` と `terraform` の template 候補を挙げられる
  - 既存の手書きルールを保持しつつ差分ベースで更新する方針を返せる
- Overfitting risk: 既存ファイル保護を重視しすぎて、新規作成ケースで冗長にならないか

## プロンプト 4

- Type: custom ルールケース
- 目的: `gitignore.io` にない tool を custom 手書き block として扱えるか確認する
- 理由: template がない tool を扱えないと、実務では最後に手作業が残るため
- Prompt:

```text
このプロジェクトは mise を使ってる。gitignore.io の結果に加えて、mise 用に必要な ignore を手書きで足したい。何を入れるべきか含めて draft して。
```

- Success signals:
  - `mise` には template がない前提を自然に扱える
  - `mise.toml` は残しつつ、`mise.local.toml` 系だけ ignore 対象にできる
  - `gitignore.io` 由来 block と custom 手書き block を分けて返せる
  - 再利用できる custom block を `assets/` 起点で扱える
- Overfitting risk: `mise` 専用の例に引っ張られて、他の custom ルール候補まで雑に扱わないか
