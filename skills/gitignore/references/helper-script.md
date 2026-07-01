# helper script

この skill では、`gitignore.io` の一覧取得や template 取得に加えて、リポジトリから候補を洗い出す処理も繰り返し発生しやすく、処理も比較的安定しているため `scripts/fetch-gitignore.sh` を同梱する。

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

この script は、space 区切りでも comma 区切りでも受け取り、template 名を lower-case に正規化して `gitignore.io` へ渡す。`detect` は comma 区切りの template 候補一覧を返し、`auto` は推定結果に optional な追加 template をマージして本文を取得する。

## script を入れた理由

この skill の中心は `.gitignore` の判断だが、`gitignore.io` から template を取ってくる部分と、リポジトリから候補を洗い出す部分は毎回ほぼ同じである。会話だけで毎回 API 形式と検出手順を説明するより、軽い helper script に寄せた方が再現しやすく、反復コストも下がる。
