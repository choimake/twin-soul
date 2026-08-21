# `rules` をリポジトリ横断方針の正本とし、`specs` を現在仕様の参照先にする

## ステータス

採用済み (2026-05-10)

## 背景

`decisions/0001-document-boundaries.md` では、`skills/` を外部展開単位、`specs/` と `decisions/` を `twin-soul` 内部ドキュメントとして扱う方針を決めた。一方で、`rules/` は位置づけを確定せず、当面は外部展開の主役として扱わない状態にしていた。

その後、APM 移行により `skill` の配布対象は `skills/` に明確化された。`decisions/0004-use-apm-for-shared-skill-distribution.md` でも、旧 `sync.sh` が担っていた `rules/` シンボリックリンクと入口ドキュメント生成は APM 配布とは別に整理する必要があると記録している。

実際にはトップレベル `rules/` にリポジトリ横断方針が集まり、`.cursor/rules/` と `.claude/rules/` には旧同期方式のシンボリックリンクが残っていた。複数の `rules` 置き場があると、どれが正本か分からず、更新漏れや参照ずれが起きる。

## 判断

`twin-soul` では、ドキュメントと `rules` の境界を次のように扱う。

- `rules/` はリポジトリ横断で守る方針、チェックリスト、禁止・推奨事項の正本とする
- `.cursor/rules/` と `.claude/rules/` は使わず、旧同期方式のシンボリックリンクは削除する
- `specs/` は `twin-soul` の現在の構成、導入方法、運用仕様を説明する参照先とする
- `decisions/` は判断理由と方針変更の履歴を残す場所とする
- 外部プロジェクトへ配布する資産の主役は引き続き `skills/` とする

`rules/` を外部プロジェクトへ配布したくなった場合は、APM 指示ドキュメントなどの配布単位として別途設計し、`specs/` と `decisions/` を更新する。

## 影響

メリット:

- リポジトリ横断方針の正本がトップレベル `rules/` に一本化される
- `.cursor/rules/` と `.claude/rules/` の同期ずれを防げる
- `rules/` と `specs/` の役割が、「守ること」と「現在どうなっているか」に分かれる
- `skill` の外部配布範囲が `skills/` に保たれる

デメリット:

- Cursor / Claude Code の実行環境別の `rules` ディレクトリを前提にした運用は使わない
- 将来 `rules` を外部配布したくなった場合は、APM 指示ドキュメントなどの設計を追加する必要がある

影響:

- `COMMON.md`、`README.md`、`CONTRIBUTING.md` はトップレベル `rules/` を正本として案内する
- `specs/document-boundaries.md` は `rules/`、`specs/`、`decisions/` の日常的な判定基準を持つ
- `.cursor/rules/` と `.claude/rules/` は削除し、再生成されても Git 管理しない

## 関連する DR

- 置き換え元（rules 部分）: [0001-document-boundaries.md](0001-document-boundaries.md)
- 関連: [0004-use-apm-for-shared-skill-distribution.md](0004-use-apm-for-shared-skill-distribution.md)
