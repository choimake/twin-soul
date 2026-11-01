# multi-model-debate skill の席とラウンド数の上限は、利用先のルートの gitignore した `.multi-model-debate.md` に書く

## ステータス

採用済み (2026-11-01)

## 背景

`skills/multi-model-debate` は、議論役の席（CLI とモデルの組）とラウンド数の上限を、skill の中の `config/defaults.yaml` から読んでいた。

使えるツールとモデルは、環境によって違う。同じ環境でも、トークンの上限に達したモデルは回復まで使えない。そのため席は環境ごとに変えたい。かといって、議論のたびにプロンプトで席を指示するのは手間がかかる。

一方、skill は APM で利用先へ配る。利用先の skill のディレクトリ（`.claude/skills/` など）は install のたびに置き換わるので、利用先で `defaults.yaml` を書き換えても次の `apm update` で消える。既定値を変えるには、このリポジトリの `defaults.yaml` を直すしかなく、環境ごとに変えられなかった。

APM に、依存パッケージから利用先へ設定を渡す仕組みが無いことは `decisions/0012-require-decision-records-config-file.md` で確認済み。

## 検討した選択肢

設定の置き場:

- skill の中の `config/defaults.yaml` のまま
  - 良い点: 変更が要らない
  - 悪い点: 環境ごとに変えられない
- 毎回プロンプトで席を指示する
  - 悪い点: 議論のたびに入力の手間がかかる
- 利用先のルートの `.multi-model-debate.md` をコミットして共有する
  - 良い点: `decision-records` の `.decision-records.md` と同じ形
  - 悪い点: 環境ごとに使えるモデルが違うので、共有した席が合わない人が出る。上限に達して席を替えるたびに差分が出る
- 利用先のルートの `.multi-model-debate.md` を gitignore する
  - 良い点: 環境ごとに書き換えても差分が出ない
  - 悪い点: 環境ごとに 1 回ずつ置く手間がかかる
- AGENTS.md に節を設ける
  - 悪い点: 毎回の文脈に読み込まれる。0012 と同じ理由で採らない

ファイルが無いときの動き:

- `decision-records` と同じく、何もせずに止まる
  - 悪い点: 席はその場で聞けば決まるのに、議論を始められない
- 席をその場で聞いて進め、あわせて雛形を置いてよいか聞く
  - 良い点: ファイルを置く前でも議論を始められる

## 判断

skill は、「起動時の指定 → 利用先のルートの `.multi-model-debate.md` → ユーザーに聞く」の順で、席とラウンド数の上限を決める。上限がどこにも無ければ 2 回にする。

`.multi-model-debate.md` はコミットせず、`.gitignore` に入れる。環境や上限で使えるモデルが変わったら、このファイルを書き換える。プロンプトで毎回指示しなくてよい。

ファイルが無くても議論は止めない。席をその場で聞いて進め、雛形を置いて `.gitignore` に足してよいかを聞く。了承されたら、skill の `assets/` に同梱した雛形をルートへコピーする。中身は人が埋める。

`config/defaults.yaml` は消す。

## 影響

メリット:

- 環境や上限に合わせて席を変えられる
- 議論のたびに席を指示しなくてよい
- `apm update` で設定が消えず、書き換えても差分が出ない

デメリット:

- チームで共有する既定の席は持てない。環境ごとに置く

影響:

- このリポジトリの `.gitignore` に `.multi-model-debate.md` を足す
- `specs/installing-shared-skills.md` の「利用先で置くファイル」に足す
- `verification-loop` と `consensus-investigation` は、同じ形の `config/defaults.yaml` を使ったままで、この判断の対象外

## 関連する DR

- 関連: [0012-require-decision-records-config-file.md](0012-require-decision-records-config-file.md)
- 関連: [0004-use-apm-for-shared-skill-distribution.md](0004-use-apm-for-shared-skill-distribution.md)
