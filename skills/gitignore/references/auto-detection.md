# 自動推定

まずリポジトリから候補を出し、その後に人間が妥当性を確認する。推定だけで全面確定しない。

## 優先する流れ

1. `scripts/fetch-gitignore.sh detect <target-path>` で候補を見る
2. 会話で明示された stack や IDE があれば上書き、または追加する
3. 必要なら `scripts/fetch-gitignore.sh auto <target-path> <extra...>` で本文を取得する
4. 取得結果をそのまま貼らず、既存 `.gitignore` や project 固有ルールと突き合わせる

自動推定は「最初の候補出し」を速くするためのものであり、最終判断の代替ではない。

## リポジトリと `detect` の主な手掛かり

`scripts/fetch-gitignore.sh detect` は主に次を見て template 候補を出す。会話や手動で得た手掛かりも同列で解釈してよい。

- 現在のホスト OS: `macos` / `linux` / `windows`
- `package.json`、`pnpm-workspace.yaml`、`yarn.lock`: `node`
- `pyproject.toml`、`requirements.txt`、`Pipfile`、`poetry.lock`、`.venv/`: `python`
- `go.mod`: `go`
- `Cargo.toml`: `rust`
- `Gemfile`: `ruby`
- `composer.json`: `php`、`composer`
- `pom.xml`: `java`
- `build.gradle`、`build.gradle.kts`、`gradlew`: `gradle`、`java`
- `.vscode/`、`*.code-workspace`: `visualstudiocode`
- `.idea/`、`*.iml`: `jetbrains` または個別 IDE template
- `*.xcodeproj`、`*.xcworkspace`: `xcode`
- `terraform/`、`*.tf`、`.terraform.lock.hcl`: `terraform`

手掛かりが弱い場合は、無理に決め打ちせず確認質問を返す。検出精度より安全性を優先し、曖昧なものは広げすぎない。
