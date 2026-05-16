# コードとコメントの内容を一致させる

## ねらい

コメントと実装が食い違うと、第三者は「コメントが正しいのか、コードが正しいのか」を判断できない。
結果として **レビューQAの増加** や **実装ミスの見逃し** を招く。

## チェック観点

- コメントが **現行の仕様/実装** と一致しているか
- 仕様変更でコードを直したのに、コメントが更新されず古い情報のままになっていないか
- 「読むだけで自明」な処理説明コメントが増えていないか（削除も選択肢）

## 指摘する基準（境界）

- コメントが実装と **矛盾** している、または **誤解を招く** 場合は 重大 として指摘する
- 迷う場合は「コメントを更新する」よりも、**コメントを削除してコード（命名/構造）で表現できないか** も選択肢として提示する

## 例

### 悪い例（コメントと実装が食い違う）

```java
// ユーザーがアクティブかどうかをチェックする
public boolean isActiveUser(User user) {
    // ユーザーの最終ログイン日時が、現在の日付から「一年以内」
    return user.getLastLogin().isAfter(LocalDate.now().minusMonths(6));
}
```

### 良い例（コメントを実装に合わせる／自明なら省略する）

```java
public boolean isActiveUser(User user) {
    return user.getLastLogin().isAfter(LocalDate.now().minusMonths(6));
}
```

もし要件が「一年以内」なら、コード側を修正する。

```java
public boolean isActiveUser(User user) {
    return user.getLastLogin().isAfter(LocalDate.now().minusYears(1));
}
```

## 補足

- コメントは「正しさのソース」になり得るため、放置すると負債化が早い
- 実装の変更が入ったときは、コメントも **同じPRで** 更新する（後回しにしない）
- 名前・ラベルと実体の食い違い（命名問題）は、[命名と実行内容を一致させる](./keep-names-in-sync-with-behavior.md) を参照する
