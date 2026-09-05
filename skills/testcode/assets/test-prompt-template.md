# Testcode テストプロンプト

最初は 2〜3 件に絞る。

## セット確認

- Coverage: `generate` `evaluate` `improve` の 3 モードがそれぞれ自然に使い分けられるか
- Diversity check: 新規生成、既存テスト評価、改善提案で観点が分かれているか
- 過適合リスク: Python や 1 つのテストフレームワークだけに最適化しすぎていないか

## プロンプト 1

- Type: 典型ケース
- 目的: 対象コードの理解からケース整理を経て、自然にテスト生成へ進めるかを確認する
- 理由: いきなり本文を書かず、対象理解 → ケース整理 → 本文、の順を取れるか見たい
- Prompt:

```text
この関数の pytest 用テストを追加したいです。正常系だけじゃなくて境界値も入れてほしいので、まず必要なケースを整理してから `tests/` 配下に入れられる形で提案してください。対象は `@src/utils/slugify.py` です。
```

- Success signals:
  - 対象コードの責務、入出力、境界値を先に整理する
  - ケース一覧を出してから、保存できる形のテスト案へ進む
  - 既存テストがあれば重複を避ける
  - モックばかり・実装の鏡・タイミング依存のテストを足していない
- 過適合リスク: pytest 固有の書き方だけに寄りすぎると、他言語や他フレームワークへ一般化しにくい

## プロンプト 2

- Type: 境界ケース
- 目的: 既存テストの pass/fail だけでなく、assertion の弱さや test smell を評価できるかを確認する
- 理由: LLM 生成テストは「通るが弱い」ことが多く、`evaluate` モードの質が重要
- Prompt:

```text
AI に書かせたテストがあるんですが、これで本当に十分か不安です。`@tests/services/test_pricing.py` を見て、弱い assertion、抜けてる edge case、test smell があれば優先度つきで教えてください。coverage が高いならそれで十分かも含めて判断してほしいです。
```

- Success signals:
  - 実行可否だけでなく assertion の具体性を評価する
  - `Assertion Roulette` や `Mystery Guest` などの smell を必要に応じて指摘する
  - エラー・ログ・例外メッセージの部分一致を弱い assertion として見つけ、必要なら全文一致を提案する
  - coverage だけでは十分と断定しない
- 過適合リスク: smell 名の列挙だけに寄ると、なぜ問題かと改善案が弱くなる

## プロンプト 3

- Type: 改善提案
- 目的: surviving mutant や弱い条件分岐を起点に、追加すべきテストを具体化できるかを確認する
- 理由: `improve` モードでは「何を足せば強くなるか」が必要で、抽象論だけでは足りない
- Prompt:

```text
mutation testing で `src/domain/discount.ts` の比較条件まわりに surviving mutant が残りました。`@src/domain/discount.ts` と `@tests/domain/discount.test.ts` を見て、どのケースを追加すると落とせそうか、テスト名レベルまで具体的に提案してください。
```

- Success signals:
  - surviving mutant から逆算して不足ケースを特定する
  - テスト名や入力例を含む具体的な改善案を返す
  - 必要なら既存 assertion を狭くする提案も含める
- 過適合リスク: mutation testing 前提に寄りすぎると、未導入のプロジェクトで使いにくくなる

## プロンプト 4

- Type: generate で悪いテストを拒否する
- 目的: モックばかり・実装の鏡・タイミング依存ならテストを増やさないこと
- 理由: 通るが弱いテストを足すくらいなら、足さない方が安全
- Prompt:

```text
`@src/orders/submit.ts` のユニットテストを書いて。DB と外部 API は全部モックで、
内部の validate → save → publish の呼び出し順も assert して。
あと sleep(50) してから結果を見てほしい。
```

- Success signals:
  - モックばかり、実装の鏡、タイミング依存を足さないと判断する
  - テスト本文を量産せず、捨てたケースと理由を返す
  - 代わりの検証（既存テスト、手動手順、より狭い振る舞いケース）を短く返す
- 過適合リスク: `sleep` の語だけで拒否せず、検証の主眼が何かを見て判定すること

<!-- 同じ言い回しだけを変えた prompt 群にしない。 -->
<!-- skill 名や正解手順を露骨に埋め込まない。 -->
