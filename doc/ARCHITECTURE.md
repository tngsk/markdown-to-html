# Mono アーキテクチャおよび開発仕様書

本書は、Markdownから単一自己完結型HTML（画像・CSS等埋め込み）を生成するCLIツール「Mono」の全体設計、変換処理フロー、および拡張（エクステンション・コンポーネント）開発のための仕様をまとめたものです。

## 1. 全体像とCLIの振る舞い

Monoは、依存関係を持たずにローカルで共有・閲覧可能な単一HTMLファイルを生成することを目的としています。内部的にはPython製の変換ツールとして動作し、各種Webコンポーネント（Vanilla JS）をMarkdown文書に埋め込むことが可能です。

### 1.1. CLIコマンドオプション

エントリーポイントは `src/main.py` であり、以下のオプションをサポートします。特にPDF出力機能など、抜け落ちやすい機能に注意してください。

*   `input_file`: (必須) 入力となるMarkdownファイルのパス。
*   `-o, --output`: 出力HTMLファイルのパス。省略時は `{入力ファイル名}.html` となります。
*   `-c, --css`: 埋め込むカスタムCSSファイルのパス（複数指定可能）。
*   `-v, --verbose`: 詳細なログを出力します。
*   `-t, --template`: カスタムHTMLテンプレートファイルのパス。
*   `-e, --excluded-tags`: 出力HTMLから除外（削除）するHTMLタグ名（複数指定可能）。
*   `--force`: デフォルトの出力サイズ制限（30MB）をバイパスして強制的に保存します。
*   `--export`: 外部エクスポートモジュール（`mono-export`）を強制的に有効にします。
*   `--pdf [OUTPUT_FILE]`: 出力されたHTMLからPDFを生成します。パスを指定しない場合は `{入力ファイル名}.pdf` として保存されます。Playwrightを利用して描画状態をPDF化します。

---

## 2. 変換処理フロー

Markdownファイルから単一HTMLへの変換は、主に `src/converter.py` の `MarkdownToHTMLConverter` クラスによってオーケストレーションされます。変換処理は以下のステップで進行します。

1.  **Markdownの読み込み**: `FileHandler` を使用して入力ファイルを読み込みます。
2.  **Markdown → HTMLの中間変換 (`MarkdownProcessor`)**:
    *   コードブロックを保護（プレースホルダーへの置換）。
    *   `src/components/*/parser.py` をホワイトリスト(`ALLOWED_COMPONENTS`)ベースで安全にロードし、カスタムディレクティブを評価・置換。
    *   Python-Markdownによる標準Markdown処理、および `src/extensions/` の拡張処理を適用。
    *   コードブロックの復元。
3.  **CSSの読み込み (`CSSEmbedder`)**: `--css` で指定された外部CSSファイルを読み込みます。
4.  **メディアの埋め込み (`MediaEmbedder`)**: 中間HTML内の画像（`<img>`）やその他のメディアリソースを抽出し、Base64エンコードしてインライン化します。
5.  **HTMLドキュメントの生成 (`HTMLDocumentBuilder`)**:
    *   HTMLボディからタイトルを抽出。
    *   `src/templates/core/base.html` （またはカスタムテンプレート）をベースに、ヘッダー、ボディ、使用されているWebコンポーネントのスクリプト（`script.js`）およびスタイル（`style.css`）を注入し、完全なHTML構造を構築。
6.  **CSSの埋め込み (`CSSEmbedder`)**: 構築されたHTMLドキュメント内に、Step 3で読み込んだCSSや、テーマのCSSを注入します。
7.  **出力とファイルサイズ検証**: HTMLを出力ファイルとして保存。20MB超過で警告、30MB超過で（`--force` がなければ）エラー終了します。
8.  **PDFの出力 (オプション) (`PDFProcessor`)**: `--pdf` が指定されている場合、生成したHTMLを読み込み、PDF形式で書き出します。

---

## 3. エクステンション開発ガイドライン

Python-Markdownの標準的な処理に介入・拡張を行いたい場合は、`src/extensions/` にモジュールを追加します。

### 3.1. エクステンションの追加方法

