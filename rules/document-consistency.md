# ドキュメント整合性の維持

## 目的

構成・運用・配布対象の変更とドキュメント更新を同期し、ドキュメントが常に「現在の姿」を反映する状態を保つ。

## 背景

技術スタックや実装方針が変わった際、ドキュメントの更新が漏れると：

- 新しく参加した人が古い手順を試して失敗する
- レビュアーがコードとドキュメントの食い違いに気づくまで時間がかかる
- 「ドキュメントが正しいのか、コードが正しいのか」の判断コストが増える

## 原則

### 1. 変更と同じPRでドキュメントを更新する

後回しにせず、同じPRで完結させる。

**対象ドキュメント:**

- README.md
- AGENTS.md
- rules/
- specs/
- decisions/（判断理由や履歴が必要な場合）
- skills/ 配下の README / references / assets
- 設定ファイルのコメント（mise.toml, apm.yml, .github/workflows/ 等）

### 2. ドキュメントは「現在の姿」を反映する

過去の手順や仕様は削除し、現在有効な情報だけを残す。

**例外:**

- `decisions/` は履歴として過去の判断を残す（削除しない）
- トラブルシューティングは「過去に起きた問題」として残す価値がある

### 3. 構成・ツール変更時のチェックポイント

- [ ] **README.md**
  - セットアップ手順
  - 前提条件（OS、ツールのバージョン）
  - コマンド例
- [ ] **rules/specs/decisions**
  - 横断方針、現在仕様、判断履歴のどれを更新すべきか確認
  - 過去の判断を消さず、新しい判断は DR として追加
- [ ] **skills/**
  - SKILL.md、references、assets の説明
  - skill として単体で成立するか
- [ ] **設定ファイルのコメント**
  - mise.toml: タスクの説明、依存ツールのコメント
  - apm.yml: skill の依存定義
  - .github/workflows/: ワークフロー内のコメント

## チェック方法

### 全文検索で確認

```bash
# 旧技術名・旧パスで全検索（decisions/を除く）
rg "旧技術名|旧パス" --glob '!decisions/**'

# 特定ファイルを対象に検索
rg "旧技術名|旧パス" README.md AGENTS.md rules specs skills mise.toml apm.yml
```

### レビュー時の観点

- コード変更に対応するドキュメント更新が含まれているか
- セットアップ手順が最新の構成に合っているか
- 削除した技術の言及が残っていないか

## 参考

- コメントと実装の整合性: `skills/universal-code-reviewer/references/rules/keep-comments-in-sync.md`
- 命名と実装の整合性: `skills/universal-code-reviewer/references/rules/keep-names-in-sync-with-behavior.md`
