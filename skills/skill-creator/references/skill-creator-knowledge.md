# Skill Creator 判断知識

## 出力モードの既定値

- 既存 skill の方針確認や構成見直しは `review`
- 新規 skill の下書き、たたき台、テンプレートに沿った本文を求められた場合は `draft`
- 保存先が明示され、ファイル作成を依頼された場合だけ `write-file`
- 構成方針と本文の両方を求められている場合は `draft`

## 意図確認

客観的に確認できる出力（ファイル変換、コード生成、固定手順、抽出処理など）は test prompt を用意しやすい。文章の好みや創作寄りの出力は、少数例の人手レビューで十分なことが多い。

## skill package と配置

- category 用の親ディレクトリがある場合でも、skill の identity は `SKILL.md` を直接含むディレクトリ名と `name` で決まる
- skill は、利用先リポジトリにこのリポジトリの `specs/` や `decisions/` がなくても成立するよう、必要知識を skill 配下へ閉じる
- このリポジトリでは skill を `skills/<skill-name>/` で編集し、各 client の導入先・展開先は直接編集しない

## 安全原則

- malware、credential 収集、data exfiltration、unauthorized access を助ける skill は作らない
- ユーザーに見える目的と実際の挙動がずれる誤解を招く（misleading な）skill は作らない
- 外部サービスや network access が必要な場合は、`compatibility` や導入手順で前提を明示する
- secret、token、個人情報をテンプレートや example に埋め込まない

## ファイル分割ルール

### `SKILL.md` に書くもの

- この skill を使った作業の成果物が満たす条件と、境界で守ること（`## 検証`）。skill 自体の構成は「完了チェック」で見る

`SKILL.md` は入口に徹する。

- 長い背景説明や細かな判断条件は書き込まない
- 外部参照は 1 段深さに留める
- 500 行未満を維持する前提で圧縮する
- 目安として 5000 token 未満に収め、毎回読むべき中核手順だけを置く
- 毎回使う短い手順（目安 10 行）は `references/` に逃がさない。SKILL.md に残す
- 詳細資料へのリンクには「いつ読むか」を添える
- skill は単体で成立させる。他 skill の手順を写し込まない。読ませないと動かない形にしない

### `references/` に書くもの

- リポジトリ全体に効く横断方針を置くトップレベル `rules/` とは役割を分ける
- skill ローカルの判断観点や個別ルール本文は、原則としてその skill 配下の `references/` に置く
- `references/` 配下の下位構成は skill ごとに決めてよく、必要な場合だけ `references/rules/` のようなディレクトリを切る
- 1 つの reference が 300 行を超える場合は、冒頭に読み方や目次を置く
- 複数 domain、framework、tool を扱う場合は、`references/aws.md`、`references/gcp.md` のように variant ごとのファイルへ分ける

### `assets/` に書くもの

- 章を省略せず使える形にする
- 具体的なプロジェクト判断は埋め込まない
- `draft` でそのまま流用できる形にする

### `scripts/` に書くもの

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

- 追加するなら、何を実行する script かを `SKILL.md` と `references/` で明示する
- 依存関係、起動方法、期待結果、失敗時の扱いを書く
- Python を使う場合でも、必要性があるときだけに限る
- `mise` や `uv` はプロジェクトの運用に合う場合だけ採用し、skill の必須前提にはしない

Python を使うときの目安:

- まずは標準ライブラリだけで足りるかを見る

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

### client-specific field の扱い

Agent Skills 標準にない field は、利用先 client の拡張として扱う。

- file scoping 用 field（例: `paths`、legacy の `globs`）は、その client が対応していると分かる場合だけ使う
- slash command 的に明示実行だけへ寄せる field（例: `disable-model-invocation`）は、その client が対応していると分かる場合だけ使う
- 合議調査（consensus-investigation）のように複数のサブエージェントを起動する重い skill は、勝手に発火させず明示呼び出しに寄せる
- skill の標準テンプレートへ client-specific field を常設しない。`disable-model-invocation` もテンプレに常設しない
- client-specific field を入れる場合は、`compatibility` や `metadata` で前提を補足するか、利用先 project の導入手順に寄せる

