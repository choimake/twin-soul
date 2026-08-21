# [Skill Name] テストプロンプト

最初は 2〜3 件に絞る。

## セット確認

- Coverage: [このセットで見たい観点を自由に書く]
- Trigger balance: [should-trigger と should-not-trigger が混ざっているか]
- Near miss: [近い語を含むが対象外の prompt があるか]
- Diversity check: [同じ言い回しだけを変えた prompt 群になっていないか]
- Realism check: [実際のユーザーが言いそうな背景、file path、曖昧さがあるか]
- Overfitting risk: [このセットにだけ最適化しても意味がない箇所はどこか]

## プロンプト 1

- Type: [この prompt の観点を自由に書く]
- Should trigger: [true / false]
- 目的: [この prompt で確認したいこと]
- 理由: [この prompt を入れる理由]
- Prompt:

```text
[実際のユーザーが言いそうな依頼文]
```

- Success signals:
  - [期待する進め方]
  - [期待する出力]
  - [必要なら確認質問]
- Overfitting risk: [この例だけに合わせると何を見落とすか]

## プロンプト 2

- Type: [この prompt の観点を自由に書く]
- Should trigger: [true / false]
- 目的: [この prompt で確認したいこと]
- 理由: [この prompt を入れる理由]
- Prompt:

```text
[実際のユーザーが言いそうな依頼文]
```

- Success signals:
  - [期待する進め方]
  - [期待する出力]
  - [必要なら確認質問]
- Overfitting risk: [この例だけに合わせると何を見落とすか]

## プロンプト 3（必要なら）

- Type: [この prompt の観点を自由に書く]
- Should trigger: [true / false]
- 目的: [この prompt で確認したいこと]
- 理由: [この prompt を入れる理由]
- Prompt:

```text
[実際のユーザーが言いそうな依頼文]
```

- Success signals:
  - [期待する進め方]
  - [期待する出力]
  - [必要なら確認質問]
- Overfitting risk: [この例だけに合わせると何を見落とすか]

<!-- 同じ言い回しだけを変えた prompt 群にしない。 -->
<!-- skill 名や正解手順を露骨に埋め込まない。 -->
<!-- should-not-trigger は明らかに無関係なものではなく、近接 task や曖昧な依頼を混ぜる。 -->
