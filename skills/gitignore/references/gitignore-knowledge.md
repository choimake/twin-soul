# Gitignore 判断知識

この資料は `gitignore` skill の判断知識をまとめたものである。`SKILL.md` は入口に留め、template 選定、リポジトリからの自動推定、custom 手書きルール、既存 `.gitignore` の扱い、helper script の使い方、fallback はこの資料を起点にする。

## 入力として受け取れるもの

呼び出し側は、必要に応じて次を渡せる。

- 対象リポジトリ や `@path`
- 明示された技術スタック、OS、IDE、ツール
- 既存 `.gitignore` の有無
- `review` / `draft` / `write-file`
- 保存先のファイルパス
- 既存の手書きルールを保持したいかどうか

未指定なら、会話とリポジトリの手掛かりから妥当な既定値を判断する。足りない情報だけを短く確認する。

## 出力モードの既定値

- 既存 `.gitignore` がある場合の見直しは `review`
- `.gitignore` がなく、新規作成の相談は `draft`
- 保存先が明示され、実ファイル更新を求められた場合だけ `write-file`

構成判断と本文案の両方を求められている場合は `draft` を優先する。

## 情報源の優先順位

template 候補は次の順で決める。

1. ユーザーが明示した技術スタック、OS、IDE
2. リポジトリ内の手掛かり
3. helper script の自動推定結果
4. 足りないときの確認質問
5. よくある補助 template の提案

リポジトリ内の手掛かりは、判断に必要な最小限だけ読む。

## 自動推定の基本方針

まずリポジトリから候補を出し、その後に人間が妥当性を確認する。推定だけで全面確定しない。

優先する流れ:

1. `scripts/fetch-gitignore.sh detect <target-path>` で候補を見る
2. 会話で明示された stack や IDE があれば上書き、または追加する
3. 必要なら `scripts/fetch-gitignore.sh auto <target-path> <extra...>` で本文を取得する
4. 取得結果をそのまま貼らず、既存 `.gitignore` や project 固有ルールと突き合わせる

自動推定は「最初の候補出し」を速くするためのものであり、最終判断の代替ではない。

### リポジトリと `detect` の主な手掛かり

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

## template 名の扱い

`gitignore.io` は template 名を comma 区切りで渡す。たとえば `macos,visualstudiocode,node` のように取得する。

### よく使う template 名

- macOS: `macos`
- Windows: `windows`
- Linux: `linux`
- VS Code: `visualstudiocode`
- Vim: `vim`
- Emacs: `emacs`
- Node.js: `node`
- Python: `python`
- Go: `go`
- Rust: `rust`
- Java: `java`
- Terraform: `terraform`
- Docker 系の補助: `docker` ではなく、通常は言語やツールごとの template と手書きルールを優先する

`gitignore.io` 上の正式名と会話中の表現が違うことがあるため、会話では自然な名前を受けて、取得時に正式な template 名へ正規化する。

## `gitignore.io` にない tool の扱い

template がない tool は、`gitignore.io` の候補とは別に custom 手書きルールとして足す。繰り返し使う block は `assets/` に置き、`draft` や `write-file` ではそこを起点にする。

### `mise`

`mise.toml` や `mise.<env>.toml` は共有設定として commit 対象に残す。ignore したいのは local override 系である。

推奨ルールは [../assets/mise-local-overrides.gitignore](../assets/mise-local-overrides.gitignore) を使う。

意図:

- `mise.toml` は project 設定なので ignore しない
- `mise.<env>.toml` も共有したい環境設定なら ignore しない
- `mise.local.toml` と `mise.<env>.local.toml` はローカル専用なので ignore する
- `.mise.*` 系は標準運用としては広げず、必要なリポジトリでだけ個別に足す

skill が `mise` を扱うときは、`gitignore.io` の本文に後付けの custom block として足す。

## 既存 `.gitignore` の扱い

既存ファイルがある場合は、次を優先する。

