# Skill Creator 判断知識

この資料は `skill-creator` skill の判断知識をまとめたものである。`SKILL.md` は使い方に留め、skill の構成設計、ファイル分割、テンプレート選択の詳細判断はこの資料を起点にする。

テンプレート:

- [../assets/skill-template.md](../assets/skill-template.md)
- [../assets/reference-template.md](../assets/reference-template.md)
- [../assets/test-prompt-template.md](../assets/test-prompt-template.md)

読み方:

- 新規作成では「呼び出し側が渡せる入力」「意図確認」「新規 skill の進め方」「description の trigger 品質チェック」を優先する
- 既存改稿では「既存 skill の改稿方針」「反復ループ」「ファイル分割ルール」を優先する
- `references/` が長くなる場合は、冒頭にこのような読み方や目次を置き、必要な箇所だけ読めるようにする

## skill の役割

Agent Skill は、特定の作業を毎回ゼロから説明しなくてよい状態にするための workflow である。

- `SKILL.md` は入口として短く保つ
- 長い判断知識は `references/` に逃がす
- 再利用する骨格や本文雛形は `assets/` に置く
- 実行補助が必要なときだけ `scripts/` を足す

一般的な Agent Skills は、`SKILL.md` を含むディレクトリ単位のパッケージとして扱う。

- 最低限 `SKILL.md` があり、YAML frontmatter と Markdown body を持つ
- `name` と `description` は必須
- `scripts/`、`references/`、`assets/` は任意リソース
- agent は最初に `name` と `description` だけを見て、必要になったときに `SKILL.md` と補助ファイルを読む
- 特定クライアント向けの field や配置ルールは、標準仕様とは分けて扱う

## 呼び出し側が渡せる入力

呼び出し側は、必要に応じて次を渡せる。

- 対象ディレクトリや既存 skill の `@path`
- skill 名、用途、トリガー語
- `review` / `draft` / `write-file` のような出力モード
- 追加したいファイルの種類
- 保存先のファイルパス

未指定なら、この skill が会話から妥当な既定値を判断する。必要最低限の確認だけを追加で行う。

出力モードの既定値:

- 既存 skill の方針確認や構成見直しは `review`
- 新規 skill の下書き、たたき台、テンプレートに沿った本文を求められた場合は `draft`
- 保存先が明示され、ファイル作成を依頼された場合だけ `write-file`
- 構成方針と本文の両方を求められている場合は `draft`

## 意図確認

新規 skill や大きな改稿では、本文を書く前に intent を確認する。会話履歴に十分な材料がある場合は、先に抽出してから不足分だけ聞く。

会話から拾うもの:

- ユーザーが繰り返し説明している作業
- 実際に使った手順、コマンド、ツール、参照ファイル
- ユーザーが修正した点、嫌がった出力、望んだ出力
- 入力形式、出力形式、成功条件
- skill 化したい一時的な作業なのか、継続的に使う workflow なのか

確認すること:

- この skill が agent に可能にする作業は何か
- どんな依頼、ファイル、状況で trigger すべきか
- 期待する出力形式や、返答の粒度は何か
- test prompt で確認する価値があるか
- 利用先リポジトリ や client 固有の制約があるか

客観的に確認できる出力（ファイル変換、コード生成、固定手順、抽出処理など）は test prompt を用意しやすい。文章の好みや創作寄りの出力は、少数例の人手レビューで十分なことが多い。

## 対象と探索の絞り方

1. ユーザーが `@path` で対象 skill や `skills/` 配下のディレクトリを指定したら、その対象を中心に扱う。
2. `review` / `draft` / `write-file` が明示されていれば、それを優先する。未指定なら依頼内容から推定する。
3. 対象 skill や用途が曖昧なら、skill 名、想定ユースケース、保存先のどれかを確認する。
4. 対象が曖昧な間は、確認質問だけを返し、具体的な本文作成には入らない。
5. 対象が決まったら、その skill に関係する既存 skill と、必要なリポジトリ 正本（例: `AGENTS.md`、`rules/`、`specs/`）だけを確認すると明示する。
6. `skills/` 配下の全件読了を前提にしない。まずは用途、ファイル名、トリガー語で関連 skill を絞る。
7. スコープ拡張が必要な場合は、まず現スコープで足りない理由と、追加で読みたいファイルを説明する。