## 反復ループ

止めどき:

- 主要な test prompt で期待する流れが安定している
- 同じ修正を何度も繰り返していない
- `SKILL.md` を重くしすぎずに改善できている
- 追加した rule や template が個別例に過剰適合していない

反復中の見方:

- 指示が増えすぎたら、効いていない指示を削る
- 重要な制約は命令だけで押し切らず、なぜ必要かを短く説明する
- test prompt 間で同じ準備や helper 作成が繰り返されるなら、`assets/` や `scripts/` へ移す価値を検討する

eval / benchmark の扱い:

- 通常の skill 作成では、2〜3 件の test prompt と人手レビューで足りることが多い
- 客観的な期待値を持つ task では、必要に応じて `evals/` や JSON の期待条件を追加してよい
- baseline 比較、複数回実行、pass rate、token、実行時間の集計は optional advanced として扱う
- eval / benchmark の仕組みを入れる場合も、通常 workflow の利用者に毎回実行を強制しない

## test prompt の作り方

観点の候補例:

- 典型ケース: skill の中核機能が素直に必要な依頼
- 境界ケース: 情報不足、曖昧さ、分岐が出る依頼
- 近接ケース: 関連はするが、skill の適用範囲を見極めたい依頼

この 3 分類に固定する必要はない。skill に応じて、確認質問の質、出力モードの違い、対象スコープの曖昧さなど、別の軸で組んでよい。

避けたい例:

- 1 行で終わる不自然に短い依頼

test prompt の下書きには [../assets/test-prompt-template.md](../assets/test-prompt-template.md) を使ってよい。

## 既存 skill の改稿方針

1. `SKILL.md` に長い判断知識が入り込んでいないかを見る。毎回使う短い手順まで逃がしていないかも見る。
2. 判断基準や分類ロジックを `references/` へ逃がす。他 skill に依存させない。この skill だけで追えるようにする。
3. 迷ったら足さず削る。使われていない指示、重複した指示、過度に狭い MUST を削る。
4. 学びの書き戻し先はこの skill。他ツールの skill 作成手順に渡さない。

改稿時に避けること:

- 1 つの test prompt だけに合わせて、他の依頼で不自然になる修正
- `SKILL.md` に詳細な例外や背景を積み上げる修正
- 毎回使う短い手順を `references/` だけに置く修正
- 他 skill を読ませないと動かない修正、または他 skill の手順を丸ごと写す修正
- 近接 skill との境界を曖昧にする広すぎる description
- script 化すべき繰り返し処理を、長い文章指示だけで押し切る修正

## description の trigger 品質チェック

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

## 出力モードごとの期待

### `review`

- 本文全体はまだ出さない

### `draft`

- `SKILL.md`、`references/`、`assets/` の順で返す
- テンプレートの章は省略しない

### `write-file`

- 保存先が明示されていない場合は `write-file` に入らず、`draft` にフォールバックする

## 応答時の明示事項

対象が未指定のとき:

- まず skill 名、用途、保存先のどれを先に決めるか確認する短い質問だけを返す

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
- 毎回使う短い手順は `SKILL.md` に残している
- 迷ったら足さず削っている。この skill だけで成立し、他 skill の手順を写していない
- `SKILL.md` の `## 検証` は、この skill を使った作業の成果物と境界の項目だけで、skill 自体の構成の確認を含めていない
- 詳細参照には、そのファイルをいつ読むかが書かれている
- unsafe / 誤解を招く（misleading な）skill を作らない安全原則が守られている
- テンプレートは `assets/` にあり、`draft` の起点にできる
- `scripts/` は必要性があるときだけ追加している
- 必要なら 2〜3 件の test prompt で trigger、出力、確認質問の妥当性を試している
- eval / benchmark は必要な skill にだけ任意追加し、通常 workflow に必須化していない
- client-specific field を標準 field と混同していない
- 用語が一貫している
- トップレベル `rules/` と skill 配下の `references/` の役割がドキュメント上で混同されていない
