---
name: [skill-name]
description: >-
  この skill が何をするかを書く。続けて、どんな依頼、キーワード、状況のときに使うかを書く。skill 名を知らない依頼でも拾える具体文脈と、近い task と混同しにくい境界を入れる。
# 任意の標準 field:
# license: [license 名または bundled license file]
# compatibility: [必要な場合だけ環境要件]
# metadata:
#   [key]: [value]
# experimental / client-specific な任意 field は、対象 agent が対応している場合だけ使う。
---

# [Skill Title]

## 目的

[この skill をどんな観点で扱うかを 1 文で書く。]

## 使う場面

- [使う場面 1]
- [使う場面 2]
- [使う場面 3]

## 手順

1. [対象や論点を特定する]
2. [依頼種別を判定する]
3. [必要最小限の関連資料だけを読む]
4. [ファイル分割や出力方針を決める]
5. [必要なら assets のテンプレートを起点に本文を組み立てる]
6. [review / draft / write-file の返し分けを書く]

詳細な判断が必要な場合は [references/[knowledge-file].md](references/[knowledge-file].md) を読む。

## 期待する出力

- [何を返すか 1]
- [何を返すか 2]
- [何を返すか 3]

## 検証

- ユーザー意図と異なる誤解を招く（misleading な）skill や、不正利用を助ける skill になっていない
- `SKILL.md` 自体は使い方に留まり、詳細知識を抱え込んでいない
- 迷ったら足さず削っている。他 skill の手順を写していない
- 毎回使う短い手順は SKILL.md に残している
- `name` は親ディレクトリ名と一致している
- 詳細な判断は `references/` を読めば追える
- 参照ファイルには「いつ読むか」が `SKILL.md` から分かる
- 新規作成や改稿では `assets/` のテンプレートを起点にできる
- YAML frontmatter は `name` と `description` を必須として持つ
- YAML frontmatter の `description` は 1024 文字以内で、`>-` を使い、plain scalar にしていない
- `description` は WHAT と WHEN を含み、undertrigger を避ける具体文脈と overtrigger を避ける境界が見える
- 必要なら 2〜3 件の test prompt で trigger、出力、確認質問の妥当性を試せる
- 任意 field や client-specific field を標準 field と混同していない
- 対象が不明なときの扱いが明確
