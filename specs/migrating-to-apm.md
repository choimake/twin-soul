# Migrating To APM

この文書は、`npx --yes github:choimake/twin-soul` で skill を導入していた利用先リポジトリを Microsoft APM に移す手順をまとめる。

## 前提

- APM CLI が利用できる
- プライベートリポジトリの場合は `GITHUB_APM_PAT`、`GITHUB_APM_PAT_{ORG}`、または `gh auth login` で Git 認証できる
- 既存の project 固有 skill は APM で導入する skill と別管理にする

## 移行手順

1. 利用先リポジトリに `apm.yml` を追加する。

   ```yaml
   name: target-project
   version: 1.0.0
   target: [cursor, claude]
   dependencies:
     apm:
       - choimake/twin-soul/skills/planner#main
       - choimake/twin-soul/skills/universal-code-reviewer#main
   ```

2. APM で導入する。

   ```bash
   apm install
   ```

3. `apm.lock.yaml` をコミットする。
4. Cursor / Claude Code から対象 skill が見えることを確認する。
5. 問題なければ旧 `skills-lock.json` と旧 copy の skill を削除する。

## 旧パスを使うリポジトリ

APM の既定では Cursor 向け skill は `.agents/skills/` に展開される。既存リポジトリ が `.cursor/skills/` を前提にしている場合は、移行期間だけ次を使う。

```bash
APM_LEGACY_SKILL_PATHS=1 apm install
```

恒久運用では `.agents/skills/` に寄せる。

## 更新

skill の更新を取り込むときは利用先リポジトリで次を実行する。

```bash
apm install --update
```

または dependency 単位で更新する。

```bash
apm deps update choimake/twin-soul/skills/planner
```
