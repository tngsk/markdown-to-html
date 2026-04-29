# Mono Component CSS Specification

この仕様書は、Mono フレームワークにおけるカスタム Web コンポーネントの CSS スタイリング構造の標準化について定義します。

## 1. 背景と課題

Web Components (Shadow DOM) を利用する際、コンポーネント自身（カプセル化された内部UI）へのスタイリングと、コンポーネントが内包するコンテンツ（Slot に挿入される Light DOM 要素）へのスタイリングという相反する課題が存在します。

**これまでのハック的手法とその問題点:**
1.  **`::slotted` の限界**: `mono-hero` や `mono-code-block` などでは Shadow DOM 内から Light DOM へスタイルを当てるため `::slotted()` を使用していましたが、これは「直下の要素にしか適用されない」という仕様上の制限があり、深い階層のタグには適用できません。
2.  **JSによる動的注入**: `mono-flow` などの一部コンポーネントでは、この制限を回避するために `script.js` の `connectedCallback` 時にわざわざ `<style>` タグを生成してグローバルなドキュメントの `<head>` に注入する（`injectLightDOMStyles`）というハック的な実装が行われており、パフォーマンスや可読性の低下を招いていました。
3.  **`base.css` の責務違反**: 全ての Light DOM に適用される `base.css` に、各コンポーネント特有のコンテンツ装飾を追記することは「関心の分離」の原則に反します。

## 2. 新しいCSSファイル構造と役割の分離

これらの課題を解決するため、各コンポーネント（`src/components/mono-*/`）ディレクトリ内の CSS ファイルを以下の2つに分割し、用途とビルド時の注入先を明確に分離します。

### 2.1. `style.css` (Shadow DOM 用スタイル)
*   **役割**: コンポーネント自身（`:host`）や、Shadow DOM 内部にカプセル化されたUI構造（ボタン、ラッパー、アイコンなど）に対するスタイルを定義します。
*   **記述ルール**: 従来通り記述します。
*   **注入先**: Python のビルドプロセス時（`HTMLDocumentBuilder` 等）に、各コンポーネントの `template.html` 内にある `{COMPONENTS_CSS}` プレースホルダーに展開され、Shadow DOM 内にカプセル化されます。

### 2.2. `content.css` (Light DOM / コンテンツ用スタイル)
*   **役割**: コンポーネントタグで囲まれた中身（Light DOM）や、Markdown から変換されて Slot に渡されるコンテンツ（`h1`, `p`, `pre`, `code` など）に対するスタイルを定義します。
*   **記述ルール**: このファイル内では、**必ず自コンポーネントのタグ名を親セレクタ（スコープ）として記述**することを徹底します。これにより、グローバルへのスタイルの漏れを防ぎます。
    *   **良い例**: `mono-hero h1 { font-size: 3rem; }`, `mono-code-block pre { padding: 1rem; }`
    *   **悪い例**: `h1 { font-size: 3rem; }`, `.my-inner-class { ... }`
*   **注入先**: Python のビルドプロセス時に、使用されている全コンポーネントの `content.css` がかき集められ、最終出力 HTML の `<head>` 内（`base.css` の読み込み後）に1つの `<style>` ブロックとしてグローバル展開されます。

## 3. 実装・リファクタリング方針

この仕様により、各コンポーネントのリファクタリングを以下のように進めます。

1.  **`mono-hero` / `mono-code-block`**:
    *   `style.css` 内の `::slotted(...)` ルールを削除します。
    *   該当するスタイルを `content.css` に移動し、`mono-hero h1 { ... }` や `mono-code-block .hljs { ... }` のような親セレクタ形式に書き直します。
2.  **`mono-flow`**:
    *   `script.js` に存在する `injectLightDOMStyles()` ハックを完全に削除します。
    *   JS内に文字列として定義されていた CSS をそのまま `content.css` に移行します（セレクタは `mono-flow .flow-container { ... }` のようにコンポーネント名から始まっているため、そのまま利用可能です）。
3.  **Python ビルドプロセスの拡張**:
    *   `src/processors/html.py` 等を改修し、各コンポーネントの `content.css` を収集して `<head>` にグローバル注入する処理を実装します。

## 4. 期待される効果

この明示的な構造により、「Shadow DOM による UI コンポーネントのカプセル化」と「Light DOM に配置される Markdown コンテンツへの安全で柔軟なスタイリング」を両立させることが可能になります。
コンポーネントの関心の分離が促進され、JavaScript による不要なスタイル操作が排除されることで、保守性とパフォーマンスの向上が期待できます。