## skill package と配置

一般的な構成:

```text
skill-name/
├── SKILL.md
├── scripts/
├── references/
└── assets/
```

判断:

- `skill-name/` は skill の配布・導入・レビューの単位にする
- `SKILL.md` の `name` は親ディレクトリ名と一致させる
- category 用の親ディレクトリがある場合でも、skill の identity は `SKILL.md` を直接含むディレクトリ名と `name` で決まる
- skill は、利用先リポジトリにこのリポジトリの `specs/` や `decisions/` がなくても成立するよう、必要知識を skill 配下へ閉じる
- このリポジトリでは `skills/<skill-name>/` を skill の正本とし、`.agents/skills/`、`.cursor/skills/`、`.claude/skills/` などの導入先・展開先は正本として扱わない

## 安全原則

skill の内容は、`description` や依頼内容からユーザーが予期できる範囲に収める。

- malware、credential 収集、data exfiltration、unauthorized access を助ける skill は作らない
- ユーザーに見える目的と実際の挙動がずれる misleading な skill は作らない
- 外部サービスや network access が必要な場合は、`compatibility` や導入手順で前提を明示する
- secret、token、個人情報をテンプレートや example に埋め込まない
- 安全上の境界が曖昧なら、本文作成より先に用途と許容範囲を確認する

## ファイル分割ルール

### `SKILL.md` に書くもの

- その skill が何を扱うか
- いつ使うか
- どの順で進めるか
- 何を返すか
- どの状態なら完成と言えるか

`SKILL.md` は入口に徹する。

- 長い背景説明や細かな判断条件は書き込まない
- 外部参照は 1 段深さに留める
- 500 行未満を維持する前提で圧縮する
- 目安として 5000 token 未満に収め、毎回読むべき中核手順だけを置く
- 詳細資料へのリンクには「いつ読むか」を添える

### `references/` に書くもの

- 判断基準
- 用語の定義
- 既定値や fallback
- レビュー観点
- 出力モードごとの差分
- どの情報をどのファイルへ置くかの配分基準

`references/` は「なぜそう分けるか」を持つ場所であり、毎回読み上げる本文ではない。

- リポジトリ全体に効く横断方針を置くトップレベル `rules/` とは役割を分ける
- skill ローカルの判断観点や個別ルール本文は、原則としてその skill 配下の `references/` に置く
- `references/` 配下の下位構成は skill ごとに決めてよく、必要な場合だけ `references/rules/` のようなディレクトリを切る
- 1 つの reference が 300 行を超える場合は、冒頭に読み方や目次を置く
- 複数 domain、framework、tool を扱う場合は、`references/aws.md`、`references/gcp.md` のように variant ごとのファイルへ分ける

### `assets/` に書くもの

- `draft` や `write-file` の起点にするテンプレート
- 繰り返し使う章立て
- 定型の見出し、プレースホルダ、コメント

`assets/` には判断知識ではなく再利用する骨格を置く。

- 章を省略せず使える形にする
- 具体的なプロジェクト判断は埋め込まない
- `draft` でそのまま流用できる形にする

### `scripts/` に書くもの

`scripts/` は次の条件を満たすときだけ追加する。

- 手順が壊れやすく、毎回同じ処理を再現したい
- 検証や生成をテキスト指示だけで安定化しにくい
- 短い説明より実行補助の方が確実

昇格させる判断:

- 複数の test prompt や反復で、同じ整形・検証・生成を繰り返している
- 毎回ほぼ同じ helper script やコマンド列を書き直している
- test prompt の実行で agent が毎回似た helper を作っている
- 入力と出力が比較的はっきりしていて、再利用しやすい
- 人手判断より、決まった手順の実行が中心になっている

まだ昇格させない判断:

- その場限りの一時的な確認だけで済む
- 毎回必要な分岐や判断が多く、script に閉じ込めると硬すぎる
- 1 回の試行でしか使っていない
- script 自体の保守コストが、手作業のコストを上回る

