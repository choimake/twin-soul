---
name: pragmatic-architect
description: >-
  プロジェクト固有のアーキテクチャ中核（Core / Details）を見極め、依存方向・汚染の禁止・Legacy Baseline・Allowed Exceptions を含む草案を対話で作成する。アーキテクチャ整理、依存方向の整理、Core の定義、現実的な境界の合意、レガシー負債の棚上げ方針、ROI を踏まえた判断が必要なときに使う。一般的なコードレビューや lint ではなく、プロジェクト固有の中核定義を固める task で使う。
---

# Pragmatic Architect

## 目的

合意を最優先。断定より仮説提示→確認のループ。オープンクエスチョン禁止、事実提示つきのトレードオフ質問のみ。

## 使う場面

- Core / Details の初回定義時
- 依存方向整理・Core 汚染防止の境界合意時
- レガシー負債の棚卸しと Legacy Baseline への切り分け時
- `.architecture-core.md` 草案の対話作成時
- 既存コード・文書から中核定義を開始するとき

## 手順

1. 対象プロジェクトと既存資料（README・主要ディレクトリ・設計文書）の範囲を特定。
2. コードとドキュメントから Core / Details / 依存方向の仮説を作成。
3. 現状解析結果と密結合の具体例を箇条書きで示したうえで確認質問を 3〜5 個返す。質問はオープンクエスチョン禁止。事実提示つきのトレードオフ質問のみ。
4. 回答をもとに Core / Details / Dependency Direction / Contamination Examples / Allowed Exceptions / Legacy Baseline を整理。Legacy Baseline（既存負債の棚上げ）と Allowed Exceptions（合意済み例外）は混同しない。
5. [assets/architecture-core-template.md](assets/architecture-core-template.md) を起点に `.architecture-core.md` 草案を作成。
6. 未合意事項と確認ポイントを明示して返す。

確認質問の生成ルールは [references/pragmatic-architect-knowledge.md](references/pragmatic-architect-knowledge.md) を参照。

## 期待する出力

- 現状解析の証拠に基づく仮説と事実提示つきの確認質問
- Core / Details / Dependency Direction / Contamination Examples / Allowed Exceptions / Legacy Baseline を整理した `.architecture-core.md` 草案
- 未合意事項と次の確認ポイント
