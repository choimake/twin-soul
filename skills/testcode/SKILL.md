---
name: testcode
description: >-
  テストコードの新規作成、既存テストの追加・改善、生成済みテストの評価を扱う。ユニットテストを書きたい、既存テストや提案されたテストを見直したい、coverage や mutation testing、test smell の観点で弱い点を洗い出したいときに使う。
---

# Testcode

## 目的

Coverage は手段、品質は Mutation Testing・Assertion 強度・Test Smell で測る。Coverage 達成を目標と混同しない。

## 使う場面

- 新規ユニットテスト・テストケース作成時
- 既存テストの coverage・assertion・edge case の見直し時
- 生成済みテストの品質評価・採用判断時
- surviving mutant・弱い assertion・test smell 起点の追加ケース検討時

## 手順

1. 対象コード・対象テスト・言語・テストフレームワーク・保存先の有無を確認。曖昧なら `@path` や用途を確認。
2. `generate` / `evaluate` / `improve` を判定。未指定なら新規作成→`generate`、品質確認→`evaluate`、改善提案→`improve`。
3. 対象ファイルと判断に必要な最小限の関連コードだけ読む。公開 API・分岐・例外・既存テストの有無を先に押さえる。
4. 期待動作とケース一覧を整理してから本文に入る。正常系・境界値・異常系・環境依存を分ける。
5. `generate`→ケース一覧をもとに file-ready なテスト案を作成。`evaluate`→実行可否・assertion の質・edge case・外部依存・coverage 偏重の有無を確認。`improve`→弱い assertion・surviving mutant・test smell を起点に追加・修正案を返す。
6. mutation testing や自動評価が未導入でも必要性と導入順を分けて返す。coverage だけで十分と断定しない。

詳細判断と各観点の入口は [references/testcode-knowledge.md](references/testcode-knowledge.md) を参照。必要に応じて `references/` 配下の分割ドキュメントを並列確認。

## 期待する出力

- テスト生成前のケース整理、または file-ready なテストコード案
- 生成済みテストの品質評価と弱い点の理由
- coverage・mutation testing・test smell の使い分けを踏まえた改善提案
- 即対応すべき点と後で導入してよい評価手段の切り分け