原則:

- まずは `scripts/` なしで設計する
- 追加するなら、何を実行する script かを `SKILL.md` と `references/` で明示する
- 依存関係、起動方法、期待結果、失敗時の扱いを書く
- Python を使う場合でも、必要性があるときだけに限る
- `mise` や `uv` はプロジェクトの運用に合う場合だけ採用し、skill の必須前提にはしない

Python を使うときの目安:

- まずは標準ライブラリだけで足りるかを見る
- 外部依存が増えるなら、本当に script 化の価値があるかを先に確認する
- `mise` や `uv` を使うのは、依存管理や再現性が実際に問題になる場合に限る
- script を入れたら、手で同じ処理を毎回やるより楽になっていることを確認する

## 新規 skill の進め方

1. skill が扱う作業を一文で整理する。
2. trigger すべき状況、期待出力、対象外を確認する。
3. 既存 skill のうち、用途や構造が近いものだけ読む。
4. トリガー語を含む `name` と `description` を決める。
5. `SKILL.md` に入口として必要な章だけを書く。
6. 詳細判断が多いなら `references/` を追加する。
7. 定型本文が必要なら `assets/` にテンプレートを置く。
8. 実行補助が必要なら、そのときだけ `scripts/` を足す。

## YAML frontmatter

`SKILL.md` の先頭 frontmatter は、厳密な YAML として読める形にする。

- `name` は小文字英数字とハイフンで書く
- `name` は 64 文字以内にし、親ディレクトリ名と一致させる
- `name` はハイフンで開始・終了しない
- `name` には連続ハイフンを使わない
- `description` は 1024 文字以内にする
- `description` は plain scalar にせず、原則 `description: >-` と 2 スペースインデントの本文で書く
- `description` には Markdown のバッククォート、`:`、`#`、引用符などが入り得るため、1 行のクォートなし値にしない
- `description` の本文は WHAT と WHEN を含め、trigger 語と境界が見える内容にする
- `license` は必要な場合だけ短いライセンス名か同梱ライセンスファイル名を書く
- `compatibility` は特定環境、必要コマンド、network access などの制約がある場合だけ書く
- `metadata` は追加情報が必要な場合だけ key-value で書く
- `allowed-tools` は実験的 field として扱い、利用先 agent が対応している場合だけ検討する

例:

```yaml
---
name: example-skill
description: >-
  この skill が何をするかを書く。続けて、どんな依頼、キーワード、状況のときに使うかを書く。
compatibility: Requires git and network access
---
```

### client-specific field の扱い

Agent Skills 標準にない field は、利用先 client の拡張として扱う。

- file scoping 用 field（例: `paths`、legacy の `globs`）は、その client が対応していると分かる場合だけ使う
- slash command 的に明示実行だけへ寄せる field（例: `disable-model-invocation`）は、その client が対応していると分かる場合だけ使う
- skill の標準テンプレートへ client-specific field を常設しない
- client-specific field を入れる場合は、`compatibility` や `metadata` で前提を補足するか、利用先 project の導入手順に寄せる

## 反復ループ

skill 作成は、設計して終わりではなく、小さく試して直す反復として扱う。

基本ループ:

1. 目的、trigger 条件、出力形式を決める。
2. `SKILL.md` と必要な補助ファイルの下書きを作る。
3. 少数の test prompt を用意する。
4. その prompt で試行し、実際の出力や進め方を見る。
5. うまくいかなかった点を、skill の構成、説明、テンプレート、scripts のどこで直すべきかに分ける。
6. skill を改善して、同じ prompt か追加 prompt で再度試す。
7. 大きな問題がなくなったら、対象を少し広げて再確認する。

止めどき:

- 主要な test prompt で期待する流れが安定している
- 同じ修正を何度も繰り返していない
- `SKILL.md` を重くしすぎずに改善できている
- 追加した rule や template が個別例に過剰適合していない

反復中の見方:

