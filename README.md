# Mono

Markdownを、ローカル画像やスタイルが埋め込まれた単一の自己完結型HTMLファイル（Single-File HTML）に変換するCLIツールです。プロジェクターでのプレゼンテーションから配布用ドキュメントまで、基本コンテンツはオフライン環境で完全動作します（外部画像や一部CDN連携機能を除く）。

## インストール

```bash
uv sync
```

## 使い方

```bash
# 基本変換（入力ファイル名.html を出力。同階層に dist/ がある場合は dist/ 内に出力）
uv run main.py document.md

# プレゼンテーション用（オートズーム mono-zoom を有効化）
uv run main.py slides.md -o output.html -p presentation

# 静的ドキュメント用（Zero-JS 出力）
uv run main.py doc.md -o output.html -p minimal

# PDF 書き出し（単一縦長PDFを出力）
uv run main.py document.md -o document.html --pdf document.pdf

# データ収集・同期サーバー起動（オプション）
uv run python -m src.server

# バージョン確認
uv run main.py --version
```

## 記法

### 3×3 デザイントークン

```markdown
# 看板見出し {.text-display}

標準本文テキスト
{: .text-body}

凝縮注釈テキスト
{: .text-compact}

@[hbox]{.gap-group}
:::
左カラム
:::
:::
右カラム
:::
@[/hbox]
```

- タイポグラフィ: `.text-display`（大見出し）、`.text-body`（本文）、`.text-compact`（注釈・カラム内）
- 余白: `.gap-flow`（均一112px）、`.gap-group`（64px）、`.gap-item`（23px）

### テキスト強調（マーカー・アンダーライン）

蛍光ペン風のマーカー強調（`== ==`）およびアンダーライン強調（`++ ++`）が利用できます。波括弧で5色のカラー（`yellow`, `pink`, `green`, `cyan`, `orange`）を指定可能です（省略時は `yellow`）。

```markdown
これは ==デフォルト黄色マーカー== です。
これは ==ピンクマーカー=={pink} です。
これは ++デフォルト黄色下線++ です。
これは ++シアン下線++{cyan} です。
```

### 主要コンポーネント

| コンポーネント | 構文例 |
|---|---|
| レイアウト | `@[hbox]{.gap-group}\n::: 左\n:::\n::: 右\n:::\n@[/hbox]` |
| セクション | `@[section](padding: "group")\n...コンテンツ...\n@[/section]` |
| ズーム | `@[zoom]()` または `-p presentation` |
| コードブロック | 通常のコードブロック（```）から自動変換 |
| ダイアグラム | `@[mermaid]\ngraph TD; A-->B;\n@[/mermaid]` |
| リンクカード | `@[link: タイトル](url: "https://example.com")` |
| テーマ切替 | `@[theme: corporate]()` |

詳細なコンポーネント仕様や教育系パッケージ（`@interactive`）については [doc/SKILL.md](doc/SKILL.md) を参照してください。

## プレゼンテーション操作

- `P`: プレゼンタービュー起動（開発中: 別ウィンドウで縮小プレビュー・トークスクリプト・スライド位置同期を表示）
- `B`: 蛍光ブラシ描画モード切替（画面上への手書きアノテーション、`Esc` で解除）
- `D`: アンビエント没頭フォーカス（周辺減光）とフラット表示の切り替え
- `J` / `K`（または `↓` / `↑`）: 水平線（`---`）がある場合はスライド間、ない場合は章・節（H1/H2）への自動スクロール
- `Z`（または要素クリック）: ホバー中要素の全画面ズーム（`Esc` で解除）
