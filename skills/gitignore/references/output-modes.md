# 出力モード

## `draft`

- 推奨 template 名を先に明示する
- その後に file-ready な `.gitignore` 案を返す
- `mise` のような custom ルールがある場合は、`gitignore.io` 由来 block の後ろに asset 起点の手書き block を足す
- 必要なら「この行は project 固有で手書き追加」と分かるよう区切る

## `write-file`

- 保存先が明示された場合だけ実行する
- 既存ファイルがあるなら全面置換より差分更新を優先する
- `gitignore.io` 由来のブロックと手書きブロックが混ざる場合は、意図が追えるようにコメントを残してよい
- `mise` 用ルールを足す場合は、既存の `mise.toml` を ignore しないことを確認する

## fallback

次の状況では、取得結果より判断の透明性を優先する。

- `gitignore.io` へ接続できない
- 自動推定の結果が OS しか出ず、言語や IDE が絞れない
- template 名が不明で候補が複数ある
- `mise` のように template が存在せず、custom ルールが必要
- リポジトリの手掛かりが弱く、複数スタックがあり得る
- 既存 `.gitignore` のローカルルールが多く、機械的な統合が危険

fallback では次を返す。

- 推奨 template 名の候補
- 必要なら custom 手書きルール
- 追加で確認したいこと
- 手書きで先に入れてよい最小限の ignore 項目