- 出力だけでなく、skill が不要に長い手順や重複作業を誘発していないかを見る
- 問題が `description`、`手順`、`references/`、`assets/`、`scripts/` のどこにあるか切り分ける
- 1 つの例だけに合わせず、同系統の依頼へ一般化できる修正を優先する
- 指示が増えすぎたら、効いていない指示を削る
- 重要な制約は命令だけで押し切らず、なぜ必要かを短く説明する
- test prompt 間で同じ準備や helper 作成が繰り返されるなら、`assets/` や `scripts/` へ移す価値を検討する

eval / benchmark の扱い:

- 通常の skill 作成では、2-3 件の test prompt と人手レビューで足りることが多い
- 客観的な期待値を持つ task では、必要に応じて `evals/` や JSON の期待条件を追加してよい
- baseline 比較、複数回実行、pass rate、token、実行時間の集計は optional advanced として扱う
- eval / benchmark の仕組みを入れる場合も、通常 workflow の利用者に毎回実行を強制しない

## test prompt の作り方

test prompt は、skill が実際に使われる場面を小さく再現するために作る。

基本方針:

- 最初は 2-3 件に絞る
- 実際のユーザーが言いそうな依頼文にする
- prompt ごとに、何を見れば成功かを先に決める
- 1 件ごとに違う観点を持たせる

観点の候補例:

- 典型ケース: skill の中核機能が素直に必要な依頼
- 境界ケース: 情報不足、曖昧さ、分岐が出る依頼
- 近接ケース: 関連はするが、skill の適用範囲を見極めたい依頼

この 3 分類に固定する必要はない。skill に応じて、確認質問の質、出力モードの違い、対象スコープの曖昧さなど、別の軸で組んでよい。

書き方:

- 抽象語だけで終わらせず、状況、対象、期待する成果物を少し入れる
- file path、対象ファイル、依頼背景など、実務で出やすい具体性を混ぜる
- skill 名を露骨に埋め込まず、自然な依頼文を優先する
- その prompt で何を確認したいかを 1 行で添える

避けたい例:

- 1 行で終わる不自然に短い依頼
- skill 名や正解手順をそのまま言ってしまう依頼
- ほぼ同じ言い回しだけを変えた prompt 群
- その例にだけ最適化すると汎用性を失う prompt 群

評価時に見ること:

- skill が本来の場面で自然に使われるか
- 必要な確認質問を返せるか
- 出力形式や進め方が期待と合うか
- 1 つの prompt に引っ張られすぎた修正になっていないか

test prompt の下書きには [../assets/test-prompt-template.md](../assets/test-prompt-template.md) を使ってよい。

## 既存 skill の改稿方針

1. `SKILL.md` に長い判断知識が入り込んでいないかを見る。
2. テンプレート化できる部分を `assets/` へ逃がす。
3. 判断基準や分類ロジックを `references/` へ逃がす。
4. 入口として必要な文章だけを `SKILL.md` に残す。
5. `description` が WHAT と WHEN を含み、トリガー語を持つか確認する。
6. フィードバックを個別例に貼り付けず、同系統の依頼に効く形へ一般化する。
7. 使われていない指示、重複した指示、過度に狭い MUST を削る。
8. 重要な制約や手順は、短い理由を添えて agent が判断できる形にする。

改稿時に避けること:

- 1 つの test prompt だけに合わせて、他の依頼で不自然になる修正
- `SKILL.md` に詳細な例外や背景を積み上げる修正
- 近接 skill との境界を曖昧にする広すぎる description
- script 化すべき繰り返し処理を、長い文章指示だけで押し切る修正

## description の trigger 品質チェック

`description` は skill の入口判定に直結するため、本文より先に質を見る。

最低限の確認:

- WHAT: その skill が何をするかが一文で分かる
- WHEN: どんな依頼や状況で使うかが入っている
- Trigger terms: ユーザーが実際に使いそうな語が含まれている
- Boundary: 近いが別の task と混同しにくい
- Intent: 実装詳細ではなく、ユーザーが達成したい目的に寄せている
- Concision: 1024 文字以内で、長すぎる説明になっていない

undertrigger を避ける観点:

