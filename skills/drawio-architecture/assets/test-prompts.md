# drawio-architecture テストプロンプト

最初は 2〜3 件に絞る。

## セット確認

- Coverage: 新規の構成図描画、スクショ付きの視覚修正、事実の正本の無い図
- Trigger balance: should-trigger と should-not-trigger が混ざっている
- Near miss: 「構成図」という語はあるが、事実の正本も `.drawio` も求めていない一般フローチャート依頼が対象外になっている
- Diversity check: 同じ言い回しだけを変えた prompt 群になっていない
- Realism check: `docs/architecture/` やスクショ添付など、実務で出やすい具体がある
- Overfitting risk: 特定プロダクトのファイル名や製品名に合わせると、他リポジトリで使えない

## プロンプト 1

- Type: 典型（構成図の新規描画）
- Should trigger: true
- 目的: skill 名を言わない依頼でも、事実の正本と `.drawio` 成果物へ進むか
- 理由: 本 skill の主用途。undertrigger を避けられているかの確認も兼ねる
- Prompt:

```text
docs/architecture/ にある構成の yaml を正本にして、サービス間のリクエスト経路を draw.io の図にしてほしい。最終成果物は .drawio でリポジトリに残したい。
```

- Success signals:
  - 事実の正本と出力 `.drawio` パスを確認してから描く
  - draw.io MCP が無ければ導入手順を案内し、描画は止めない。案内であり、mcp.json を書いて導入完了にはしない
  - 非圧縮の native draw.io を書く
  - 完了前に全体と潰れている箇所のスクショを求める
- Overfitting risk: `docs/architecture/` 以外の正本パスでも、同じ確認と成果物判定になること

## プロンプト 2

- Type: 視覚確認（スクショ付き修正）
- Should trigger: true
- 目的: 見た目修正の依頼で、事実を触らず座標・寸法・ラベルだけ直すか
- 理由: スクショ無しの座標推測を避け、視覚確認ループが起動するかを見る
- Prompt:

```text
構成図をデスクトップの draw.io で開いた全体スクショと、右寄りの箱で線が文字に被っている部分スクショを貼る。見た目だけ直して。中身のサービス構成は変えないで。
```

- Success signals:
  - スクショを見てから座標・ウェイポイント・カード寸法・ラベル位置だけ直す
  - 事実の正本やノード追加に手を出さない
  - 2 周から 3 周で止め、公式 stencil を同じ周回に混ぜない
- Overfitting risk: 特定の交差パターンだけ直す手順に固定しないこと。潰れている箇所が違っても同じ制約で直すこと

## プロンプト 3

- Type: 近接（事実の正本の無い一般フローチャート）
- Should trigger: false
- 目的: 「構成図」という語があっても、事実の正本も `.drawio` も求めていないときは本 skill の成果物に進まないか
- 理由: 一般フローチャート / UI 下書きと、構成図の境界を見る
- Prompt:

```text
新しい機能の構成図をざっと見たい。仕様書も構成の yaml もまだ無い。チャットに処理フローと画面遷移の下書きを出して。
```

- Success signals:
  - 構成図の `.drawio` 作成に入らない
  - 事実の正本が無い一般フローチャート / UI 下書きとして切り分ける
  - 本 skill のデザインシステムやスクショ周回を必須化しない
- Overfitting risk: 図形式の名前だけで拒否せず、事実の正本がある構成図の下書き相談までは拾えること

<!-- 同じ言い回しだけを変えた prompt 群にしない。 -->
<!-- skill 名や正解手順を露骨に埋め込まない。 -->
<!-- should-not-trigger は明らかに無関係なものではなく、近接 task や曖昧な依頼を混ぜる。 -->
