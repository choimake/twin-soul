# APM の root Skill collection で全 skill を導入する

## ステータス

採用済み (2026-05-16)

## 背景

DR-0004 では、APM 移行の初期方針として `skills/<skill-name>/` をサブディレクトリ単位の package として導入することを採用し、全 `skill` 一括導入は必要になってから判断するとしていた。

その後、第三者が `twin-soul` を利用する導線を整理したところ、次の問題が分かった。

- 利用者が全 skill を試したい場合、12 個の `skills/<skill-name>` を列挙する手順は長く、公開 README の入口として分かりにくい
- root `apm.yml` に `path: ./skills/...` を列挙すると、remote package として `choimake/twin-soul#main` を導入したときに利用先のファイルシステム上のローカルパス依存と見なされ、APM が拒否する
- APM は `skills/<skill-name>/SKILL.md` が並ぶ repository を Skill collection として扱えるため、root package から全 skill を導入できる

一方で、APM CLI `0.12.4` のローカル E2E では `--skill` / `skills:` による subset install が `twin-soul` に対して期待どおり絞り込まれなかった。そのため、特定 skill の導入は検証済みのサブディレクトリ package 指定を使う。

## 判断

`twin-soul` の公開導入では、root package を APM の Skill collection として扱う。

採用する方針:

- 全 skill を導入する場合は `choimake/twin-soul#<ref>` を指定する
- 特定 skill だけを導入する場合は `choimake/twin-soul/skills/<skill-name>#<ref>` を指定する
- root `apm.yml` には remote install を壊す `path: ./skills/...` dependency を置かない
- root `apm.yml` は package metadata と target を表す
- このリポジトリの root `apm.lock.yaml` は、ローカルパス依存の管理をやめた後は不要とする
- 利用先リポジトリでは引き続き `apm.lock.yaml` をコミットし、解決済み commit と展開内容を固定する

この判断は、DR-0004 の「初期移行では全 skill 一括のまとめパッケージ化ではなく、既存 `skills/<skill-name>/` を APM のサブディレクトリ単位のパッケージとして参照する」という部分を置き換える。

## 影響

メリット:

- 第三者は `apm install choimake/twin-soul#main --target cursor,claude` で全 skill を導入できる
- 公開 README の最短導線が短くなり、`twin-soul` を clone しない利用者に説明しやすい
- remote package から利用先のファイルシステム上のローカルパスを参照する構成を避けられる
- 特定 skill 導入はサブディレクトリ package として明示でき、チームで必要な skill だけを選びやすい

デメリット / 注意:

- このリポジトリの root では `apm.lock.yaml` を持たないため、配布元の lockfile と利用先の lockfile の役割を区別する必要がある
- `--skill` / `skills:` による subset install は APM の公式機能として存在するが、`twin-soul` の APM CLI `0.12.4` 検証では期待どおりに絞り込まれなかったため、公開手順の本命にしない
- DR-0004 の初期移行方針を読む利用者には、現在の導入仕様として `specs/installing-shared-skills.md` と本 DR を参照してもらう必要がある
- root package の `#main` 例は、変更が main に入る前は旧 manifest を指す可能性があるため、PR 検証では branch / commit SHA など修正済み ref を使う

## 関連する DR

- Supersedes: [0004-use-apm-for-shared-skill-distribution.md](0004-use-apm-for-shared-skill-distribution.md) の全 skill 一括導入を見送った初期移行方針
- 関連: [0001-document-boundaries.md](0001-document-boundaries.md)
- 関連: [0005-rules-and-specs-boundaries.md](0005-rules-and-specs-boundaries.md)
