# Code Block 独自実装とhighlight.js廃止に関する検討レポート

## 1. 背景と目的
現在、MonoフレームワークではコードブロックのシンタックスハイライトにフロントエンドJSライブラリである `highlight.js` (CDN経由) を利用しています。
しかし、Monoは「オフラインでも動作する単一HTMLファイル」を基本理念としているため、外部CDNへの依存やフロントエンドでの動的レンダリングを削減し、Python側（ビルド時）で静的なHTML/CSSとしてコードブロックを生成・埋め込むアプローチが適しています。

本レポートでは、`highlight.js` の廃止および独自のコードブロック実装（`mono-code-block` のリニューアル）に向けた検討結果をまとめます。

## 2. 要件と設計方針

新しい独自実装のコードブロックには、以下の要件を満たすことが求められます。

1. **通常のコードブロックとの区別（プレフィックス構文の導入）**
2. **シンタックスハイライト機能（オフライン・バックエンド生成）**
3. **コピーボタンの設置**
4. **行番号の表示**
5. **ファイル名（タイトル）の表示**

### 2.1. `mono:` プレフィックスによる通常のコードブロックとの区別
Markdownの記法において、以下のように `mono:` プレフィックスを付けることで、リッチな独自コードブロックと通常の装飾なし `<pre><code>` ブロックを明確に区別できるようにします。

**独自（リッチ）コードブロックの構文例:**
```markdown
    ```mono:python:example.py
    import pandas as pd
    ```
```
- `mono:`: リッチなコードブロックとしてパースするための識別子。
- `python`: プログラミング言語（シンタックスハイライト用）。
- `example.py`: （オプション）ファイル名やタイトル。

**通常のコードブロックの構文例:**
```markdown
    ```python
    import pandas as pd
    ```
```
- 既存のMarkdownの挙動を維持し、装飾なしのプレーンな `<pre><code>` として出力します（パースコストの削減・シンプルな表示用）。

### 2.2. シンタックスハイライトのバックエンド化 (`pygments` の活用)
フロントエンドでの `highlight.js` を廃止する代わりに、Pythonの標準的なシンタックスハイライターである `pygments` を導入することを提案します。

- **処理の流れ:** `src/extensions/code_block.py` などのMarkdown拡張でコードブロックをフックし、`pygments` を使って構文解析を行い、CSSクラス付きの静的なHTMLスパン（`<span class="k">import</span>` など）に変換して出力します。
- **スタイル:** Pygments用のCSSスタイル（例: Atom One Darkテーマ相当）を生成し、`src/embedders/css.py` 経由で最終的なHTMLに埋め込みます。
- **メリット:** 完全にオフライン対応が可能となり、クライアント側のJS実行コストが不要になるため、パフォーマンスが向上します。

### 2.3. コピーボタン・行番号・ファイル名の実装

- **ファイル名:** 構文からパースしたファイル名（例: `example.py`）を `<mono-code-block title="example.py">` などの属性として渡し、ヘッダー部分に表示します。
- **コピーボタン:** 既存の `mono-code-block` の `script.js` に実装されているコピー機能を維持・改善します（クリップボードAPIの利用）。静的なHTMLになってもコピーボタンの機能は軽量なVanilla JSで完結します。
- **行番号:** Pygmentsのオプションで行番号を出力するか、CSSのカウンタ (`counter-reset`, `counter-increment`) を用いて行番号をスタイルで付与する方法が考えられます。コピー時に行番号が含まれないよう、CSSベースの実装（または擬似要素による表示）が推奨されます。

## 3. アーキテクチャの変更案

### 3.1. 削除・廃止する要素
- `src/constants.py` の `HIGHLIGHT_JS_CDN_BASE` などの設定。
- `src/processors/html.py` における `{HIGHLIGHT_JS_CSS}` および `{HIGHLIGHT_JS}` の注入処理。
- `src/components/mono-code-block/style.css` にある `highlight.js` 用のテーマ上書きCSS。
- `src/components/mono-code-block/script.js` の `initializeSyntaxHighlighting()` メソッド。

### 3.2. 追加・改修する要素
1. **PyPIパッケージの追加:** `uv add pygments`
2. **Markdown拡張の改修 (`src/extensions/code_block.py`):**
   - 正規表現でフェンスコードブロックの言語指定を解析。
   - `mono:` プレフィックスがある場合のみ、`Pygments` でハイライト済みのHTMLを生成し、`<mono-code-block>` でラップする。
   - 通常のコードブロックは素の `<pre><code class="language-xxx">` のまま返す。
3. **Pygments用CSSの生成と埋め込み:**
   - ビルドプロセス時に Pygments からCSSを取得（例: `HtmlFormatter(style='monokai').get_style_defs('.highlight')`）。
   - これを `CSSEmbedder` に渡してHTMLの `<style>` にインジェクトする。
4. **コンポーネントの構造変更 (`mono-code-block`):**
   - タイトル（ファイル名）を表示するUIをヘッダーに追加。
   - 行番号表示用のCSSスタイルを追加。

## 4. メリットとデメリット（Pros / Cons）

### メリット (Pros)
- **完全オフライン対応:** 外部CDNへの依存がなくなり、Monoの「単一ファイル・オフライン動作」のコンセプトに合致する。
- **クライアントパフォーマンスの向上:** ブラウザ側での巨大な正規表現パース（highlight.js）が不要になり、レンダリングが高速化する。
- **表現力の向上:** `mono:` プレフィックスにより、「リッチなコードブロック」と「シンプルなコードブロック」を使い分けられるようになる。ファイル名や行番号などのドキュメント作成に便利な標準機能が備わる。

### デメリット (Cons)
- **ビルド時間の増加:** Python側（Pygments）での構文解析が行われるため、巨大なコードブロックが多数ある場合、MarkdownからHTMLへの変換ビルド時間がわずかに増加する可能性がある。
- **依存ライブラリの追加:** `pygments` という外部Pythonパッケージへの依存が増える。
- **テーマ設定の再構築:** highlight.js用に最適化されていたCSSテーマを、Pygmentsのクラスベースのテーマ構造に書き換える必要がある。

## 5. 結論と次のステップ
`highlight.js` の廃止と、`pygments` を用いたバックエンド生成モデルへの移行は、Monoフレームワークの思想（オフライン単一ファイル、高速な初期レンダリング）に極めて適しています。
また `mono:` プレフィックスの導入は、ユーザーに柔軟な選択肢を提供し、既存のMarkdownを破壊することなく安全に移行できる優れたアプローチです。

**今後の実装に向けたステップ:**
1. `pygments` の導入と動作検証。
2. `src/extensions/code_block.py` における `mono:` プレフィックスのパース処理の実装。
3. `pygments` による静的HTML生成と、Pygments用CSSの抽出・埋め込みロジックの実装。
4. `mono-code-block` コンポーネントのUI更新（ファイル名、行番号、コピー機能の調整）。
5. 既存コードブロックのテストとリファクタリング。