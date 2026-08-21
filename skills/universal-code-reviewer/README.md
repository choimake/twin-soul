# Universal Code Reviewer

`universal-code-reviewer` は、コードレビュー時の汎用チェック観点をそろえ、スコープを絞ったまま一貫した指摘を返すための skill である。

## 概要

- `@path` を起点にレビュー対象を絞る
- `references/rules/` 配下の観点を順番に適用する
- ルール名と優先度が分かる形で指摘を返す
- 必要な場合だけ追加で見たいファイルを提案する

## なぜ必要か

- レビュー観点を毎回ばらつかせず、同じ基準で確認できる
- 対象範囲を明示し、不要に大きなレビューへ広げにくい
- 指摘の根拠となるルールを追いやすい

## はじめ方

前提:

- `skills/universal-code-reviewer/` 配下のファイルを参照できること
- レビュー対象の `@path`、または PR / 差分などの対象範囲が分かること

`/universal-code-reviewer` で呼び出して使う。

依頼例:

```text
/universal-code-reviewer @app/workflow/ をレビューして
/universal-code-reviewer この PR の変更を見て
/universal-code-reviewer デッドコードとコメントの整合性をチェックして
```

`@path` がある場合はその範囲を優先する。`差分だけ` のような明示がない限り、勝手に diff review へ寄せない。

期待する結果:

- 重要度順のレビュー指摘が返る
- どのルールに基づく指摘か分かる
- 追加で読むべきファイルがある場合だけ提案される

## サポート

- Skill 本体: [`SKILL.md`](SKILL.md)
- 判断基準と出力方針: [`references/universal-code-reviewer-knowledge.md`](references/universal-code-reviewer-knowledge.md)
- レビュー時の骨格: [`assets/review-output-template.md`](assets/review-output-template.md)
- 個別ルール: [`references/rules/`](references/rules/)

この skill では、個別ルールの本文を `references/rules/` に置く。これは skill の下位構成であり、トップレベル `rules/` のようなリポジトリ横断方針とは別物として扱う。
