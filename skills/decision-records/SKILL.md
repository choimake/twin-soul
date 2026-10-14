---
name: decision-records
description: >-
  Decision Record (DR) や ADR の新規追加、更新、supersede 判断、下書き作成を整理する。判断記録、設計判断の履歴、方針変更の記録、`decisions/` への追記、既存 DR の更新方針整理が必要なときに使う。更新か新規追加か迷う依頼、accepted な DR を書き換えたい依頼、テンプレートに沿った DR 本文が欲しい依頼でも参照する。
---

# Decision Records

## 目的

Accepted DR を直接変更しない。意味が変わるなら新規追加し、全体を変えるなら supersede、一部だけ変えるなら一部変更にする。判断の履歴を壊さないことが最優先。

## 使う場面

- 新規 DR / ADR 追加時
- 既存 DR の直接更新か新規追加かの整理時
- supersede 要否の判断時
- テンプレートに沿った DR 本文の下書き作成時
- 設計判断メモ・方針変更履歴の整理時

## 前提

リポジトリのルートの `.decision-records.md` に、DR の保管先と、DR を作る基準を書いておく。基準がリンクなら、その文書も読む。

ファイルが無いか、どちらかの節が雛形のままなら、DR の作業はしない。新規作成も、既存 DR の更新や誤字修正もしない。代わりに次だけ行って終える。

- ファイルが無ければ、[assets/decision-records-config.md](assets/decision-records-config.md) を `.decision-records.md` としてルートに置いてよいか聞き、了承されたらコピーする。既にあれば触らない
- 2 つの節を埋めるよう伝える。中身は埋めない

## 手順

1. `.decision-records.md` を読む。対象 DR・論点を特定。一意でなければ `@path` やテーマを確認。
2. 方針確認・下書き作成・実ファイル更新のいずれかを判定。`review` / `draft` / `write-file` が明示されていれば優先。
3. 論点に関係する既存 DR だけ確認。全件読了不要。新しい判断を記録するかは、`.decision-records.md` の基準で決める。
4. 更新依頼なら軽微修正か意味変更かを判定。意味変更なら既存 Accepted DR を直接変更せず新規 DR を追加する。判断全体を変えるなら supersede、一部だけ変えるなら一部変更。一部変更が重なって判断の大半が上書きされるなら、まとめた DR で supersede。意思決定に効いていない値だけの変更なら DR を足さない。Proposed の DR は直接書き換えてよく、ステータスは採否が決まるまで Proposed のまま。
5. `draft` / `write-file` では [assets/dr-template.md](assets/dr-template.md) を起点に本文を組み立て。章を省略しない。
6. `review`→判断と進め方のみ返す。`draft`→短い要約後に本文全体を返す。`write-file`→保存先が明示された場合のみ実行。

詳細判断と応答ルールは [references/dr-knowledge.md](references/dr-knowledge.md) を参照。

## 期待する出力

- 新規追加か更新か、更新なら直接更新か supersede か一部変更かの判断
- 関連 DR の扱い整理
- テンプレートに沿った新規作成・更新方針、または file-ready な DR 下書き
