# Installing Skills

この文書は、`twin-soul` から別プロジェクトへ skill を導入するときの APM 運用を整理する。

## 目的

- `skills/` を単一正本として保つ
- `Cursor` と `Claude Code` の両方で同じ skill を見せる
- 利用先リポジトリの project 固有 skill を壊さない
- `apm.lock.yaml` で導入内容を再現可能にする

この文書の手順は APM CLI `0.12.4` で検証する。

## 使い方

### 全 skill を入れる

第三者が `twin-soul` の skill をまとめて使う場合は、利用先リポジトリで root package を指定する。`twin-soul` は `skills/<skill-name>/SKILL.md` が並ぶ Skill collection として扱われ、APM が nested skill を target runtime へ展開する。

```bash
cd /path/to/target-project
apm install choimake/twin-soul#main --target cursor,claude
```

チームで再現可能に運用する場合は、利用先リポジトリに `apm.yml` を置く。

```yaml
name: target-project
version: 1.0.0
target: [cursor, claude]
dependencies:
  apm:
    - choimake/twin-soul#main
```

その後、利用先リポジトリで実行する。

```bash
apm install
```

- `twin-soul` を clone していない環境でも使える
- GitHub リポジトリから直接取得し、APM が target runtime へ展開する
- プライベートリポジトリの場合は Git 認証が必要
- バージョン固定は `#v1.0.0`、commit 固定は `#<sha>` のように dependency ref へ付ける
- `.cursor/skills/` を前提にした利用先では、移行期間だけ `APM_LEGACY_SKILL_PATHS=1 apm install` を使える

### 特定 skill だけ入れる

用途を絞りたい場合は、各 skill を subdirectory package として指定する。

```bash
apm install choimake/twin-soul/skills/planner#main --target cursor,claude
```

複数の skill を選んで入れる場合は、必要な subdirectory package を並べる。

```bash
apm install \
  choimake/twin-soul/skills/planner#main \
  choimake/twin-soul/skills/testcode#main \
  --target cursor,claude
```

`apm.yml` に書く場合も、必要な skill を列挙する。

```yaml
name: target-project
version: 1.0.0
target: [cursor, claude]
dependencies:
  apm:
    - choimake/twin-soul/skills/planner#main
    - choimake/twin-soul/skills/testcode#main
```

この方式は導入単位が明示的で、チームで用途を絞る場合に更新範囲を小さくできる。

### このリポジトリを clone して開発するとき（任意）

ローカル authoring 用にも、ルートの `apm.yml` は Skill collection として扱う。`dependencies.apm` に `path: ./skills/...` を列挙すると、remote package として導入されたときに consumer filesystem への local path dependency と見なされるため使わない。

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

全 skill 導入では、APM が root package を Skill collection として解釈し、`skills/<skill-name>/` をそれぞれ target の skill ディレクトリへ展開する。特定 skill の導入では `choimake/twin-soul/skills/<skill-name>#<ref>` のサブディレクトリ package として導入する。

skill 内の `references/`、`assets/`、`scripts/` などの下位構成は deploy 側で固定しない。

## 更新フロー

1. `twin-soul` 側の `skills/` を更新する
2. このリポジトリで `mise run ci:apm` を実行する（クリーン環境では `apm install --dry-run` のみだと展開先が無く audit が失敗するため、`ci:apm` は実インストール後に audit する）
3. 利用先リポジトリごとに `apm install --update`、`apm update`、または `apm deps update` を実行する

## トラブルシューティング

### remote package の local_path dependency が拒否される

次のようなエラーが出る場合、remote package として読み込まれた `apm.yml` が `path: ./skills/...` のような local path dependency を宣言している。

```text
Refusing to install local_path dependency './skills/planner' declared by remote package 'twin-soul': remote packages cannot reference paths on the consumer filesystem.
```

remote package では consumer filesystem 上の local path を参照できない。`twin-soul` では root package を Skill collection として扱い、全 skill は `choimake/twin-soul#main`、特定 skill は `choimake/twin-soul/skills/<skill-name>#main` で導入する。

## npx / skills-lock.json からの移行

以前の installer は `.cursor/skills/` と `.claude/skills/` に copy し、`skills-lock.json` に管理対象を記録していた。APM 移行後は `apm.yml` と `apm.lock.yaml` を正とする。

1. 利用先リポジトリに `apm.yml` を追加する
2. 必要な skill を `dependencies.apm` に列挙する
3. `apm install` を実行する
4. 動作確認後、旧 `skills-lock.json` と旧 copy の skill を削除する

旧 `.cursor/skills/` を即時に消せない場合は、移行期間だけ `APM_LEGACY_SKILL_PATHS=1 apm install` を使い、段階的に `.agents/skills/` へ寄せる。

## 将来拡張

今の導入は skill に絞っている。必要になれば APM の instructions として `rules/` の配布も検討できるが、現時点では skill の配布対象に含めない。
