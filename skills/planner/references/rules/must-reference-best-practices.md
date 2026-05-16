# ベストプラクティスを参照しているか

## ねらい

ベストプラクティスを参照することで、車輪の再発明を防ぎ、実績ある手法を活用できる。
特に、認証、API設計、テスト戦略など、定石が確立している領域では、ベストプラクティスの参照が重要。

## チェック観点

- ベストプラクティスセクションが存在するか
- 参照先がタスク内容に関連しているか
- リンク形式で記述されているか（URL付き）
- 信頼性の高いソース（公式ドキュメント、Thoughtbot、Atlassian、Martin Fowlerなど）を含むか

## 指摘する基準

- ベストプラクティスセクションが無い場合は **提案** として指摘する
- ベストプラクティスの参照が不十分（1件以下）な場合は **提案** として指摘する
- リンクが無い、または無関係な参照の場合は **提案** として指摘する

## 例

### 悪い例（参照が無い）

```markdown
## ベストプラクティス

特になし
```

### 良い例（リンク付き、関連性あり）

```markdown
## ベストプラクティス

- [Planning ベストプラクティス - Atlassian](https://www.atlassian.com/agile/project-management/planning): アジャイル開発における計画の立て方
- [受け入れ条件 - Thoughtbot](https://thoughtbot.com/blog/acceptance-criteria): 良い受け入れ条件の書き方
- [Decision Records - Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions): 設計判断の記録方法
```

## 補足

- Web検索でベストプラクティスを取得する場合は、「技術キーワード + best practices + 2026」の形式で検索する
- 検索結果から信頼性の高いソースを優先的に選ぶ
- タスク内容と無関係な一般論は避け、具体的な技術領域に関連するベストプラクティスを選ぶ
