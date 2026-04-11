# Markdown to HTML Converter

Markdownファイルを、画像（Base64）やCSSが埋め込まれた**単一の自己完結型HTMLファイル**に変換するCLIツールです。ローカルでの配布や共有に最適です。

## 特徴

- **単一ファイル出力**: 画像をBase64として埋め込み、外部リソース依存のないHTMLを生成（共有が容易）。
- **高度なコードブロック**: Highlight.jsによるシンタックスハイライトと、ワンクリック「コピー」ボタンを自動付与。
- **Colabリンク自動変換**: `.ipynb` を指すリンクを検知し、Google Colabの起動バッジ付きリンク（別タブで開く）へ自動変換。
- **カスタム記法**: `{{テキスト}}` と記述すると、改行を防ぐ `nowrap` スパンに変換。

## セットアップ

依存管理に `uv` を使用します。

```bash
uv sync
```

## 使い方

### 基本的な変換
入力ファイル名に基づいて `document.html` が生成されます。

```bash
uv run main.py document.md
```

### カスタムCSSを埋め込む
複数のCSSファイルを指定して埋め込むことができます。

```bash
uv run main.py document.md -c style.css theme.css
```

### 出力ファイルの指定と詳細ログ
`-o` で出力先を指定し、`-v` で変換プロセスの詳細なログを確認します。

```bash
uv run main.py document.md -o docs/index.html -v
```

### HTMLタグの除外処理
指定したタグ（およびその中身）を出力HTMLから削除します。

```bash
uv run main.py document.md -e hr div
```

---

すべてのオプションを確認するにはヘルプを参照してください：

```bash
uv run main.py --help
```
