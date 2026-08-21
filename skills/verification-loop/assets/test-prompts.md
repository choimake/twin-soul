# verification-loop テストプロンプト

最初は 2〜3 件に絞る。

## セット確認

- Coverage: 基準確認、実装×独立レビューの分担、モデル未指定時の確認
- Trigger balance: should-trigger と should-not-trigger が混ざっているか
- Near miss: 通常の単発レビュー依頼が対象外になっているか
- Diversity check: 同じ言い回しだけを変えた prompt 群になっていないか
- Realism check: 実際のユーザーが言いそうな背景と合格基準があるか
- Overfitting risk: このセットにだけ最適化しても意味がない箇所はどこか

## プロンプト 1

- Type: 明示的な検証ループ依頼（基準あり、skill 名なし）
- Should trigger: true
- 目的: skill 名を明示しない依頼でも、基準提示後に実装→独立レビューへ進むか
- 理由: 本 skill の主用途。undertrigger を避けられているかの確認も兼ねる
- Prompt:

```text
README に新機能の導入例を1段落追加してほしい。実装担当とレビュー担当を分けて、合格するまで直してほしい。
合格基準:
- README の既存の説明と矛盾しない
- mise run ci:lint が通る
品質ゲート: review
実装用のモデルとレビュー用のモデルは、それぞれ私が指定する識別子を使ってほしい。
```

- Success signals:
  - 着手前に確定した基準・ゲート・モデルを箇条書きで提示する
  - 実装とレビューを別サブエージェントに委譲する方針を取る
  - メインエージェントが自分で本文を書き始めない
- Overfitting risk: README 以外の成果物でも同じ委譲手順になること

## プロンプト 2

- Type: 基準・モデル未提示
- Should trigger: true
- 目的: 着手前に確認質問へ入るか
- 理由: 合格基準とモデル解決の手順を確認する
- Prompt:

```text
実装と独立レビューを分けて、合格するまでループしてほしい。
対象は skills/verification-loop の説明文の改善。
```

- Success signals:
  - 完了条件・機械的検証・レビュー観点・品質ゲート・モデルを確認する
  - config/defaults.yaml を読む、または引数未指定であることに言及する
  - 確認前に実装委譲へ進まない
- Overfitting risk: 確認項目の文言固定に過適合しないこと

## プロンプト 3

- Type: 通常の単発レビュー（対象外）
- Should trigger: false
- 目的: 単発レビューを verification-loop に引き寄せないこと
- 理由: description の境界確認
- Prompt:

```text
この PR の差分をレビューして。改善点ある？
```

- Success signals:
  - verification-loop の実装×レビューループを開始しない
  - 通常のコードレビュー skill や通常レビュー手順へ寄せる
- Overfitting risk: 「レビュー」という語だけで常に拒否しないこと（検証ループ明示時は trigger する）

## プロンプト 4（任意・skill 名明示）

- Type: skill 名を明示した検証ループ依頼
- Should trigger: true
- 目的: skill 名を直接指定した依頼でも、プロンプト 1 と同じ委譲手順に入るか
- 理由: undertrigger 側（プロンプト 1）と対になる確認。skill 名依存で手順が変わらないことを見る
- Prompt:

```text
verification-loop skill を使って、設定ファイルのコメントを見直してほしい。実装とレビューは別担当に分けて、合格するまでループしてほしい。
```

- Success signals:
  - プロンプト 1 と同じ着手前の基準確認・委譲手順を取る
  - skill 名の有無で確認項目や委譲方針がぶれない
- Overfitting risk: このプロンプトの文言だけに合わせて、skill 名なし依頼への対応が弱くならないこと