- skill 名を知らない依頼でも拾える語があるか
- ファイル種別、成果物、作業動詞など別の言い回しを拾えるか
- 「こういうときに使う」が弱すぎないか
- ユーザーが skill 名を言わなくても、その task で使うべき具体文脈が入っているか
- 短い keyword だけでなく、依頼の目的や成果物に基づく trigger が入っているか

overtrigger を避ける観点:

- 近接 task まで過剰に取り込みそうな広すぎる語だけで書いていないか
- skill の責務外まで含む説明になっていないか
- 一般的すぎる表現だけで他 skill と衝突しないか

近接 task との境界で見ること:

- その skill が勝つべき状況と、別 workflow に寄せるべき状況が説明から読み取れるか
- 類似語を含んでも、対象ファイル、出力形式、目的で差別化できているか

description 評価用 prompt:

- should-trigger と should-not-trigger を混ぜる
- near miss（近い語を含むが別 task）を必ず入れる
- skill 名を明示しない依頼を入れる
- 具体的な file path、曖昧な言い方、短い依頼、長い背景付き依頼を混ぜる
- 評価結果をもとに直すときは、個別 prompt の語を貼り付けず、一般化した trigger / boundary に直す

短い確認質問:

- この description を読んだだけで「何をする skill か」が分かるか
- skill 名を知らないユーザーの依頼でも trigger できそうか
- 似た依頼で誤発火しそうな箇所はないか

## 出力モードごとの期待

### `review`

- skill 構成の判断と進め方だけを返す
- どのファイルを作るか、何をどこへ移すかを整理する
- 本文全体はまだ出さない

### `draft`

- まず短い説明で、対象範囲と構成判断を要約する
- 続けて必要なファイルごとに file-ready な本文を返す
- `SKILL.md`、`references/`、`assets/` の順で返す
- テンプレートの章は省略しない

### `write-file`

- ユーザーが保存先の `@path` やファイルパスを明示したときだけ使う
- 実ファイルを書いた後に、作成先と構成判断を短く報告する
- `skills/` を更新した場合は、最後に `mise run ci:apm`（または `apm install --target cursor,claude && apm audit --ci --no-policy`）で APM 配布前提を確認する
- 保存先が明示されていない場合は `write-file` に入らず、`draft` にフォールバックする

## 応答時の明示事項

対象が未指定のとき:

- まず skill 名、用途、保存先のどれを先に決めるか確認する短い質問だけを返す
- 対象が決まったら、関連 skill と必要なリポジトリ 正本だけを確認して進めると添える

新規 skill の依頼では、返答の冒頭に次の文を入れる。

> 既存 skill の全件読了はせず、用途や構造が近い skill と必要なリポジトリ 正本だけを確認して進めます。`SKILL.md` は workflow、`references/` は判断知識、`assets/` はテンプレートとして分けます。

`scripts/` を追加しない判断をした場合は、次を地の文で明示してよい。

- 実行補助がなくても安定して運用できるため、今回は `scripts/` を追加しない
- 繰り返し処理や検証が必要になった時点で追加を検討する

## 完了チェック

- `name` は小文字英数字とハイフンで一意に付けている
- `name` は親ディレクトリ名と一致している
- `description` は `>-` の block scalar で書き、YAML frontmatter として安全に読める
- `description` は 1024 文字以内で、WHAT と WHEN を含む
- `description` は trigger 語と近接 task との境界を含む
- `description` は undertrigger を避ける具体文脈を含み、overtrigger しない境界も持つ
- `SKILL.md` は薄く、詳細を `references/` へ逃がしている
- 詳細参照には、そのファイルをいつ読むかが書かれている
- unsafe / misleading な skill を作らない安全原則が守られている
- テンプレートは `assets/` にあり、`draft` の起点にできる
- `scripts/` は必要性があるときだけ追加している
- eval / benchmark は必要な skill にだけ任意追加し、通常 workflow に必須化していない
- client-specific field を標準 field と混同していない
- 用語が一貫している
- トップレベル `rules/` と skill 配下の `references/` の役割が文書上で混同されていない