1.  `src/extensions/` に新しいPythonファイルを作成します（例: `my_extension.py`）。
2.  `markdown.extensions.Extension` を継承したクラスを作成し、`extendMarkdown` メソッドを実装して、プリプロセッサ、インラインプロセッサ、ツリープロセッサ、またはポストプロセッサを登録します。
3.  モジュールの末尾に `def makeExtension(**kwargs):` 関数を定義し、拡張クラスのインスタンスを返すようにします。
4.  作成したエクステンションが有効になるよう、`src/constants.py` などの `MARKDOWN_EXTENSIONS` リストに追加（または動的にロード）されるように構成します。

---

## 4. コンポーネント開発ガイドライン

カスタムMarkdown記法で記述できるUI要素（Webコンポーネント）を追加する場合、`src/components/` 配下にディレクトリを作成します。

### 4.1. ディレクトリ構造と必須ファイル

コンポーネントのディレクトリ名はケバブケース（例: `mono-my-component`）とし、以下のファイルを含めます。

*   `parser.py`: MarkdownからHTMLタグ（コンポーネントのタグ）への置換ロジック。
*   `script.js`: Vanilla JSによるWeb Componentsの実装（Shadow DOMまたはLight DOMへのアクセス）。
*   `style.css`: コンポーネント固有のスタイル（通常は `:host` セレクタを用いてShadow DOM内のスタイルを定義）。
*   `template.html`: Shadow DOM内に展開されるHTMLテンプレート。

※これらのアセットは、`HTMLDocumentBuilder` によって使用されているコンポーネントのみが自動的に抽出され、最終的なHTMLに注入されます。

### 4.2. Markdownディレクティブの統一フォーマット

コンポーネントを呼び出す際のMarkdownディレクティブは、パーサーの統一性と予測可能性を高めるため、以下のフォーマットを標準（推奨）とします。

**インラインまたは空要素のコンポーネント:**
```markdown
@[component-name: label](key: "value", key2: "value2")
```

**ブロックレベルのコンポーネント (コンテンツを囲む場合):**
ブロックレベルの場合は、明確な終了タグを用いる形式を標準とします。`@[end]` 等の曖昧な閉じタグは避け、コンポーネント名を含む閉じタグを使用してください。

```markdown
@[component-name: label](key: "value")
ここに内部のMarkdownコンテンツやHTMLを記述します。
@[/component-name]
```

#### `parser.py` の実装例 (ブロックレベルの場合)
`src/processors/base_parser.py` の `BaseComponentParser` を継承して実装します。

```python
import re
from src.processors.base_parser import BaseComponentParser
import html

class Parser(BaseComponentParser):
    START_PATTERN = r"@\[my-component(?:\:\s*([^\]]*))?\](?:\(((?:[^()]*|\([^()]*\))*)\))?"
    END_PATTERN = r"@\[/my-component\]"

    @property
    def block_level_tags(self) -> list[str]:
        return ["mono-my-component"]

    def process(self, markdown_content: str) -> str:
        # 開始タグの処理
        pattern = re.compile(self.START_PATTERN)
        def start_replacer(match: re.Match) -> str:
            label = match.group(1)
            args_str = match.group(2)
            args = self.parse_key_value_args(args_str)
            # ... 属性の構築 ...
            return f'<mono-my-component markdown="1">'

        result = pattern.sub(start_replacer, markdown_content)

        # 終了タグの処理
        end_pattern = re.compile(self.END_PATTERN)
        result = end_pattern.sub('</mono-my-component>', result)

        return result
```

### 4.3. 暗黙的コンポーネントについて

一部のコンポーネントは、明示的なMarkdownディレクティブを持たず、システムの特定の条件やPython-Markdown側の置換ロジックによって自動的に組み込まれる「暗黙的コンポーネント」として実装されています。

**暗黙的コンポーネントのリスト:**
*   `mono-brush`
*   `mono-code-block`
*   `mono-export`
*   `mono-sync`

**⚠️ 注意: 将来的な廃止予定**
これらの暗黙的コンポーネントは、設計の一貫性を保つため、将来的に現在の暗黙的な注入方式から廃止、または明示的なシステムアーキテクチャへと移行される予定です。新規開発においては、明示的なディレクティブを持つ通常のコンポーネントとして設計することを推奨します。