1. 既存の手書きルールや project 固有ルールをむやみに消さない
2. `gitignore.io` の生成ブロックと手書きルールを区別して読む
3. 何を追加し、何を維持し、何を削るかを分けて提案する
4. 判別しにくい項目は削除せず、理由付きで保留にする

既存ファイルが `# Created by https://www.toptal.com/developers/gitignore/api/...` のような見出しを持つ場合でも、その後に足された手書きルールがあり得る。全面置換ではなく、差分ベースで扱う方が安全である。

## review の観点

- 今の `.gitignore` で拾えていないビルド生成物、キャッシュ、仮想環境、IDE ファイルがないか
- リポジトリに存在する設定と関係ない template を抱え込みすぎていないか
- 個人設定を project 共有の `.gitignore` に入れすぎていないか
- `dist/`、`.next/`、`.venv/`、`.terraform/` など、実際の生成物と整合しているか
- `.env` 系を ignore する一方で、`.env.example` など共有すべき例ファイルを誤って除外していないか
- `mise` の local override だけを ignore し、`mise.toml` 本体を誤って除外していないか

## draft と write-file の方針

### `draft`

- 推奨 template 名を先に明示する
- その後に file-ready な `.gitignore` 案を返す
- `mise` のような custom ルールがある場合は、`gitignore.io` 由来 block の後ろに asset 起点の手書き block を足す
- 必要なら「この行は project 固有で手書き追加」と分かるよう区切る

### `write-file`

- 保存先が明示された場合だけ実行する
- 既存ファイルがあるなら全面置換より差分更新を優先する
- `gitignore.io` 由来のブロックと手書きブロックが混ざる場合は、意図が追えるようにコメントを残してよい
- `mise` 用ルールを足す場合は、既存の `mise.toml` を ignore しないことを確認する

## helper script の使いどころ

この skill では、`gitignore.io` の一覧取得や template 取得に加えて、リポジトリから候補を洗い出す処理も繰り返し発生しやすく、処理も比較的安定しているため `scripts/fetch-gitignore.sh` を同梱する。

### 使い方

template 一覧:

```bash
bash skills/gitignore/scripts/fetch-gitignore.sh list
```

template 候補の自動推定:

```bash
bash skills/gitignore/scripts/fetch-gitignore.sh detect .
```

自動推定に追加 template を足す:

```bash
bash skills/gitignore/scripts/fetch-gitignore.sh detect . terraform
```

template 取得:

```bash
bash skills/gitignore/scripts/fetch-gitignore.sh macos visualstudiocode node
```

自動推定してそのまま取得:

```bash
bash skills/gitignore/scripts/fetch-gitignore.sh auto .
```

この script は、space 区切りでも comma 区切りでも受け取り、template 名を lower-case に正規化して `gitignore.io` へ渡す。`detect` は comma 区切りの template 候補一覧を返し、`auto` は推定結果に optional な追加 template をマージして本文を取得する。

## fallback

次の状況では、取得結果より判断の透明性を優先する。

- `gitignore.io` へ接続できない
- 自動推定の結果が OS しか出ず、言語や IDE が絞れない
- template 名が不明で候補が複数ある
- `mise` のように template が存在せず、custom ルールが必要
- リポジトリの手掛かりが弱く、複数スタックがあり得る
- 既存 `.gitignore` のローカルルールが多く、機械的な統合が危険

fallback では次を返す。

- 推奨 template 名の候補
- 必要なら custom 手書きルール
- 追加で確認したいこと
- 手書きで先に入れてよい最小限の ignore 項目

## script を入れた理由

この skill の中心は `.gitignore` の判断だが、`gitignore.io` から template を取ってくる部分と、リポジトリから候補を洗い出す部分は毎回ほぼ同じである。会話だけで毎回 API 形式と検出手順を説明するより、軽い helper script に寄せた方が再現しやすく、反復コストも下がる。
