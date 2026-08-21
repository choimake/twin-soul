# Rules

このディレクトリは、`twin-soul` で作業するときに守るリポジトリ横断の方針を置く。

## 置くもの

- 作業時の禁止・推奨事項
- レビューや変更時のチェックリスト
- 複数の skill や文書にまたがって効く運用ルール

## 置かないもの

- 現在の構成や配布仕様の説明（`specs/` に置く）
- 判断理由や方針変更の履歴（`decisions/` に置く）
- skill 固有の詳細知識（各 `skills/<skill-name>/references/` に置く）

## 代表文書

- [documentation-standards.md](documentation-standards.md) - ドキュメント全体の構造と昇格パス
- [working-memory.md](working-memory.md) - 作業メモリの雛形と詳細判断
- [document-consistency.md](document-consistency.md) - コード変更とドキュメント更新の同期
- [version-pinning.md](version-pinning.md) - tool・依存・イメージのバージョン pin 方針
- [github-pr-workflow.md](github-pr-workflow.md) - PR 本文はテンプレートに従う
- [github-issue-workflow.md](github-issue-workflow.md) - Issue 作成とスコープ変更時の運用
- [when-to-create-decision-records.md](when-to-create-decision-records.md) - DR を作る判断基準
- [bash-safety.md](bash-safety.md) - Bash コマンド安全性の判断基準
- [worktree-workflow.md](worktree-workflow.md) - 変更作業は `.worktrees/` で行い、hook が main 編集を止める

## 迷ったとき

「作業者が守るべきこと」なら `rules/` に置く。「今どう構成されているか」なら `specs/` に置く。「なぜそう決めたか」なら `decisions/` に置く。

例外がなく、許可か拒否かではっきり分かれて安く判定でき、繰り返して破られた禁止だけ hook に移す。判断が要る本文はここに残す。

詳細な境界は [../specs/document-boundaries.md](../specs/document-boundaries.md) を参照する。
