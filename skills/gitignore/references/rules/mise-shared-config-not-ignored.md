# mise の共有設定を誤って ignore していないか

## ねらい

`mise.toml` は project 設定として commit 対象に残すべきである。local override だけを ignore し、共有設定まで除外するとチーム全体の環境構築が壊れる。

## チェック観点

- `mise.toml` や共有したい `mise.<env>.toml` を ignore していないか
- `mise.local.toml` と `mise.<env>.local.toml` だけを ignore 対象にしているか
- `.mise.*` 系を標準運用として広げすぎていないか

## 指摘する基準

- `mise.toml` 本体を ignore している場合は **重大** として指摘する
- 共有環境設定の `mise.<env>.toml` を ignore している場合は **重大** として指摘する
- local override の ignore 漏れがある場合は **提案** として指摘する

## 例

### 悪い例

```gitignore
mise.toml
mise.local.toml
```

### 良い例

```gitignore
# mise local overrides
mise.local.toml
mise.*.local.toml
```

## 補足

- 推奨ルールは [../../assets/mise-local-overrides.gitignore](../../assets/mise-local-overrides.gitignore) を起点にする
- custom block は `gitignore.io` 由来 block の後ろに足す
