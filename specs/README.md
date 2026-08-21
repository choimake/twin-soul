# Specs

このディレクトリは、`twin-soul` の現在の構成・導入方法・運用仕様を説明する参照ドキュメントを置く。

## 置くもの

- skill の導入仕様
- APM 移行や配布方式の現在形
- このリポジトリ内部のドキュメント構成や運用仕様
- 初見の作業者が現在の仕組みを確認するための事実

## 置かないもの

- 作業時に守る横断ルール（`rules/` に置く）
- 判断理由や過去の選択肢の履歴（`decisions/` に置く）
- 外部プロジェクトへ単体配布する workflow（`skills/` に置く）

## 代表文書

- [document-boundaries.md](document-boundaries.md) - ドキュメントと再利用資産の境界
- [installing-shared-skills.md](installing-shared-skills.md) - skill の導入仕様
- [migrating-to-apm.md](migrating-to-apm.md) - APM への移行手順

## 迷ったとき

`specs/` は「現在どうなっているか」を書く場所であり、「どう守るべきか」や「なぜ決めたか」を主目的にしない。判断に迷う場合は [document-boundaries.md](document-boundaries.md) を先に確認する。
