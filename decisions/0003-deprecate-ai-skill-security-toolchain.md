# AI スキルセキュリティ検証ツールチェーンの撤去

## ステータス

採用済み (2026-04-20)

## 背景

[decisions/0002-ai-skill-security-toolchain.md](0002-ai-skill-security-toolchain.md) で採用した promptfoo + mlx-lm + E2B によるセキュリティ検証ツールチェーンを、その後の運用観察を踏まえて再評価したところ、以下の構造的な乖離が明らかになった。

1. **実運用モデルと計測モデルの乖離**: 実際に `skills/` を動かすのは Cursor / Claude Code 上の Claude Sonnet/Opus・GPT-5・Gemini 等の大型モデルだが、テストは Qwen3.5-4B-4bit（mlx-lm）への 1-shot 評価であり、拒否耐性の代理にならない。DR-0002 自身も「4B への変更後は再計測が必要」と明記したまま塩漬けになっていた。
2. **SKILL.md 本文を測っていない**: `tests/security/*-attacks.yaml` は SKILL.md 原文ではなく、yaml 側で再記述したテスト専用 system prompt を使用。拒否文言をテスト用 prompt に明記することで合格しやすく、実物の防御力を測っていなかった。
3. **エージェントループ・ツール呼び出し防御の欠落**: 実被害（`/etc/passwd` 書き込みなど）は最終的にエージェントのツール承認 UI やファイルシステム権限で止まるが、1-shot のチャット応答ではこれらを再現できない。
4. **アサーションが表層・正常系ゼロ**: `icontains-any` で `できません` / `お断り` 等の拒否語を拾うだけで、「できません」と返しつつ攻撃手順も出力するケースに脆弱。また、skill 本来の価値（例: planner が AC/Verification/Risks を揃えた 計画を作れるか）の正常系テストは 1 件も存在しなかった。
5. **CI に統合されていない**: [.github/workflows/ci.yml](../.github/workflows/ci.yml) は `lint` ジョブのみで、`test:security:*` はローカル実行専用。mlx-lm が Apple Silicon 専用のため CI に載せる見通しも立っておらず、リグレッション検知機構として機能していなかった。
6. **網羅率の穴**: `skills/pragmatic-architect/` には対応する yaml が無く、10 `skill` のうち 9 `skill` しか網羅されていなかった。
7. **脅威モデルの取り違え**: DR-0002 が本来想定していた脅威は「ブラックボックスな第三者 `skill` を取り込むときに悪意ある指示やコードが紛れる」こと。現行テストは逆向きで「こちらの `skill` がユーザーの攻撃指示を拒むか」を測っており、脅威モデルとレイヤーが合っていなかった。

検討したが採用しなかった代替案:

- **案 B: 実利用モデルへ差し替え + LLM-as-judge で正常系も測る**: Claude / GPT などの実利用モデルを プロバイダーにし、SKILL.md 原文を読み込ませ、`llm-rubric` 等で正常系（必須セクションの有無、AC の検証可能性など）も採点する構成。精度は上がるが、(a) 10 `skill` × 3〜8 ケースの再設計コスト、(b) `pragmatic-architect` の対話フローに対応する会話フィクスチャ設計、(c) API 費用と CI 統合のコスト管理が必要で、現時点で投資判断をするだけの運用ニーズが無い。
- **案 C: ブラックボックスな `skill` 検査器へリフォーム**: DR-0002 本来の脅威モデル（入稿された `skills/<name>/` を静的解析 + サンドボックス実行）に合わせて作り直す案。現行 yaml とはレイヤーが異なるため、採るなら一度撤去したうえで別スコープで起こすのが自然。

## 判断

現行の AI スキルセキュリティ検証ツールチェーン一式を撤去し、DR-0002 を置き換える。

撤去対象:

