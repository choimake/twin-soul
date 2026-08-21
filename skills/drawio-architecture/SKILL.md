---
name: drawio-architecture
description: >-
  事実の正本（yaml 等）に基づき、非圧縮の native draw.io（.drawio）で構成図を描画し、人のスクショで視覚確認する。構成図、アーキテクチャ図、.drawio、draw.io、データ面、制御面、視覚確認、スクショ修正の依頼で使う。事実 SoT のない一般的なフローチャートや UI スケッチは対象外。
compatibility: Optional HTTP MCP at https://mcp.draw.io/mcp. Drawing continues without it.
---

# draw.io 構成図

## 目的

事実の正本に載るものだけをノードとエッジにし、見た目はデザインシステムに揃える。成果物は非圧縮の native draw.io である。

## 使う場面

- 利用先リポジトリの構成図を `.drawio` で新規に描くとき
- 既存の構成図を、スクショを見ながら視覚修正するとき
- 構成図のレビュー（事実と見た目のルールの突合）をするとき
- データ面と制御面を分けて描くとき

対象外である。

- 事実の正本がない一般的なフローチャートや UI スケッチ

## 手順

1. 利用先リポジトリの事実の正本（yaml または同等の一覧）と、出力する `.drawio` のパスを特定する。欠けていれば質問する。正本に無い実リソースは足さない。推測でノードを増やすと、図と運用実態がずれる。
2. 依頼を次のどれかに分類する。新規描画 / 視覚修正 / レビュー。
3. draw.io MCP の有無を見る。無ければ導入手順を案内してから描画へ進む。案内が契約である。入れられるなら入れてもよい。クライアントの有効化や設定ファイルの編集が要るなら案内だけにし、mcp.json は自分で書かない。無理ならアイコンなしで描く。案内文とツールの使い分けは、MCP の有無を見るとき、または stencil を足すときに [references/mcp.md](references/mcp.md) を読む。
4. デザインシステムの定数で、非圧縮の native draw.io XML（`mxfile` + `mxGraphModel`）を書く。余白・色・カード・線の定数は、描く直前に [references/drawio-architecture-knowledge.md](references/drawio-architecture-knowledge.md) を読む。データ面（リクエストと読み書き）と制御面（管理操作）は分ける。1 枚に同居させると回廊が埋まり、左から右の本流が読めなくなる。
5. 公式 stencil を足すときは、MCP の `search_shapes` が返した style だけ使う。ライブラリの shape 名を推測して書くと、公式と一致しない style になる。検索できないときはアイコンなしで進める。視覚確認の周回には stencil 作業を混ぜない。狭いカードへアイコンを足すと文字がさらに潰れる。
6. 完了前に、全体と潰れている箇所の人のスクショを求める。XML の parse や MCP プレビューでは、文字切れと線の重なりは見えない。直すのは座標・ウェイポイント・カード寸法・ラベル位置である。2 周から 3 周で止める。合格条件は、スクショ周回に入る前に [references/visual-qa-checklist.md](references/visual-qa-checklist.md) を読む。

視覚修正でスクショが無いときは、座標を推測しない。重なりは画像を見ないと分からないため、先に画像を求める。

実行補助スクリプトは足さない。描画と視覚確認は手置きとスクショで足りる。

## 期待する出力

- 非圧縮の native draw.io（`.drawio`）
- 使った事実の正本と、出力パスの明示
- MCP が無かった場合は、案内した導入手順。入れたならその結果
- 新規描画・レビューでは、分割した図があるなら概観と制御面の役割分担
- 視覚修正では、直した座標・寸法・ラベル位置の要約。事実の正本は触らない
- スクショ待ち、またはスクショ後の修正結果。MCP preview や XML parse だけでは完了にしない

## 検証

- `name` は親ディレクトリ名 `drawio-architecture` と一致している
- `description` は WHAT と WHEN を含み、一般フローチャートや UI スケッチとの境界が見える
- `SKILL.md` は workflow に留め、デザインシステム・MCP・視覚確認の詳細は `references/` にある
- 参照ファイルには「いつ読むか」がこのドキュメントから分かる
- 公式 stencil は `search_shapes` の結果を使い、失敗時はアイコンなしで進める
- 完了は人のスクショであり、MCP preview や XML parse だけではない
