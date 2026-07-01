# 関係ない template を抱え込みすぎていないか

## ねらい

リポジトリに存在しない stack や IDE の template を含めると、`.gitignore` が過剰になり、必要なファイルまで誤って除外するリスクが増える。

## チェック観点

- 選定 template がリポジトリ内の手掛かりと整合しているか
- 会話で明示された stack / IDE / OS 以外の template を無根拠に含めていないか
- 個人設定（特定 editor の local 設定など）を project 共有 `.gitignore` に入れすぎていないか
- `docker` template を、言語別 template で足せる場合に安易に選んでいないか

## 指摘する基準

- リポジトリに存在しない主要 stack の template を含む場合は **重大** として指摘する
- 個人設定を project 共有 `.gitignore` に入れすぎている場合は **提案** として指摘する
- 補助 template の選定理由が説明されていない場合は **提案** として指摘する

## 例

### 悪い例

```gitignore
# Python だけのリポジトリなのに Java / Ruby / PHP template を全部含める
```

### 良い例

```gitignore
# リポジトリに package.json と .vscode/ がある → macos,visualstudiocode,node
```

## 補足

- OS template は host OS またはチームの主要 OS に合わせて選ぶ
- 手掛かりが弱い場合は template を絞らず、確認質問を返す方が安全
