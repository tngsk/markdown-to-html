# Mono Doc

Markdownを、ローカル画像やスタイルが埋め込まれた単一の自己完結型HTMLファイル（Single-File HTML）および高精度PDFに変換するCLIツールです。16pxの繊細なドットグリッドによる知的で構造的なキャンバス上に、プロジェクターでのプレゼンテーションから配布用ドキュメントまで、オフライン環境で完全動作する成果物を生成します。

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

### 3×3 デザイントークン & 16px ドットグリッド

Mono Docは、16pxのドットグリッドを基盤とした3段階の流体スケール（Typography Trinity / Spacing Trinity）を採用しています。

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
- 背景基盤: 16px四方の精緻なドットグリッドがコンテンツ境界（CSS Grid）と数理的に連動します。

### テキスト強調（見出しマーカー・インラインマーカー・アンダーライン）

Mono Space直系の見出しマーカー（文字ベースラインに重なる72%〜91%の蛍光帯）は、属性リスト記法（`{.marker}`）で見出しに指定できます。Space 3トーン（`normal`, `ai`, `warning`）およびDoc 5カラー（`yellow`, `pink`, `green`, `cyan`, `orange`）に対応しています。

```markdown
# 通常章見出し {.marker}
## AI関連見出し {.marker-ai}
### 警告事項 {.marker-warning}
```

本文中の蛍光ペン風マーカー強調（`== ==`）およびアンダーライン強調（`++ ++`）も利用できます。波括弧でトーン・カラー（`ai`, `warning`, `yellow`, `pink`, `green`, `cyan`, `orange`）を指定可能です（省略時は `yellow`）。

```markdown
これは ==デフォルト黄色マーカー== です。
これは ==AIトーン紫マーカー=={ai} です。
これは ==ピンクマーカー=={pink} です。
これは ++シアン下線++{cyan} です。
```

### 主要コンポーネント

| コンポーネント | 構文例 |
|---|---|
| レイアウト | `@[hbox]{.gap-group}\n::: 左\n:::\n::: 右\n:::\n@[/hbox]` |
| 比較（2/3要素） | `@[compare](gap: "group")\n::: Before\n従来\n:::\n::: After\n新提案\n:::\n@[/compare]` |
| セクション | `@[section](padding: "group")\n...コンテンツ...\n@[/section]` |
| ズーム | `@[zoom]()` または `-p presentation` |
| コードブロック | 通常のコードブロック（```）から自動変換 |
| ダイアグラム | `@[mermaid]\ngraph TD; A-->B;\n@[/mermaid]` |
| リンクカード | `@[link: タイトル](url: "https://example.com")`（TTLキャッシュ対応） |
| テーマ切替 | `@[theme: corporate]()` |

詳細なコンポーネント仕様や教育系パッケージ（`@interactive`）については [doc/SKILL.md](doc/SKILL.md) を参照してください。

## プレゼンテーション操作

- `P`: プレゼンタービュー起動（開発中: 別ウィンドウで縮小プレビュー・トークスクリプト・スライド位置同期を表示）
- `B`: 蛍光ブラシ描画モード切替（画面上への手書きアノテーション、`Esc` で解除）
- `D`: アンビエント没頭フォーカス（周辺減光）とフラット表示の切り替え
- `J` / `K`（または `↓` / `↑`）: 水平線（`---`）がある場合はスライド間、ない場合は章・節（H1/H2）への自動スクロール
- `Z`（または要素クリック）: ホバー中要素の全画面ズーム（`Esc` で解除）