- `tests/security/` 配下の attack yaml（共通 + 9 `skill` 分）と `tests/security/run/` 配下の promptfoo / E2B 実行スクリプト
- `scripts/setup/` 配下の promptfoo / mlx-lm インストール・起動スクリプト
- [mise.toml](../mise.toml) の `mlx-lm:server` / `install:promptfoo` / `install:mlx-lm` / `setup:all` / `test:promptfoo` / `test:e2b` / `test:security:*` / `[env]` 節の `E2B_API_KEY` と `MLX_LM_MODEL`
- [package.json](../package.json) の `scripts.test` / `scripts.test:promptfoo` / `keywords` の `security`・`verification`・`promptfoo`・`mlx-lm` / `devDependencies` の `@e2b/code-interpreter`・`promptfoo`
- 運用ドキュメント `docs/ai-skill-security.md` と [README.md](../README.md) / [specs/document-boundaries.md](../specs/document-boundaries.md) からのリンク
- [.gitignore](../.gitignore) / [.prettierignore](../.prettierignore) / [\_typos.toml](../_typos.toml) の promptfoo / E2B / mlx / jailbreak 関連エントリ
- ルートの `promptfoo-output/` 生成物ディレクトリ

保留する方針:

- 将来もし再度セキュリティ検証が必要になったら、案 B（実利用モデル + LLM-as-judge）か案 C（ブラックボックス検査器）のいずれかを **新規 DR として起票し、別の計画 / PBI でゼロから設計する**。現行資産の継ぎ足しは行わない。
- 現行 yaml の設計意図や攻撃パターンは git 履歴から復元可能であるため、スナップショットを別途残さない。

## 影響

メリット:

- 実効性が乏しい検証資産（約 75KB の yaml + 実行スクリプト + ドキュメント + 依存 npm パッケージ）のメンテナンス負荷が消える
- mlx-lm / promptfoo / E2B の環境セットアップ（Python / Node / macOS 依存）が はじめ方から消え、新規コントリビューターの導入ハードルが下がる
- 「4B 再計測の宿題」「pragmatic-architect 未網羅」「CI 未統合」といった塩漬け課題が全て解消する
- `scripts/ci/run-shellcheck.sh` など CI 系スクリプトの走査対象が小さくなる

デメリット / 注意:

- 形式的なセキュリティ検証のメトリクス（合格率 100% 等）を失うため、「何かテストで担保されている」という心理的な安心感は無くなる。実運用上の防御の本丸はエージェント側（Cursor / Claude Code）のツール承認 UI とファイルシステム権限であるため、この撤去で実被害リスクが上がるわけではない、という前提を持つ必要がある。
- 将来 B / C 案を立ち上げる場合は、現行資産の継ぎ足しではなくゼロから設計し直すコストが必要になる。ただし現行資産の問題点（モデル乖離・SKILL.md 未使用・正常系欠落など）を引き継がずに済むため、結果的には合理的。
- [rules/when-to-create-decision-records.md](../rules/when-to-create-decision-records.md) / [rules/removing-dependencies.md](../rules/removing-dependencies.md) / [rules/document-consistency.md](../rules/document-consistency.md) / [rules/gitignore-vs-gitkeep.md](../rules/gitignore-vs-gitkeep.md) は promptfoo / mlx-lm / garak / E2B を「DR を残すべき事例」「依存削除の事例」として引用しているが、これらは過去事例としての教育的価値があるため本 DR では触らず残す。将来的にルール側を整理する場合は別の PBI / 計画 で扱う。
- 外部プロジェクトへの共有対象は [package.json](../package.json) の `files` フィールド（`bin/`, `skills/`, `rules/`, `COMMON.md`）のみで、`tests/` や `docs/` は共有対象外であるため、`npx github:choimake/twin-soul` で導入済みの利用先リポジトリへの影響はない。

## 関連する DR

- 置き換え元: [decisions/0002-ai-skill-security-toolchain.md](0002-ai-skill-security-toolchain.md)
