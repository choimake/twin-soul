# 共有すべき env 例ファイルを誤って除外していないか

## ねらい

`.env` 系を ignore する一方で、`.env.example` など共有すべき例ファイルまで除外すると、新メンバーが必要な環境変数を把握できなくなる。

## チェック観点

- `.env`、`.env.local` など機密を含む file を ignore しているか
- `.env.example`、`.env.sample` など共有すべき例 file を誤って ignore していないか
- `!.env.example` のような negation pattern が必要な場合に含まれているか

## 指摘する基準

- `.env.example` など共有すべき例 file を ignore している場合は **重大** として指摘する
- `.env` 系の ignore 漏れがある場合は **提案** として指摘する
- negation pattern の必要性が説明されていない場合は **任意** として指摘する

## 例

### 悪い例

```gitignore
.env*
```

### 良い例

```gitignore
.env
.env.local
!.env.example
```

## 補足

- プロジェクトの env file 命名規則に合わせて調整する
- 判別しにくい場合は、共有 file の一覧を確認してから提案する
