# draw.io MCP

この資料は `drawio-architecture` skill の MCP 導入案内とツールの使い分けです。描画ルールは [drawio-architecture-knowledge.md](drawio-architecture-knowledge.md)、完了判定は [visual-qa-checklist.md](visual-qa-checklist.md) です。

## いつ読むか

- 手順 3（MCP の有無を見て、無ければ案内するとき）
- 公式 stencil を足すとき

## 契約

案内が契約です。必須インストールではありません。

- 既にあるなら何もしません
- 無ければ導入手順を案内し、描画は止めません
- 入れられる環境なら入れてもよいです
- クライアントの有効化や設定ファイルの編集が要るなら案内だけにします
- エージェントは利用先の mcp.json を書いて導入完了にはしません
- 入れられなかったときは、アイコンなし・プレビューなしで `.drawio` を書き、案内した旨を残します

## 入れるもの

- 名前: `drawio`
- URL: `https://mcp.draw.io/mcp`
- 輸送: HTTP（remote）

stdio の `@drawio/mcp` は既定にしません。

## 案内する手順

APM がある利用先:

```bash
apm install --mcp drawio --transport http --url https://mcp.draw.io/mcp --target cursor,claude
```

subdirectory package（`choimake/twin-soul/skills/drawio-architecture`）を direct dependency にした利用先は、この MCP が既に書かれていることがあります。root collection だけで全 skill を入れた場合は付きません。

APM が無いとき（案内だけ。エージェントは設定ファイルを書きません）:

- Cursor: `.cursor/mcp.json` に `mcpServers.drawio.url = https://mcp.draw.io/mcp`
- Claude Code: `claude mcp add --transport http drawio https://mcp.draw.io/mcp`、または `.mcp.json` に同じ URL

## ツール

| ツール | 使うとき | 完成条件にするか |
| --- | --- | --- |
| `search_shapes` | 公式 stencil の style を取る。名前を推測すると公式と一致しない | しない。一致しない結果は捨て、連打しない |
| `create_diagram` | 描いた XML のプレビュー。縮小画像では重なりが見えない | しない。人のスクショが合格条件 |
