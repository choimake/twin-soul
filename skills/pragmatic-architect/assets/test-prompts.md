# Pragmatic Architect テストプロンプト

最初は 3 件に絞る。

## セット確認

- Coverage: 典型的な初期定義、ドキュメントとコードの乖離、理想論への反証の 3 軸をカバー
- Diversity check: 言語・規模・ユーザーの態度が異なる 3 件で、同じ言い回しの変形になっていない
- Overfitting risk: 特定言語やフレームワークへの最適化を避け、判断プロセスの質を見る

## プロンプト 1

- Type: 典型ケース — 新規プロジェクトで Core を定義したい
- 目的: 現状解析 → 仮説提示 → トレードオフ質問 → 草案化の基本フローが回ること
- 理由: skill の中核ユースケースが動かなければ MVP として成立しない
- Prompt:

```text
新しい TypeScript のバックエンド API プロジェクトのアーキテクチャを整理したい。
まだ設計文書はない。ディレクトリ構成はこんな感じ:

src/
  controllers/    # Express のルーティング
  services/       # ビジネスロジック
  models/         # Prisma のスキーマ定義とクライアント
  utils/          # 共通ユーティリティ

`src/services/orderService.ts` が `src/models/prismaClient.ts` を直接 import していて、
`src/controllers/orderController.ts` が `src/services/orderService.ts` の型を直接使っている。
テストは `src/services/` に対してだけ書いてあるが、Prisma のモックが必要な状態。

`.architecture-core.md` を作って、何を Core として守るか決めたい。
```

- Success signals:
  - ディレクトリ構造の解析結果を箇条書きで提示している
  - `services/` → `models/` の直接依存を汚染候補として指摘している
  - Core / Details の仮分類を提示している
  - 「Prisma 依存を Allowed Exception にするか、分離して Legacy Baseline にするか」のようなトレードオフ質問を返している
  - オープンクエスチョンではなく、事実つきの二択/三択になっている
  - 確認質問に `src/services/orderService.ts` や `src/models/prismaClient.ts` など具体的なファイルパスを含めている
- Overfitting risk: TypeScript / Prisma 固有の知識に寄りすぎると、他言語で使えなくなる

## プロンプト 2

- Type: 境界ケース — ドキュメントが古く、コードと意図が食い違う
- 目的: ドキュメントよりコードを事実として優先し、乖離を明示できること
- 理由: 実プロジェクトではドキュメントが古いのが常態。コードとドキュメントの食い違いを適切に扱えないと、誤った Core 定義を導く
- Prompt:

```text
Python の Django プロジェクトのアーキテクチャを見直したい。
README には「ヘキサゴナルアーキテクチャを採用し、domain/ がコアで ports/ と adapters/ で
外部を隔離している」と書いてある。

でも実際のコード:
- `domain/models.py` が `django.db.models.Model` を継承している
- `domain/services.py` が `adapters/email.py` を直接 import している
- `ports/` ディレクトリは空で、1ファイルも入っていない
- `adapters/payment.py` が `domain/models.py` の Django QuerySet を直接使っている
- テストは `tests/` にあるが、全部 Django の TestCase で DB 接続が必要

README の設計意図と実装がだいぶ違う。どこから手をつけるべき？
```

- Success signals:
  - README の記述とコードの実態の乖離を具体的に列挙している
  - コードを事実として優先すると明示している
  - `domain/models.py` の Django 依存を汚染として指摘している
  - 「README の意図を今から実現するか / 現状を Legacy Baseline にして段階的に直すか」のトレードオフ質問を返している
  - `ports/` が空である事実から、ヘキサゴナルの実現度を評価している
  - 確認質問に `domain/models.py` や `domain/services.py` など具体的なファイルパスを含めている
- Overfitting risk: Django 固有の知識に寄りすぎないこと。「ドキュメントと実態の乖離」という汎用的な判断力を見る

## プロンプト 3

- Type: 反証ケース — 理想論を押し通すユーザーへの反論と Legacy Baseline の提案
- 目的: 現実と乖離した要求に対し、反証を示して現実的な妥協案（Legacy Baseline）を提案できること
- 理由: 「全部きれいにしたい」は最も多い理想論で、これに無批判に従うと実現不可能な草案ができる。skill が反論し、段階的アプローチを提示できるかは品質の核心
- Prompt:

```text
Rails のモノリスなんだけど、クリーンアーキテクチャに全面移行したい。

構成:
app/
  models/         # ActiveRecord モデル 45 個
  controllers/    # 30 コントローラ
  services/       # 12 サービスクラス（Fat Model から切り出し中）
  jobs/           # Sidekiq ジョブ 8 個
  mailers/        # 5 メーラー
lib/
  api_clients/    # 外部 API クライアント 3 個

全部のモデルが ActiveRecord を継承していて、コントローラから直接 Model を呼んでるところも多い。
たとえば `app/controllers/orders_controller.rb` が `Order.where(...)` を直接呼んでいるし、
`app/models/order.rb` の中に配送料計算のビジネスロジックが 200 行くらいある。
`app/services/payment_service.rb` は最近切り出したけど、中で `User` と `Order` を直接参照している。
services/ は最近作り始めたばかりで、まだ 12 個しかない。
テストは model spec と request spec があるけど、service のテストは半分くらい。

理想的には domain/ を切り出して、ActiveRecord をアダプタにしたいけど、
まずは `.architecture-core.md` を作りたい。
全部きれいにリファクタしたいので、最終形を書いてほしい。
```

- Success signals:
  - 45 モデル × ActiveRecord 依存の規模感から、全面移行のコストを示している
  - 「全部きれいにリファクタしたい」に対して、反証（規模、テストカバレッジ、移行段階）を提示している
  - まず Legacy Baseline を広く取り、`services/` の拡充から始める段階的アプローチを提案している
  - 最終形だけでなく、現実的な第一歩を `.architecture-core.md` 草案に入れている
  - 「最終形を書いてほしい」に対し、現時点の Legacy Baseline と将来の目標を分けて提示している
  - いきなり断定せず、まず現状解析の証拠を出している
  - 確認質問に `app/models/order.rb` や `app/services/payment_service.rb` など具体的なファイルパスを含めている
- Overfitting risk: Rails 固有のパターンに寄りすぎないこと。「理想論 vs 現実」のトレードオフ判断力を見る
