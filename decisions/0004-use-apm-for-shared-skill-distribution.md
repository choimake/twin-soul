# APM を `skill` の配布基盤として使う

## ステータス

採用済み (2026-05-10)

## 背景

`twin-soul` は、`skill` の正本を `skills/` に置き、これまで次の 2 つの独自経路で利用していた。

- 集約リポジトリ内では `scripts/hub/sync.sh` が `.cursor/skills/` と `.claude/skills/` にシンボリックリンクを張り、`AGENTS.md` / `CLAUDE.md` を再生成する
- 利用先リポジトリでは `npx --yes github:choimake/twin-soul` が `bin/install.js` を実行し、`.cursor/skills/` と `.claude/skills/` にコピーして `skills-lock.json` を更新する

この方式は小さく始めるには十分だったが、次の制約が出ていた。

- 配布・固定・監査・対象実行環境ごとの配置を独自実装で持つ必要がある
- `npx` インストーラーと hub 内 `sync.sh` で役割が分かれ、更新フローが増えている
- `skills-lock.json` は `twin-soul` 固有の管理情報であり、今後 MCP / プロンプト / 指示文書 などを扱う場合の拡張先が弱い
- Cursor / Claude Code 以外のエージェント実行環境へ広げる場合、配置ルールをこちらで追い続ける必要がある

Microsoft APM（Agent Package Manager）は、Git リポジトリ / サブディレクトリからのパッケージ導入、`apm.lock.yaml` によるコミット固定、監査、Cursor / Claude Code など複数の実行環境への展開を提供する。`twin-soul` の各 `skills/<skill-name>/SKILL.md` はすでに `name` / `description` フロントマターを持ち、APM のサブディレクトリ単位のパッケージとして扱える。

## 判断

`twin-soul` の `skill` 配布基盤を Microsoft APM に移行する。

採用する方針:

- `skills/` は引き続き `skill` の正本とする
- 利用先リポジトリは `apm.yml` に `choimake/twin-soul/skills/<skill-name>#<ref>` を宣言し、`apm install` で導入する
- 利用先リポジトリは `apm.lock.yaml` をコミットし、解決済みコミットと展開済みファイルを固定する
- Cursor 向け `skill` は APM 標準の `.agents/skills/`、Claude Code 向け `skill` は `.claude/skills/` を既定の展開先とする
- 既存リポジトリが `.cursor/skills/` を前提にしている場合だけ、移行期間中に `APM_LEGACY_SKILL_PATHS=1` または `--legacy-skill-paths` を使う
- プライベートリポジトリとして使う場合は APM の Git 認証（`GITHUB_APM_PAT`、`GITHUB_APM_PAT_{ORG}`、`gh auth login` など）に任せる
- 独自の `npx` インストーラー、`skills-lock.json` 運用、hub 内 `sync.sh` 差分確認は撤去する

初期移行では、全 `skill` 一括のまとめパッケージ化ではなく、既存 `skills/<skill-name>/` を APM のサブディレクトリ単位のパッケージとして参照する。全 `skill` 一括導入や `rules` / 指示文書の外部配布が必要になった場合は、別途 `.apm/skills/` や `.apm/instructions/` への移行を検討する。

## 影響

メリット:

- 配布・固定・監査・実行環境ごとの配置を APM に委譲でき、独自インストーラーの保守が不要になる
- 利用先リポジトリは `apm.yml` と `apm.lock.yaml` で導入 `skill` と解決済みコミットを明示できる
- プライベートリポジトリの認証や CI 上の再現性を APM の標準機能に寄せられる
- Cursor / Claude Code 以外の実行環境へ広げる余地ができる
- `skills/` 正本の考え方は維持できるため、既存 `skill` の本文構造を大きく変えずに移行できる

デメリット / 注意:

- `apm` CLI がローカル開発環境と CI の前提に加わる
- Cursor 向けの既定展開先が `.cursor/skills/` ではなく `.agents/skills/` になるため、既存リポジトリでは移行期間の案内が必要になる
- `sync.sh` は `skills/` だけでなく `rules/` シンボリックリンクと入口文書生成も担っていたため、`rules/` / `AGENTS.md` / `CLAUDE.md` の扱いは APM 配布とは別に整理する必要がある
- 全 `skill` 一括導入は `npx` 時代より明示的になる。必要な `skill` を `apm.yml` に列挙する運用を基本とし、まとめパッケージ化は必要になってから判断する

## 関連する DR

- 関連: [decisions/0001-document-boundaries.md](0001-document-boundaries.md)
- 関連: [decisions/0003-deprecate-ai-skill-security-toolchain.md](0003-deprecate-ai-skill-security-toolchain.md)
