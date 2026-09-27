# template 選定

template 名は `github/gitignore` のファイル名（拡張子なし、大文字小文字は区別しない）を comma 区切りで渡す。たとえば `macos,visualstudiocode,node` のように取得する。

## よく使う template 名

- macOS: `macos`
- Windows: `windows`
- Linux: `linux`
- VS Code: `visualstudiocode`
- Vim: `vim`
- Emacs: `emacs`
- Node.js: `node`
- Python: `python`
- Go: `go`
- Rust: `rust`
- Java: `java`
- Terraform: `terraform`
- Docker 系の補助: docker 用の template は無いので、言語やツールごとの template と手書きルールで足す

`github/gitignore` 上のファイル名と会話中の表現が違うことがあるため、会話では自然な名前を受けて、取得時に正式な template 名へ正規化する。
