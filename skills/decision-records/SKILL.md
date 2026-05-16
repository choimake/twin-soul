---
name: decision-records
description: >-
  Decision Record (DR) や ADR の新規追加、更新、supersede 判断、下書き作成を整理する。判断記録、設計判断の履歴、方針変更の記録、`decisions/` への追記、既存 DR の更新方針整理が必要なときに使う。更新か新規追加か迷う依頼、accepted な DR を書き換えたい依頼、テンプレートに沿った DR 本文が欲しい依頼でも参照する。
---

# Decision Records

## 目的

Accepted DR を直接変更しない。意味が変わるなら新規追加して supersede。判断の履歴を壊さないことが最優先。

## 使う場面

- 新規 DR / ADR 追加時
- 既存 DR の直接更新か新規追加かの整理時
- supersede 要否の判断時
- テンプレートに沿った DR 本文の下書き作成時
- 設計判断メモ・方針変更履歴の整理時

## 手順

1. 対象 DR・保管ディレクトリ・論点を特定。一意でなければ `@path` やテーマを確認。
2. 方針確認・下書き作成・実ファイル更新のいずれかを判定。`review` / `draft` / `write-file` が明示されていれば優先。
3. 論点に関係する既存 DR だけ確認。全件読了不要。
4. 更新依頼なら軽微修正か意味変更かを判定。意味変更なら既存 Accepted DR を直接変更せず新規 DR を追加して supersede。
5. `draft` / `write-file` では [assets/dr-template.md](assets/dr-template.md) を起点に本文を組み立て。章を省略しない。
6. `review`→判断と進め方のみ返す。`draft`→短い要約後に本文全体を返す。`write-file`→保存先が明示された場合のみ実行。

詳細判断と応答ルールは [references/dr-knowledge.md](references/dr-knowledge.md) を参照。

## 期待する出力

- 新規追加か更新か、更新なら直接更新か supersede かの判断
- 関連 DR の扱い整理
- テンプレートに沿った新規作成・更新方針、または file-ready な DR 下書き
