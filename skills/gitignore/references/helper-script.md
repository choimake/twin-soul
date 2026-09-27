# helper script

この skill では、`github/gitignore` の一覧取得や template 取得に加えて、リポジトリから候補を洗い出す処理も繰り返し発生しやすく、処理も比較的安定しているため `scripts/fetch-gitignore.sh` を同梱する。

## 使い方

template 一覧:

```bash
bash skills/gitignore/scripts/fetch-gitignore.sh list
```

template 候補の自動推定:

```bash
bash skills/gitignore/scripts/fetch-gitignore.sh detect .
```

自動推定に追加 template を足す:

```bash
bash skills/gitignore/scripts/fetch-gitignore.sh detect . terraform
```

template 取得:

```bash
bash skills/gitignore/scripts/fetch-gitignore.sh macos visualstudiocode node
```

自動推定してそのまま取得:

```bash
bash skills/gitignore/scripts/fetch-gitignore.sh auto .
```

この script は、space 区切りでも comma 区切りでも受け取り、template 名を lower-case に正規化し、cache に clone した `github/gitignore` の `<名前>.gitignore` を大文字小文字を区別せずに探す（root、`Global/`、`community/` の順）。`detect` は comma 区切りの template 候補一覧を返し、`auto` は推定結果に optional な追加 template をマージして本文を取得する。本文の先頭には取得元の commit を出すので、報告にはその commit を書く。

## 取得元と cache

- 取得元は `https://github.com/github/gitignore.git`。初回だけ `git clone --depth 1` し、以後は cache を読む
- cache の場所は `GITIGNORE_TEMPLATES_DIR`（既定: `${XDG_CACHE_HOME:-~/.cache}/twin-soul/github-gitignore`）
- 最新のテンプレートにしたいときは cache ディレクトリを消して再実行する
- clone が途中で止まるなどして cache が壊れていると、その旨を出して終了コード 1 で止まる。cache ディレクトリを消して再実行する
- 見つからない template 名があると、名前を挙げて終了コード 1 で止まる。`list` で名前を確かめる

## script を入れた理由

この skill の中心は `.gitignore` の判断だが、テンプレートを取ってくる部分と、リポジトリから候補を洗い出す部分は毎回ほぼ同じである。会話だけで毎回取得方法と検出手順を説明するより、軽い helper script に寄せた方が再現しやすく、反復コストも下がる。
