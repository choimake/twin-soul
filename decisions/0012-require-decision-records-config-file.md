# decision-records skill は、利用先のルートの `.decision-records.md` に書いた保管先と作成基準がなければ動かない

## ステータス

採用済み (2026-10-15)

## 背景

`skills/decision-records` は APM で他のリポジトリへ配る。DR を作るかの基準は `rules/when-to-create-decision-records.md` にあるが、`rules/` は配らないので、利用先では skill だけが届く。

skill を外部の視点でレビューすると、基準が skill の中に無いことが課題として挙がった。基準は利用先ごとに違ってよいので、skill に固定せず、利用先が決めて渡せるようにしたい。

APM（0.32.0 で確認）には、依存パッケージから利用先へ設定を渡す仕組みも、利用先のルートにファイルを置く仕組みも無い。

- 依存パッケージに書いた `lifecycle:` の post-install は、利用先の `apm install` では走らない。走るのは、利用先の `apm.yml`、`~/.apm/apm.yml`、管理者ポリシーに書いたものだけ
- skill のディレクトリ（`.claude/skills/` など）は install のたびに置き換わり、`.gitignore` の対象にもなる。ここに基準を置くと消えるか、チームで共有されない

## 検討した選択肢

- 利用先のルートの `.decision-records.md` に置く
  - 良い点: 場所が一つに決まる。DR の保管先も同じファイルに書ける。adr-tools の `.adr-dir` や log4brains の `.log4brains.yml` と同じ形
  - 悪い点: ドットファイルなので気づきにくい。ファイルが一つ増える
- DR 保管ディレクトリの README.md に置く
  - 良い点: DR と並ぶので見つけやすい
  - 悪い点: 保管ディレクトリの名前が利用先で違うので、先にディレクトリを探す必要がある
- AGENTS.md に節を設ける
  - 良い点: ファイルが増えない
  - 悪い点: 毎回の文脈に読み込まれる。節の見出しで探すので、書き方がずれると見つからない

基準ファイルを利用先に置く方法も比べた。

- install で配る SessionStart hook が、ファイルが無ければ雛形を作る
  - 良い点: 人が何もしなくても雛形ができる
  - 悪い点: 利用先の `.claude/settings.json` が書き換わる。毎回のセッションでスクリプトが走る。Cursor で発火するかは確かめていない
- skill が雛形を同梱し、ファイルが無ければ置いてよいかを聞いてコピーする
  - 良い点: APM の版やエージェントの種類に関係なく同じように動く
  - 悪い点: 最初に一度、人の了承が要る

## 判断

skill は、利用先のルートの `.decision-records.md` を読んでから動く。このファイルには「保管先」と「DR を作る基準」の 2 つの節を書く。基準は本文でも、別の文書へのリンクでもよい。

ファイルが無いか、どちらかの節が雛形のままなら、DR の作業は何もしない。新規作成だけでなく、既存 DR の更新や誤字修正もしない。基準が無いまま動かすと、利用先ごとに作る・作らないが揺れるため。

雛形は skill の `assets/` に同梱する。ファイルが無いときは、置いてよいかを聞いて、了承されたらルートへコピーする。節の中身は人が埋める。

## 影響

メリット:

- 利用先ごとに DR を作る基準を決められる
- 保管先を探さなくてよくなる

デメリット:

- 既に skill を入れている利用先では、`.decision-records.md` を置くまで skill が止まる
- 誤字直しのような小さな作業でも、ファイルが無いと止まる

影響:

- このリポジトリのルートにも `.decision-records.md` を置き、保管先を `decisions/`、基準を `rules/when-to-create-decision-records.md` へのリンクにする
- `specs/installing-shared-skills.md` に、利用先で置くファイルとして書く

APM が依存パッケージから利用先へファイルや設定を渡せるようになったら、雛形を置く方法を見直す。

## 関連する DR

- 関連: [0004-use-apm-for-shared-skill-distribution.md](0004-use-apm-for-shared-skill-distribution.md)
- 関連: [0008-use-root-skill-collection-for-apm-install.md](0008-use-root-skill-collection-for-apm-install.md)
