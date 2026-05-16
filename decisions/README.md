# 判断記録

このディレクトリは、`twin-soul` の重要な判断理由と方針変更の履歴を判断記録（DR）として残す。

## 置くもの

- 複数の選択肢から選んだ理由
- 後から「なぜこうしたのか」と聞かれそうな判断
- 後戻りコストが高い方針変更
- `rules/` や `specs/` の意味を変える判断

## 置かないもの

- 現在の運用仕様そのもの（`specs/` に置く）
- 作業時に守るチェックリスト（`rules/` に置く）
- 日々の作業メモや未確定の仮説

## 更新ルール

- 採用済み DR の意味を直接書き換えない
- 方針が変わる場合は新しい DR を追加し、古い DR を置き換え済みにする
- 誤字やリンク修正など、意味が変わらない軽微修正だけ直接編集してよい

## 代表文書

- [0001-document-boundaries.md](0001-document-boundaries.md) - 文書境界の初期判断
- [0004-use-apm-for-shared-skill-distribution.md](0004-use-apm-for-shared-skill-distribution.md) - `skill` 配布基盤を APM に移した判断（現行の root Skill collection 導入は 0008 を参照）
- [0005-rules-and-specs-boundaries.md](0005-rules-and-specs-boundaries.md) - `rules/` と `specs/` の境界確定
- [0007-withdraw-local-gh-agent-write.md](0007-withdraw-local-gh-agent-write.md) - ローカルトークンでエージェントに GitHub 書き込み操作を任せる運用を撤回する判断
- [0008-use-root-skill-collection-for-apm-install.md](0008-use-root-skill-collection-for-apm-install.md) - APM の root Skill collection で全 skill を導入する判断

DR を作るか迷う場合は [../rules/when-to-create-decision-records.md](../rules/when-to-create-decision-records.md) を参照する。
