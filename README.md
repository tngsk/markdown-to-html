# Markdown to HTML Converter

Markdownファイルを、画像（Base64）やCSSが埋め込まれた**単一の自己完結型HTMLファイル**に変換するCLIツールです。ローカルでの配布や共有に最適です。

## 特徴

- **単一ファイル出力**: 画像をBase64として埋め込み、外部リソース依存のないHTMLを生成（共有が容易）。
- **高度なコードブロック**: Highlight.jsによるシンタックスハイライトと、ワンクリック「コピー」ボタンを自動付与。
- **Colabリンク自動変換**: `.ipynb` を指すリンクを検知し、Google Colabの起動バッジ付きリンク（別タブで開く）へ自動変換。
- **カスタム記法**: `{{テキスト}}` と記述すると、改行を防ぐ `nowrap` スパンに変換。
- **画像の最適化と遅延読み込み**: 画像をWebPに変換・SVGをインライン化し、非同期注入戦略によって遅延読み込みを行うことでパフォーマンスを最適化。
- **ファイルサイズ検証**: 出力ファイルのサイズを検証し、30MBを超える場合は警告・停止（`--force` でバイパス可能）。
- **セキュリティ設定（CSP）**: `config.toml` から設定を読み込み、Content-Security-Policyタグを自動設定。
- **Web Components対応**: 外部依存なしのVanilla JSによるWeb Componentsの埋め込みに対応。（`mono-icon`、`mono-spacer`、`mono-sound`、`mono-brush`、`mono-layout` など）

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

### カスタムテンプレートを使用する
カスタムのHTMLテンプレートを指定して変換します。

```bash
uv run main.py document.md -t custom_template.html
```

### ファイルサイズ制限をバイパスする
出力HTMLが30MBを超える場合、デフォルトではエラーになりますが `--force` で強制的に保存できます。

```bash
uv run main.py document.md --force
```

### 同期・データ収集サーバーの起動
同期機能（スクロール同期など）やデータ収集（投票結果など）を使用する場合は、付属のFastAPIサーバーを起動します。

```bash
uv run server.py
```
サーバーはデフォルトで `http://0.0.0.0:8000` で起動し、WebSocket (`/ws/sync`) とデータ収集API (`/api/data`) を提供します。

---

すべてのオプションを確認するにはヘルプを参照してください：

```bash
uv run main.py --help
```

## 変更ログ

- `mono-icon`コンポーネントの追加
- `mono-spacer`コンポーネントによる水平/垂直スペーシングのサポート
- デスクトップアプリの設計ドキュメントの最終化
- GIFアニメーションサポートツールの設計ドキュメント追加
- 効果音コンポーネント `mono-sound` の追加
- ディレクトリ構造の `src/` 配下へのリファクタリング
- 描画オーバーレイのための `mono-brush` コンポーネント追加
- 方向ベースのレイアウトシステム `mono-layout` の追加
