# [Skill Title] 判断知識

この資料は `[skill-name]` skill の判断知識をまとめたものである。`SKILL.md` は使い方に留め、詳細判断はこの資料とテンプレートを起点にする。

テンプレート:

- [../assets/[template-file].md](../assets/[template-file].md)

## この skill の役割

- [その skill が担う役割]
- [何を `SKILL.md` に残し、何を外へ逃がすか]

## 呼び出し側が渡せる入力

- [対象の `@path`]
- [出力モード]
- [論点やキーワード]
- [保存先]

未指定なら、この skill が会話から妥当な既定値を判断する。必要最低限の確認だけを追加する。

## 意図確認

- [会話履歴から拾うべき手順、修正指摘、入出力形式]
- [ユーザーに確認すべき trigger 条件、期待出力、対象外]
- [test prompt が必要な条件]

## 安全原則

- [ユーザー意図と異なる誤解を招く（misleading な）挙動を避ける]
- [不正利用、secret 埋め込み、data exfiltration を助けない]
- [外部依存や network access が必要な場合の明示方法]

## 対象と探索の絞り方

1. [対象指定がある場合の扱い]
2. [出力モード指定がある場合の扱い]
3. [曖昧な場合の確認事項]
4. [最小スコープで読む方針]

## skill package と frontmatter

- [skill の配布・導入単位]
- [`name` と親ディレクトリ名の一致]
- [`description` の trigger / boundary 方針]
- [必要な任意 field: `license` / `compatibility` / `metadata`]
- [client-specific field を使う条件]
- [標準 field と client-specific field を混同しないための注意]

## ファイル分割ルール

### `SKILL.md`

- [目的 / 使う場面 / 手順 / 期待する出力 / 検証 を置く]
- [入口として薄く保つ。毎回使う短い手順はここに残す]
- [他 skill の手順は写さず、パスを渡す]
- [詳細参照をいつ読むかを書く]

### `references/`

- [判断基準]
- [fallback]
- [レビュー観点]
- [description の trigger 品質チェック]
- [長い reference の読み方や目次]
- [複数 domain / framework を扱う場合の variant 分割]

### `assets/`

- [テンプレート]
- [再利用する章立て]

### `scripts/`

- [昇格させる条件]
- [まだ手作業のままでよい条件]
- [依存関係や実行方法の書き方]

## progressive disclosure

- [最初に `description` だけで拾わせる情報]
- [`SKILL.md` に毎回読むべき中核手順として置く情報]
- [`references/` や `assets/` に逃がす情報]
- [参照ファイルを読む条件]
- [大きすぎる `SKILL.md` を分割する判断]

## description 評価

- [should-trigger prompt]
- [should-not-trigger prompt]
- [near miss prompt]
- [undertrigger を避ける具体文脈]
- [overtrigger を避ける境界]
- [overfitting を避ける見方]

## 改善ループ

- [少数の test prompt で見る観点]
- [個別例に過適合しないための判断]
- [迷ったら足さず削る判断]
- [重要な指示に理由を添える判断]
- [eval / benchmark を任意追加する条件]

## 出力モードごとの期待

### `review`

- [判断と進め方だけを返す]

### `draft`

- [要約の後に file-ready な本文を返す]

### `write-file`

- [保存先が明示されたときだけファイル更新する]

## 応答時の明示事項

- [対象未指定時の確認質問]
- [最小スコープで進める宣言]
- [必要なら scripts を追加しない理由]
