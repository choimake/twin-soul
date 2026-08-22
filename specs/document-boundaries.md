# Document Boundaries

このドキュメントは、`twin-soul` 内で扱うドキュメントと再利用資産の境界を整理する。

## 目的

- 外部に展開する単位と、`twin-soul` 内部だけで使うドキュメントを分ける
- skill の設計時に、内部ドキュメントを前提にしすぎるコンセプトずれを防ぐ
- `skills/`、`specs/`、`decisions/`、`rules/` の扱いを実務上の観点でそろえる

## 境界の要約

判断理由は [../decisions/0001-document-boundaries.md](../decisions/0001-document-boundaries.md) と [../decisions/0005-rules-and-specs-boundaries.md](../decisions/0005-rules-and-specs-boundaries.md) を参照する。

| 種別         | 主用途                           | 外部展開の前提 | 補足                                                       |
| ------------ | -------------------------------- | -------------- | ---------------------------------------------------------- |
| `skills/`    | workflow と補助知識の配布        | あり           | APM の subdirectory package として単体導入できる状態を保つ |
| `specs/`     | `twin-soul` 内部の構成・運用仕様 | なし           | skill の配布対象ではない                                   |
| `decisions/` | `twin-soul` 内部の判断理由と履歴 | なし           | skill の前提知識として要求しない                           |
| `rules/`     | リポジトリ横断で守る方針              | なし           | 外部展開の主役ではなく、このリポジトリの正本として扱う          |

## `skills/` の扱い

- `skills/` は外部プロジェクトへ展開する skill の正本とする
- 1 つの skill は `skills/<skill-name>/` を単位にして APM で配布できる構成にする
- skill は `SKILL.md` を入口にし、必要な知識は同じ skill 配下の `references/`、`assets/`、`scripts/` に閉じる
- skill 配下の markdown 相対リンクは `skills/<skill-name>/` 内に閉じる。`rules/` や他 skill へ `../` で繋がない
- 利用先リポジトリに `specs/` や `decisions/` が存在しなくても、skill 自体の説明と workflow が成立している必要がある

外部プロジェクトへの導入方法と配布単位は [installing-shared-skills.md](installing-shared-skills.md) を参照する。

## `specs/` の扱い

- `specs/` は `twin-soul` 自身の構成、運用、配布方針を整理する
- installer の振る舞い、ドキュメント構成、配布元としての運用など、リポジトリ内部の仕様を残す
- skill の設計判断を説明するときに参照してよいが、skill の利用先で読めることを前提にしない

## `decisions/` の扱い

- `decisions/` は `twin-soul` 内部の判断理由と変更履歴を残す
- 現在の運用ルールそのものではなく、なぜその境界や方針を採用したかを記録する
- 日常の参照先にはせず、背景や採用理由を確認したいときだけ読む
- skill の本文や説明が `decisions/` の存在を前提にしないようにする

## `rules/` の扱い

- `rules/` はリポジトリ横断で守る方針、チェックリスト、禁止・推奨事項を置く正本とする
- `.cursor/rules/` や `.claude/rules/` には同期コピーや symlink を置かず、必要な内容はトップレベル `rules/` に集約する
- `rules/` は APM で外部プロジェクトへ導入する skill の配布対象ではない
- skill から `rules/` へ相対リンクしない。APM が展開時に `apm_modules/` 向きへ書き換え、`apm audit` が drift と誤判定する
- 抽象原則を再利用資産として扱いたい場合は、まず `skills/` で単体展開可能な workflow や補助知識に落とせるかを検討する
- `rules/` を将来 APM instructions などとして外部配布する場合は、別途 `specs/` と `decisions/` で位置づけを更新する

## 作業時の判断基準

新しい知識やドキュメントを追加するときは、次の順で置き場を判断する。

1. 外部プロジェクトへ単体で展開したいか
2. 利用先リポジトリに `twin-soul` 内部ドキュメントがなくても成立するか
3. 作業時に守る方針を書きたいのか、現在の運用仕様を書きたいのか、判断理由を書きたいのか

判断の目安:

- 単体で展開したいものは `skills/`
- リポジトリ横断で守る方針やチェックリストは `rules/`
- `twin-soul` の運用や構成を説明するものは `specs/`
- なぜその方針にしたかを残すものは `decisions/`

例:

- `rules/bash-safety.md`: Bash 実行時に守る安全性の判断基準
- `rules/document-consistency.md`: 変更時に守るドキュメント整合性のルール
- `specs/installing-shared-skills.md`: APM による skill 導入の現在仕様
- `specs/migrating-to-apm.md`: 旧方式から APM へ移る手順
