# エージェント作業のローカル記録を `memory/` に置き、Git 管理しない

## ステータス

採用済み (2026-08-21)

## 背景

`rules/documentation-standards.md` は、バージョン管理外の作業領域と、そこから正式ドキュメントへの昇格パスを持っていた。一方で置き場の名前は `work-ai/` や `.scratch/` など例示のままで、エージェントが申し送りや失敗の学びを残す場所が固定されていなかった。

候補は次だった。

- 既存の `.local/` の下に置く
- 例示どおり `work-ai/` や `.scratch/` を採用する
- リポジトリ直下に `memory/` を新設する
- planner など個別 skill の手順に寄せる
- Claude Code Auto Memory（`~/.claude/projects/.../memory/`）に任せる

## 判断

リポジトリ直下の `memory/` を、AI エージェント作業全般のローカル記録とする。

- 中身は共有の正本ではない。`.gitignore` でディレクトリごと除外し、`.gitkeep` は置かない
- 運用ルールは毎回読む `AGENTS.md` に書く。雛形と詳細判断は `rules/working-memory.md` に置く
- planner を含む個別 skill には手順を足さない
- Claude Code Auto Memory とは混ぜない。repo 直下の `memory/` はツール非依存の作業領域とする
- 利用先リポジトリへはこの運用を自動展開しない。`rules/` は APM の配布対象ではない

`.local/` はツールのローカル上書き向けで、作業記録の置き場としては意味が分かりにくい。`work-ai/` や `.scratch/` は一時領域のニュアンスが強く、学びや申し送りが残りにくい。個別 skill に寄せると plan 以外の作業で抜け、同じ手順が複製される。

中身を 3 系統に分ける。

- `memory/lessons.md` — 同じ過ちを繰り返さない学び
- `memory/handoff.md` — 進行中作業の申し送り
- `memory/notes/` — 作業用メモ

## 影響

メリット:

- 置き場が固定され、セッションをまたいで学びと申し送りを読める
- Git を汚さず、秘密情報や未確定メモが共有履歴に入りにくい
- 運用は `AGENTS.md`、詳細は `rules/` に分かれ、個別 skill を肥大させない

デメリット:

- クローン直後は `memory/` が無い。作業開始時に作り直す
- ローカル記録なので、他マシンや他作業者には見えない
- `AGENTS.md` に運用を足す分、always-on の文量が増える

影響:

- チーム運用に効く知見は `memory/` に溜めず、`rules/`、`specs/`、`decisions/`、`skills/` へ昇格する
- Issue / PR から `memory/` 内のパスを唯一の参照にしない
- gitignore skill は `memory/` 用の custom block を再利用できる

## 関連する DR

- 関連: [0005-rules-and-specs-boundaries.md](0005-rules-and-specs-boundaries.md)
