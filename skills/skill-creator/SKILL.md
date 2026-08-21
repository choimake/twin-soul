---
name: skill-creator
description: >-
  Agent Skill の新規作成、改稿、分割、`skills/` 配下への保存方針を整理する。`SKILL.md` / `references/` / `assets/` / `scripts/` の役割分担を決めたいとき、既存 skill を共通ルールに合わせて直したいとき、skill 用テンプレートから下書きを作りたいときに使う。
---

# Skill Creator

## 目的

SKILL.md は薄く保つ。判断知識の肥大は `references/` へ。迷ったら「SKILL.md だけで workflow が追えるか」を基準にする。

## 使う場面

- 新規 skill 追加時
- `SKILL.md` が肥大化し `references/` / `assets/` への分割が必要なとき
- `SKILL.md` / `references/` / `assets/` / `scripts/` の責務整理時
- 既存 skill を共通パターンに合わせて改稿するとき
- テンプレート起点の skill 一式下書き作成時
- 段階的改善の反復時

## 手順

1. 対象 skill の名前・保管先・テーマを特定。一意でなければ `@path` や用途を確認し、会話履歴から使った手順・修正指摘・入出力形式を拾う。
2. 構成レビュー・下書き作成・実ファイル更新のいずれかを判定。`review` / `draft` / `write-file` が明示されていれば優先。
3. skill が可能にする作業、trigger すべき状況、期待出力、test prompt 要否を確認。ユーザー意図と異なる誤解を招く（misleading な）skill や不正利用を助ける skill は作らない。
4. 関係する既存 skill と、必要なリポジトリの正本（`AGENTS.md`、`rules/`、`specs/` など）だけ確認。全 skill 読了は不要。
5. 新規か既存更新かを判定しファイル分割方針を決定。`SKILL.md`→workflow、`references/`→判断知識、`assets/`→テンプレート、`scripts/`→実行補助のみ。
6. `draft` / `write-file` では [assets/skill-template.md](assets/skill-template.md) と [assets/reference-template.md](assets/reference-template.md) を起点に本文を組み立てる。
7. `SKILL.md` の YAML frontmatter は `name` と `description` を必須にし、`description` には WHAT / WHEN / trigger / boundary と undertrigger を避ける具体文脈を入れる。任意 field や client-specific field は標準 field と混同しない。
8. 少数の test prompt で試行し結果から改善点を反映。個別例に過適合せず、効いていない指示は削り、重要な指示は理由も書く。
9. `scripts/` は原則追加せず、手順が壊れやすい・繰り返し実行する・検証が必要な場合のみ追加。eval / benchmark の仕組みは通常 workflow に必須化せず、必要な skill だけ任意で追加する。
10. `review`→分割方針と不足点のみ返す。`draft`→短い要約後に file-ready な本文案を返す。`write-file`→保存先が明示された場合のみ実行、`skills/` 更新後は `mise run ci:apm`（または `apm install --target cursor,claude && apm audit --ci --no-policy`）で確認。

詳細判断とファイル分割ルールは [references/skill-creator-knowledge.md](references/skill-creator-knowledge.md) を参照。

## 期待する出力

- 対象 skill に必要なファイル構成の整理
- `SKILL.md` / `references/` / `assets/` / `scripts/` の役割分担
- テンプレート起点の新規作成・改稿方針、または file-ready な skill 下書き
- `scripts/` 追加要否の判断
- test prompt や eval / benchmark を任意追加すべきかの判断
