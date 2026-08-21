# 作業メモリの詳細

このドキュメントは [`../AGENTS.md`](../AGENTS.md) の「作業メモリ」運用を補う。毎回の手順は AGENTS.md を正本とする。ここには雛形、肥大時の切り方、昇格の判断だけを置く。

## 3系統

- `memory/lessons.md` — 同じ過ちを繰り返さない学び。短くキュレーションする
- `memory/handoff.md` — 進行中作業の申し送り。最新状態を保つ。ログではない
- `memory/notes/` — 作業用メモ。日付やタスク名で分割し、必要なときだけ読む

開始時は `lessons.md` と `handoff.md` だけ読む。`notes/` は今回の作業に関係するものだけ追加で読む。

## 雛形

### `memory/lessons.md`

```markdown
# Lessons

- YYYY-MM-DD: [何が起きたか] / [次からどうするか]
```

1 行 1 学びを保つ。経緯の全文は `notes/` へ移す。

### `memory/handoff.md`

```markdown
# Handoff

- 更新: YYYY-MM-DD
- 現状: [完了 / 途中 / 止まっていること]
- 対象ファイル: [パス]
- 判断: [選んだことと理由]
- 検証: [コマンドまたは確認結果]
- 次の一手: [次セッションがすぐ着手できる1手]
- リスク: [確認済みの懸念だけ]
```

必須項目は現状、対象ファイル、判断、検証、次の一手、既知のリスク。会話の全文は書かない。200 行を超えたら「やったこと」を削り、最新状態だけ残す。

### `memory/notes/<日付-または-タスク>.md`

```markdown
# [メモ題名]

- 日付: YYYY-MM-DD
- 目的: [このメモを残す理由]

[調査メモ、試したこと、残課題]
```

## 書かないもの

- 秘密情報
- 会話の全文
- すでに `rules/`、`specs/`、`decisions/`、skill にある内容のコピー
- Issue / PR から辿れない一時パスを、共有ドキュメントの唯一の参照にすること

## 肥大したら

- `lessons.md` と `handoff.md` は索引として短く保つ
- 詳細は `notes/` の topic ファイルへ移す
- 古い申し送りは、次の一手が終わったら消すか 1 行の結果に縮める
- 同じ学びが 3 回以上出たら、正式ドキュメントへ昇格する候補にする

## 昇格

- チーム運用に効く知見は `memory/` に溜めない
- 守る方針は `rules/`、現在仕様は `specs/`、判断理由は `decisions/`、再利用手順は `skills/`
- 昇格したら `memory/` 側は削るか、正式ドキュメントへのリンクだけ残す
- 昇格パスの正本は [documentation-standards.md](documentation-standards.md)

## Claude Auto Memory との違い

- このリポジトリの `memory/` はツール非依存の作業領域
- Claude Code の Auto Memory（`~/.claude/projects/.../memory/`）とは混ぜない
- どちらに書いても、確立した知見の正本は `rules/`、`specs/`、`decisions/`、`skills/`
