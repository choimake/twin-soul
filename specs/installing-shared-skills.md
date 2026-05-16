# Installing Skills

この文書は、`twin-soul` から別プロジェクトへ skill を導入するときの APM 運用を整理する。

## 目的

- `skills/` を単一正本として保つ
- `Cursor` と `Claude Code` の両方で同じ skill を見せる
- 利用先リポジトリの project 固有 skill を壊さない
- `apm.lock.yaml` で導入内容を再現可能にする

## 使い方

### APM でインストール（公式）

利用先リポジトリに `apm.yml` を作成し、必要な skill を `dependencies.apm` に列挙する。

```yaml
name: target-project
version: 1.0.0
target: [cursor, claude]
dependencies:
  apm:
    - choimake/twin-soul/skills/planner#main
    - choimake/twin-soul/skills/universal-code-reviewer#main
```

利用先リポジトリで実行する。

```bash
cd /path/to/target-project
apm install
```

- `twin-soul` を clone していない環境でも使える
- GitHub リポジトリから直接取得し、APM が target runtime へ展開する
- プライベートリポジトリの場合は Git 認証が必要
- バージョン固定は `#v1.0.0`、commit 固定は `#<sha>` のように dependency ref へ付ける
- `.cursor/skills/` を前提にした利用先では、移行期間だけ `APM_LEGACY_SKILL_PATHS=1 apm install` を使える

### このリポジトリを clone して開発するとき（任意）

ローカル authoring 用に、ルートの `apm.yml` は `skills/*` を local dev dependency として列挙している。

```bash
apm install --target cursor,claude
```

## 管理方式

- 導入は利用先リポジトリの `apm.lock.yaml` に解決結果を書き出す
- `apm.lock.yaml` は git コミット対象である
- APM は resolved commit、virtual path、deployed files を記録し、再実行時の cleanup に使う
- skill と同名の local file がある場合、APM の collision detection に従う。意図的に上書きする場合だけ `--force` を使う

## 対象パス

- `.agents/skills/<skill-name>`
- `.claude/skills/<skill-name>`

APM の既定では、Cursor 向け skill は cross-client 標準の `.agents/skills/` に展開される。Claude Code は `.claude/skills/` に展開される。既存の `.cursor/skills/` が必要なリポジトリでは `--legacy-skill-paths` または `APM_LEGACY_SKILL_PATHS=1` を使う。

skill は `skills/<skill-name>/` ディレクトリを単位として導入し、`references/`、`assets/`、`scripts/` などの下位構成は deploy 側で固定しない。

## 更新フロー

1. `twin-soul` 側の `skills/` を更新する
2. このリポジトリで `mise run ci:apm` を実行する（クリーン環境では `apm install --dry-run` のみだと展開先が無く audit が失敗するため、`ci:apm` は実インストール後に audit する）
3. 利用先リポジトリごとに `apm install --update` または `apm deps update` を実行する

## npx / skills-lock.json からの移行

以前の installer は `.cursor/skills/` と `.claude/skills/` に copy し、`skills-lock.json` に管理対象を記録していた。APM 移行後は `apm.yml` と `apm.lock.yaml` を正とする。

1. 利用先リポジトリに `apm.yml` を追加する
2. 必要な skill を `dependencies.apm` に列挙する
3. `apm install` を実行する
4. 動作確認後、旧 `skills-lock.json` と旧 copy の skill を削除する

旧 `.cursor/skills/` を即時に消せない場合は、移行期間だけ `APM_LEGACY_SKILL_PATHS=1 apm install` を使い、段階的に `.agents/skills/` へ寄せる。

## 将来拡張

今の導入は skill に絞っている。必要になれば APM の instructions として `rules/` の配布も検討できるが、現時点では skill の配布対象に含めない。
