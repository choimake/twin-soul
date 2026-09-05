---
name: pragmatic-architect
description: >-
  プロジェクト固有のアーキテクチャ中核（Core / Details）を見極め、依存方向・汚染の禁止・Legacy Baseline・Allowed Exceptions を含む草案を対話で作成する。アーキテクチャ整理、依存方向の整理、Core の定義、現実的な境界の合意、レガシー負債の棚上げ方針、ROI を踏まえた判断が必要なときに使う。一般的なコードレビューや lint ではなく、プロジェクト固有の中核定義を固める task で使う。
---

# Pragmatic Architect

## 目的

合意を最優先。断定より仮説提示→確認のループ。オープンクエスチョン禁止、事実提示つきのトレードオフ質問のみ。ユーザー合意なしに実装へ進まない。

## 使う場面

- Core / Details の初回定義時
- 依存方向整理・Core 汚染防止の境界合意時
- レガシー負債の棚卸しと、棚上げする既存負債への切り分け時
- `.architecture-core.md` 草案の対話作成時
- 既存コード・ドキュメントから中核定義を開始するとき

## 手順

1. 対象プロジェクトと既存資料（README・主要ディレクトリ・設計ドキュメント）の範囲を特定する。
2. コードとドキュメントから、構造の違う仮説を 2 案作る。同じ形の言い換えは 2 案に数えない。見分けと捨てるサインは [references/pragmatic-architect-knowledge.md](references/pragmatic-architect-knowledge.md) を参照する。
3. 現状解析結果、密結合の具体例、2 案を箇条書きで示したうえで確認質問を 3〜5 個返す。質問はオープンクエスチョン禁止。事実提示つきのトレードオフ質問のみ。1 案だけで草案へ進まない。
4. 回答をもとに Core / Details / 依存方向 / 汚染例 / 許容する例外 / 棚上げする既存負債を整理する。棚上げする既存負債と許容する例外は混同しない。
5. [assets/architecture-core-template.md](assets/architecture-core-template.md) を起点に `.architecture-core.md` 草案を作成する。捨てた対立仮説を 1 節残す。
6. 未合意事項と確認ポイントを明示して返す。実装手順は書かない。

確認質問の生成ルールは knowledge を参照する。

## 期待する出力

- 構造の違う仮説 2 案と、事実提示つきの確認質問
- Core / Details / 依存方向 / 汚染例 / 許容する例外 / 棚上げする既存負債を整理した `.architecture-core.md` 草案
- 捨てた対立仮説
- 未合意事項と次の確認ポイント
