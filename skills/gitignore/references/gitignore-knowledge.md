# Gitignore 判断知識

この資料は `gitignore` skill の判断知識 hub である。`SKILL.md` は入口に留め、詳細判断はこの資料から必要な reference だけを読む。

テンプレート:

- [../assets/review-output-template.md](../assets/review-output-template.md)
- [../assets/test-prompts.md](../assets/test-prompts.md)

## この skill の役割

- `.gitignore` の新規作成、既存ファイルの見直し、template 選定を一貫して扱う
- `gitignore.io` 由来 block と custom 手書き block の境界を保つ
- リポジトリの手掛かりから template 候補を推定し、過不足のない ignore 構成を提案する

## 入力として受け取れるもの

呼び出し側は、必要に応じて次を渡せる。

- 対象リポジトリ や `@path`
- 明示された技術スタック、OS、IDE、ツール
- 既存 `.gitignore` の有無
- `review` / `draft` / `write-file`
- 保存先のファイルパス
- 既存の手書きルールを保持したいかどうか

未指定なら、会話とリポジトリの手掛かりから妥当な既定値を判断する。足りない情報だけを短く確認する。

## 出力モードの既定値

- 既存 `.gitignore` がある場合の見直しは `review`
- `.gitignore` がなく、新規作成の相談は `draft`
- 保存先が明示され、実ファイル更新を求められた場合だけ `write-file`

構成判断と本文案の両方を求められている場合は `draft` を優先する。

## 情報源の優先順位

template 候補は次の順で決める。

1. ユーザーが明示した技術スタック、OS、IDE
2. リポジトリ内の手掛かり
3. helper script の自動推定結果
4. 足りないときの確認質問
5. よくある補助 template の提案

リポジトリ内の手掛かりは、判断に必要な最小限だけ読む。

## 読み方

| タイミング | 読む file |
|---|---|
| template 選定 | [template-selection.md](template-selection.md) |
| リポジトリ探索・自動推定 | [auto-detection.md](auto-detection.md) |
| mise 等 custom ルール | [custom-rules.md](custom-rules.md) |
| 既存 file 更新 | [existing-gitignore.md](existing-gitignore.md) |
| draft / write-file / fallback | [output-modes.md](output-modes.md) |
| script 実行 | [helper-script.md](helper-script.md) |

## レビュールールの適用順序

`references/rules/` 配下を **ファイル名の辞書順** で適用する。

1. `avoid-unrelated-templates.md`
2. `match-repo-artifacts.md`
3. `mise-shared-config-not-ignored.md`
4. `preserve-handwritten-rules.md`
5. `protect-shared-env-examples.md`

各ルールは個別に評価し、違反があれば 優先度（重大 / 提案 / 任意）付きで指摘する。優先度の詳細は各 rule file の「指摘する基準」を参照。

## 出力モードごとの期待

### `review`

- 既存 `.gitignore` を読み、`references/rules/` のルールを適用する
- レビュー結果を [../assets/review-output-template.md](../assets/review-output-template.md) の形式で返す
- 重大指摘があれば修正を促し、無ければ「レビュー合格」を明示する

### `draft`

- 推奨 template 名と file-ready な `.gitignore` 案を返す
- 下書き完成後、自動的に `references/rules/` で品質チェックし、結果を添える
- 重大指摘があれば、下書きを修正して再レビューする（最大 2 回）

### `write-file`

- `draft` と同じ手順で `.gitignore` を生成する
- 保存先が明示されていれば、そのパスに保存する
- 保存前に rules レビュー合格を確認する
- 保存後、保存先パスとレビュー結果を報告する
