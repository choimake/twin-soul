# .gitignoreと.gitkeepの使い分け

## 目的

空のディレクトリや生成物ディレクトリの扱いを明確にし、`.gitignore` と `.gitkeep` を正しく使い分ける。

## 判断基準

**「空のディレクトリにファイルが追加されたとき、そのファイルをGit管理対象に含めたいか？」**

- **含めたい** → `.gitkeep` を使う
- **含めたくない** → `.gitignore` を使う

## パターン別の使い分け

### 1. ビルド成果物・生成物ディレクトリ → `.gitignore`

**例:**

- `build/` - コンパイル結果
- `dist/` - 配布パッケージ
- `.agents/skills/` - APM の Cursor 向け展開物
- `.claude/skills/` - APM の Claude Code 向け展開物
- `.cursor/skills/` - 旧 Cursor パス互換の展開物
- `apm_modules/` - APM のローカルキャッシュ
- `.cursor/plans/` - Cursor のローカル plan 作業領域
- `memory/` - エージェント作業のローカル記録

**設定例:**

```.gitignore
# APM 展開物
.agents/skills/
.claude/skills/
.cursor/skills/

# APM の local cache
apm_modules/

# Agent local working memory（正本ではない）
memory/
```

**理由:**

- 生成物はGit管理不要（再生成可能）
- チーム間で内容が異なる（環境依存）
- ファイルサイズが大きい

### 2. 空の構造ディレクトリ → `.gitkeep`

**例:**

- `templates/` - 空のテンプレートディレクトリ
- `logs/` - ログファイルを配置する予定の空ディレクトリ
- `uploads/` - アップロードファイルの配置先（空の状態で構造を保持）

**設定例:**

```bash
mkdir -p templates
touch templates/.gitkeep
```

```.gitignore
# ログファイルは除外するが、ディレクトリ構造は保持
logs/*
!logs/.gitkeep
```

**理由:**

- ディレクトリ構造をリポジトリに含めたい
- アプリケーションがディレクトリの存在を前提にしている
- チーム全員が同じディレクトリ構造を共有すべき

### 3. 一部のファイルだけ管理対象にする → `.gitignore` + `!` パターン

**例:**

- `config/` - 設定ファイルの一部だけ管理

```.gitignore
# config/配下は全て除外
config/*

# ただしサンプルファイルだけは含める
!config/.gitkeep
!config/config.example.json
```

## 例: APM 展開物

APM の展開先は `skills/` から再生成できるため、Git 管理対象にしない。

**誤り:**

```.gitignore
.agents/skills/*
!.agents/skills/.gitkeep
```

```bash
touch .agents/skills/.gitkeep
```

**正しい:**

```.gitignore
.agents/skills/
.claude/skills/
.cursor/skills/
```

展開先ディレクトリは `apm install` で作られるため、`.gitkeep` は不要。

## よくある間違い

### 生成物ディレクトリに `.gitkeep` を置く

```bash
# APM 展開物なので .gitkeep は不要
touch .agents/skills/.gitkeep
```

### `.gitignore` だけで管理

```.gitignore
.agents/skills/
```

### 空ディレクトリを `.gitignore` で除外してしまう

```bash
# templates/は空の構造ディレクトリだが、.gitignoreで除外してしまう
echo "templates/" >> .gitignore
```

### `.gitkeep` で構造を保持

```bash
touch templates/.gitkeep
```

## 参考

- [Git公式ドキュメント - gitignore](https://git-scm.com/docs/gitignore)
- `.gitkeep` はGit公式の機能ではなく、慣習的な名前（`.keep`, `.gitdummy` 等でも可）
