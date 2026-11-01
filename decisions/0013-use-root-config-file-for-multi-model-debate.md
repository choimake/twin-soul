# multi-model-debate skill の席とラウンド数の上限は、利用先のルートの `.multi-model-debate.md` に書く

## ステータス

採用済み (2026-11-01)

## 背景

`skills/multi-model-debate` は、議論役の席（CLI とモデルの組）とラウンド数の上限を、skill の中の `config/defaults.yaml` から読んでいた。

skill は APM で利用先へ配る。利用先の skill のディレクトリ（`.claude/skills/` など）は install のたびに置き換わるので、利用先で `defaults.yaml` を書き換えても次の `apm update` で消える。既定値を変えるには、このリポジトリの `defaults.yaml` を直すしかなく、利用先ごとに変えられなかった。

APM に、依存パッケージから利用先へ設定を渡す仕組みが無いことは `decisions/0012-require-decision-records-config-file.md` で確認済み。

## 検討した選択肢

設定の置き場:

- skill の中の `config/defaults.yaml` のまま
  - 良い点: 変更が要らない
  - 悪い点: 利用先ごとに変えられない
- 利用先のルートの `.multi-model-debate.md`
  - 良い点: `decision-records` の `.decision-records.md` と同じ形で、利用先がコミットして共有できる
  - 悪い点: ドットファイルが一つ増える
- AGENTS.md に節を設ける
  - 悪い点: 毎回の文脈に読み込まれる。0012 と同じ理由で採らない

ファイルが無いときの動き:

- `decision-records` と同じく、何もせずに止まる
  - 悪い点: 席は起動時に聞けば決まる。止める理由が無い
- 席をその場で聞いて進め、あわせて雛形を置いてよいか聞く
  - 良い点: 既に skill を入れている利用先でも、そのまま使える

個人ごとの上書き（gitignore したローカルファイル）は、今は要る場面が無いので作らない。

## 判断

skill は、「起動時の指定 → 利用先のルートの `.multi-model-debate.md` → ユーザーに聞く」の順で、席とラウンド数の上限を決める。上限がどこにも無ければ 2 回にする。

ファイルが無くても議論は止めない。席をその場で聞いて進め、雛形を置いてよいかを聞く。了承されたら、skill の `assets/` に同梱した雛形をルートへコピーする。中身は人が埋める。

`config/defaults.yaml` は消す。

## 影響

メリット:

- 利用先ごとに席と上限を決め、チームで共有できる
- `apm update` で設定が消えない

デメリット:

- 環境によって使える CLI が違う人がいると、共有した席が合わない。その人は起動時に指定して上書きする

影響:

- このリポジトリのルートにも `.multi-model-debate.md` を置く
- `specs/installing-shared-skills.md` の「利用先で置くファイル」に足す
- `verification-loop` と `consensus-investigation` は、同じ形の `config/defaults.yaml` を使ったままで、この判断の対象外

個人ごとに席を変えたい利用先が出たら、ローカルファイルでの上書きを見直す。

## 関連する DR

- 関連: [0012-require-decision-records-config-file.md](0012-require-decision-records-config-file.md)
- 関連: [0004-use-apm-for-shared-skill-distribution.md](0004-use-apm-for-shared-skill-distribution.md)
