# テスト評価

この資料は `testcode` skill の `evaluate` と `improve` 観点をまとめたものである。生成元を問わず、既存テストや提案されたテストの品質を判断するときに使う。

## 評価設計

テスト品質の評価は、次の 4 つを分けて考える。

- 成功条件:
  - そのテストで何を保証したいか。例: 戻り値、例外、状態更新、イベント発火
- ケース集合:
  - 典型ケース、境界値、異常系、回帰防止ケースが入っているか
- 判定方法:
  - 実行が通るか、assertion が狭く具体的か、coverage や mutation の結果はどうか
- 継続評価:
  - prompt やテストを変えたあとで、同じ観点を再確認できるか

「なんとなく良さそう」で判断せず、少数でもよいので固定の確認観点を持つ。

## 良いテストの条件

- self-checking:
  - 人が目視で判断しなくても pass/fail が決まる
- repeatable:
  - 同じ条件なら毎回同じ結果になる
- isolated:
  - DB、FS、ネットワーク、時刻、sleep に不必要に依存しない
- fast:
  - 小さな変更のたびに気軽に回せる

加えて、assertion は広くぼかさず、失敗時に何が壊れたか分かる狭い形を優先する。
エラー・ログ・例外メッセージが仕様の一部なら、部分一致ではなく全文一致で固定する。詳細は [message-assertions.md](message-assertions.md) を参照する。

## `evaluate` の進め方

次の順で見る。

1. テストは self-checking か。実行して終わりになっていないか
2. assertion は狭く具体的か。通ればよい雑な比較になっていないか
3. メッセージ出力を検証する場合、最終的な全文をテストから読めるか
4. 正常系だけでなく境界値、例外、空入力、無効入力を見ているか
5. 外部依存に寄りすぎていないか。unit test なのに DB、FS、sleep、ネットワークへ触れていないか
6. coverage が高いだけで満足していないか。必要なら mutation testing を勧める

## `improve` の進め方

次の入力を改善の起点にしてよい。

- surviving mutant
- pass はするが assertion が広いテスト
- edge case 漏れ
- `Assertion Roulette` などの test smell
- 過剰な fixture や不要な mocking

改善提案では、`どの弱さを埋めるのか` をケース名付きで返す。単に「coverage を上げる」では終わらせない。

## coverage の扱い

coverage は有益だが、それだけでは assertion の弱さを見抜けない。

- どこを通ったかを見るには有効
- 漏れている分岐の洗い出しに向く
- 「本当にバグを検出できるか」は別観点で見る必要がある

coverage 偏重になりそうなときは、mutation testing や具体的な assertion の見直しを追加で勧める。
