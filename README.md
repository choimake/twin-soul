# twin-soul

`twin-soul` は、`choimake` が複数プロジェクトで使い回すスキルとルールの置き場所です。
外部のナレッジに加えて、過去の経験から生まれた少し独特な判断や手順も含めているため、`twin-soul`（双子の魂）と名付けました。

## 概要

- 過去の経験から得た作業手順を `skill` として整理する
- リポジトリ横断で守りたい判断基準を `rules` として一元管理する
- Microsoft APM（Agent Package Manager）で `skill` を導入・更新する
- `apm.lock.yaml` で利用先リポジトリの `skill` バージョンを固定する

## なぜ使うか

- プロジェクトごとに同じ判断や手順を作り直さなくてよくなる
- AI 補助の作業手順を、個人の記憶ではなくリポジトリに残せる
- `skill` の更新を 1 か所に集約できる
- 利用先リポジトリのプロジェクト固有 `skill` を壊さずに、共通の型だけを追加できる

## はじめ方

### 使うだけの人向け

利用先リポジトリで APM CLI を使い、`twin-soul` を GitHub から直接導入します。`twin-soul` を clone する必要はありません。この手順は APM CLI `0.12.4` で検証しています。

全 skill をまとめて入れる場合:

```bash
apm install choimake/twin-soul#main --target cursor,claude
```

特定の skill だけ入れる場合:

```bash
apm install choimake/twin-soul/skills/planner#main --target cursor,claude
```

複数の skill を選んで入れる場合は、必要な subdirectory package を並べます。

```bash
apm install \
  choimake/twin-soul/skills/planner#main \
  choimake/twin-soul/skills/testcode#main \
  --target cursor,claude
```

チームで再現可能に運用する場合は、利用先リポジトリの `apm.yml` に依存を残します。全 skill を入れる例:

```yaml
name: target-project
version: 1.0.0
target: [cursor, claude]
dependencies:
  apm:
    - choimake/twin-soul#main
```

特定の skill だけ入れる例:

```yaml
name: target-project
version: 1.0.0
target: [cursor, claude]
dependencies:
  apm:
    - choimake/twin-soul/skills/planner#main
    - choimake/twin-soul/skills/testcode#main
```

その後、利用先リポジトリで実行します。

```bash
apm install
```

- `apm.lock.yaml` は利用先リポジトリでコミットします
- Cursor 向け skill は `.agents/skills/`、Claude Code 向け skill は `.claude/skills/` に展開されます
- `.agents/skills/`、`.claude/skills/`、`.cursor/skills/` は APM 展開物なのでコミットしません
- `.cursor/skills/` を前提にした既存リポジトリでは、移行期間だけ `APM_LEGACY_SKILL_PATHS=1 apm install` を使えます

詳しい導入仕様は [specs/installing-shared-skills.md](specs/installing-shared-skills.md) を参照してください。

### このリポジトリを開発する人向け

前提:

- 先に [AGENTS.md](AGENTS.md) とトップレベルの [rules/](rules/) を読む
- APM CLI は `mise install` で `pipx:apm-cli` として導入される
- 貢献前の検証手順は [CONTRIBUTING.md](CONTRIBUTING.md) を読む

```bash
# mise環境のセットアップ（APM CLI と検証ツール）
mise install
```

変更を検証します。

```bash
mise run ci:lint
mise run ci:apm
```

期待する結果:

- gitleaks, actionlint, ShellCheck, typos が成功する
- APM の `skill` 同期（`apm install`）と監査が成功する
- このリポジトリは組織共通の APM 監査ポリシーを使わないため、監査では `--no-policy` を指定する

## リポジトリ構成

- `skills/`: 実務経験から切り出した作業手順
- `rules/`: このリポジトリ全体に効く横断方針の正本
- `AGENTS.md`: エージェント向けの共通方針と文書優先順位
- `specs/`: 現在の構成と運用仕様
- `decisions/`: 大きな判断の記録
- `scripts/`: `ci/`（ローカル静的チェック）の補助スクリプト

`skill` は `skills/<skill-name>/SKILL.md` を起点にし、必要なときだけ `assets/`、`references/`、`scripts/` を足します。`skill` 内の判断観点や補助知識は各 `skill` 配下の `references/` に置き、リポジトリ全体の横断方針を置くトップレベル `rules/` とは分けて扱います。`references/` 配下の下位構成は `skill` ごとに決めてよく、たとえば `universal-code-reviewer` では個別ルール群を `references/rules/` に置きます。

## 公開時の注意

- このリポジトリは日本語主体で運用します。公開文書、Issue / PR テンプレート、スクリプトの人間向けメッセージも原則として日本語で揃えます。
- 法的な利用条件は [LICENSE](LICENSE) を参照してください。
- 脆弱性や機密情報漏えいの報告は [SECURITY.md](SECURITY.md) に従ってください。
- 貢献手順、検証コマンド、APM 展開物の扱いは [CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。
- 行動規範は [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) を参照してください。
- `skills/` が `skill` の正本です。`.agents/skills/`、`.claude/skills/`、`.cursor/skills/` は APM 展開物として扱い、コミットしません。

## 利用できるスキル

ここにある skill は、汎用知識だけではなく、このリポジトリで育てた判断や手順を再利用するための入口です。

- **decision-records**: Decision Record (DR) や ADR の新規追加、更新、supersede 判断、下書き作成を整理する
- **gap-analysis**: PRD と検証・調査結果を突き合わせ、実現可否と根拠を整理する
- **gitignore**: `.gitignore` の新規作成、既存見直し、`gitignore.io` からのテンプレート取得、自動推定を扱う
- **migrations-script**: 一度きりの移行スクリプト、データ修正、バックフィルの計画・レビューを扱う
- **mise-guide**: mise の tool バージョン管理、環境変数、task ランナー、GitHub Actions 連携の設定・相談を扱う
- **pbi**: プロダクトバックログアイテム（PBI）用 Markdown の起案・レビューを行い、受入基準・合意可能な検証・スコープを品質ゲートする
- **planner**: 計画ファイルの品質を確認し、必須項目の強制、AI 自動レビュー、Web 検索統合を行う
- **pragmatic-architect**: プロジェクト固有の Core / Details・依存方向・Legacy Baseline を対話で整理し、中核定義の草案を作る（一般的なコードレビュー用ではない）
- **readme**: README をプロジェクトの入口文書としてレビュー、作成、改稿する
- **requirements-definition**: 小規模プロダクト向けの要求定義を整理・レビューする
- **skill-creator**: Agent Skill の新規作成、改稿、分割、保存方針整理を行う
- **testcode**: テストコードの新規作成、既存テストの追加・改善、生成済みテストの評価を扱う
- **universal-code-reviewer**: コードレビューの汎用チェック観点を適用する

## 関連文書

- 共通方針と優先順位: [AGENTS.md](AGENTS.md)
- リポジトリ横断ルール: [rules/](rules/)
- `skill` の導入仕様: [specs/installing-shared-skills.md](specs/installing-shared-skills.md)
- 判断の履歴: [decisions/](decisions/)
- README 改善の観点: [skills/readme/SKILL.md](skills/readme/SKILL.md)
- 貢献手順: [CONTRIBUTING.md](CONTRIBUTING.md)
- セキュリティ報告: [SECURITY.md](SECURITY.md)
