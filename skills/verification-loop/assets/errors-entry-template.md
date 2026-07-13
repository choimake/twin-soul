# errors.md エントリ

`errors_path`（既定 `.verification-loop/errors.md`）へ追記するとき、次の形を使う。試行が 2 回以上の場合のみ追記する。

```md
## YYYY-MM-DD

- **タスク種別**: [例: ドキュメント実装 / 設定追加 / 機能実装]
- **エラー種別**: [hallucination / format_error / context_drift / tool_failure / その他]
- **状況**: [1行で何が起きたか]
- **適用した対策**: [次の同種タスクの実装指示へ注入する対策]
- **状態**: 未解消 / 対策の定着を監視中
- **recurred**: true / false
```

運用:

- 「状態: 未解消」または「状態: 対策の定着を監視中」のエントリだけを残す
- 解消済み（教訓をルール・退行検知テストへ移したあと）のエントリは追記タイミングで削除する
- 同種エラーが過去にあれば `recurred: true`
