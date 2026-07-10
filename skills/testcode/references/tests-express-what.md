# テストは What を示す

この資料は、テストコードが担う情報の層を整理する。
テストは実装手順（How）ではなく、期待する振る舞い（What）を示す。

## ねらい

テスト名・ケース・assertion を読めば、保証している振る舞いが分かるように書く。
実装の内部手順を写したテストは、リファクタで壊れやすい。仕様の説明にもなりにくい。

## 判断基準

- テスト名やケース名が、入力条件と期待結果（What）を表しているか
- assertion が、利用者から観測できる振る舞いまたは契約を検証しているか
- private な手順や一時変数の値への依存が、検証の主眼になっていないか

## 良い例と悪い例

### 悪い例（How を写している）

```text
should_call_validate_then_save_then_publish
```

内部呼び出し順の検証が主眼である。利用者にとっての成果が分からない。

### 良い例（What を示している）

```text
should_reject_save_when_user_lacks_write_permission
```

権限がないときに保存を拒否する振る舞いが、名前から読める。

## 生成・評価への使い方

- `generate`: ケース一覧を期待振る舞いの言葉で先に書き、その後でテスト本文へ落とす
- `evaluate` / `improve`: 通るが実装詳細に依存しているテストを、What 視点へ書き換える候補とする

関連:

- ケース列挙の手順は [test-generation.md](test-generation.md)
- assertion の強さは [test-evaluation.md](test-evaluation.md)
- 実装詳細への密結合は [test-smells.md](test-smells.md) の観点と合わせて見る
