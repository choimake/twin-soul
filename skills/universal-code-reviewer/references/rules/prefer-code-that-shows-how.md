# コードは How を示す

## ねらい

本番コードは、処理の進め方（How）を命名・分割・制御構造で読めるようにする。
How をコメントで繰り返すと、実装とコメントの二重管理になる。結果として、実装とコメントがずれやすい。

## チェック観点

- 関数名・変数名・型名から、処理の役割と手順の骨格が読めるか
- 長い関数や深いネストが、手順の把握を妨げていないか
- コメントが、コードを読めば分かる How の言い換えになっていないか

## 指摘する基準（境界）

- 名前や構造を直せば読めるのに、コメントで How を補っている場合は、命名・分割を優先して提案する
- 構造だけでは追いにくい回避策や複雑な制御は、本ルールではなく `write-intentful-comments.md`（Why not）で扱う

## 例

### 悪い例（How をコメントで繰り返している）

```java
// ユーザーを取得して、権限を確認してから保存する
public void save(User user) {
    User current = userRepository.find(user.getId());
    if (!current.hasPermission(Permission.WRITE)) {
        throw new ForbiddenException();
    }
    userRepository.save(user);
}
```

コメントが処理手順の言い換えに留まっている。命名や分割で示せる情報になっていない。

### 良い例（命名と分割で How を示す）

```java
public void saveIfWritable(User user) {
    User current = requireWritableUser(user.getId());
    userRepository.save(user);
}

private User requireWritableUser(String userId) {
    User current = userRepository.find(userId);
    if (!current.hasPermission(Permission.WRITE)) {
        throw new ForbiddenException();
    }
    return current;
}
```

## 補足

- このルールは「コードで How を示す」ことを扱う。コメントに残す内容は `write-intentful-comments.md` を参照する
- テストが示す層（What）は、本ルールの対象外である
