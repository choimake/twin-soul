# 命名と実行内容を一致させる

## ねらい

識別子（関数名、変数名、ファイル名、ジョブID、表示名など）と実体の挙動がズレると、読む人は「名前から期待される動き」と「実際の動き」を都度すり合わせる必要が出る。
このズレはレビューの判断コストを増やし、誤解による運用ミスや変更ミスにつながる。

## チェック観点

- 名前/ラベル/ID が **実際にやっていること** と一致しているか
  - 例: GitHub Actions の job ID / `name:`、step name、スクリプト名、Terraform module 名/変数名
- 変更で役割が増減したのに、名前が更新されず「過去の役割」を示したままになっていないか
- 一時的な名称（`tmp` / `wip` / `bootstrap_only` 等）が残っていないか（残すなら意図と期限を明記する）

## 指摘する基準（境界）

- 「名前から期待される挙動」と「実際の挙動」がズレており、**誤解や運用ミスにつながり得る** 場合は 重大 として指摘する
- 互換性などで識別子（ID）を変えにくい場合は、代替として **表示名/README/コメント** で補う案も提示する

## 例

### 悪い例（名前と実体が食い違う）

```yaml
jobs:
  infra_bootstrap_tfstate:
    steps:
      - name: Check Terramate invariants
        run: ./scripts/ci-check-invariants.sh
      - name: Terraform module checks (infra/modules/* with tests/)
        run: ./scripts/check-modules.sh
```

job ID が「bootstrap tfstate だけ」を連想させる一方で、実際は invariants や複数 module のチェックも行っている。

### 良い例（名前を実体に合わせる）

```yaml
jobs:
  infra_checks:
    name: Infra checks (invariants + modules)
    steps:
      - name: Check Terramate invariants
        run: ./scripts/ci-check-invariants.sh
      - name: Terraform module checks (infra/modules/* with tests/)
        run: ./scripts/check-modules.sh
```

## 補足

- このルールは「コメントと実装の不一致」ではなく、「命名と実体の不一致」を扱う
- 命名を直せない事情がある場合は、せめて表示名（例: GitHub Actions の `name:`）や README で意図を補う
