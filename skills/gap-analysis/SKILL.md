---
name: gap-analysis
description: >-
  PRD（または同等の要求一覧）と検証・調査結果を突き合わせ、実現可否と根拠を表形式でまとめる Gap 分析を行う。Gap 分析表、実現可否、検証結果、PRD 要件の充足確認、スパイク結果の整理時に使う。バックログアイテムの起票そのもの、実装手順や変更ファイル一覧を主とする plan ファイルの作成は対象外。
---

# Gap 分析

## 目的

PRD 上の要求と、実測・調査で得た証拠を対応づけ、判定凡例に沿った実現可否と制限・代替を一文書に収束させる。他の Agent Skill を前提としない。

## 使う場面

- PRD 要件と検証（スパイク・PoC・試験環境での確認）結果を突き合わせたいとき
- 「可 / 条件付き可 / 不可」をステークホルダと合意したいとき
- 前提ドキュメント・検証環境・期間を残したいとき（表紙メタ）

## 手順

1. 対象を特定する。既存の Gap 分析 Markdown の `@path` があれば優先、無ければ新規作成として扱う。
2. 出力モードを判定する。`review` / `draft` / `write-file` が明示されていれば優先。未指定なら、既存パスあり→`review`、無し→`draft`。
3. 対象 PRD（または要件リスト）、検証・調査の範囲・日付・環境を確定する。不足なら最小限の質問のみ。別 skill の実行を求めない。
4. [assets/gap-analysis-template.md](assets/gap-analysis-template.md) を起点に、要件をグループ見出し・連番 ID・短いラベル見出しのいずれで区切ってもよい形で本文を組み立てる。入力に要件 ID が無ければ新規に付与しない。
5. 各要件について、PRD 上の記述、実現可否（凡例）、根拠・実証内容、制限事項、代替案・回避策、PRD 仕様変更案を埋める。1 件だけ詳しく書く場合は [assets/requirement-row-template.md](assets/requirement-row-template.md) を参照。
6. サマリ表で一覧化し、必要なら「今後の検討事項」を追記する。
7. `write-file` は、保存先パスがユーザーから明示されたときのみそのパスへ書き込む。未指定なら `draft` で本文を返す。

判定の細部・品質チェック・出力モードの差分は [references/gap-analysis-knowledge.md](references/gap-analysis-knowledge.md) を参照する。

## 期待する出力

- Gap 分析表（Markdown）：表紙メタ、判定凡例、任意の共通前提、要件ごとの表、サマリ、任意の今後の検討
- `review` 時は構成の妥当性・不足列・証拠の欠落の指摘
- `draft` / `write-file` 時は上記構造に沿った本文

## 検証

- `SKILL.md` は workflow のみに留め、詳細判断は `references/gap-analysis-knowledge.md` に分離している
- テンプレートは `assets/` にあり、`draft` / `write-file` の起点にできる
- `description` は WHAT と WHEN を含み、対象外（バックログ起票本体・実装 plan 専用）の境界が読み取れる
- 対象や入力が不明なときの扱い（最小限の確認質問のみ返す）が `references/` で明確になっている
