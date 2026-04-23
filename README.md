# Mono - Markdown to Monolithic Document

Markdownファイルを、画像（Base64）やCSSが埋め込まれた**単一の自己完結型HTMLファイル**に変換するCLIツールです。ローカルでの配布や共有に最適です。

## 特徴

- **単一ファイル出力**: 画像をBase64として埋め込み、外部リソース依存のないHTMLを生成（共有が容易）。
- **コードブロック**: Highlight.jsによるシンタックスハイライトと、ワンクリック「コピー」ボタンを自動付与。
- **Colabリンク自動変換**: `.ipynb` を指すリンクを検知し、Google Colabの起動バッジ付きリンク（別タブで開く）へ自動変換。
- **カスタム記法**: `{{テキスト}}` と記述すると、改行を防ぐ `nowrap` スパンに変換。
- **画像の最適化と遅延読み込み**: 画像をWebPに変換・SVGをインライン化し、非同期注入戦略によって遅延読み込みを行うことでパフォーマンスを最適化。
- **ファイルサイズ検証**: 出力ファイルのサイズを検証し、30MBを超える場合は警告・停止（`--force` でバイパス可能）。
- **セキュリティ設定（CSP）**: `config.toml` から設定を読み込み、Content-Security-Policyタグを自動設定。
- **Web Components対応**: 外部依存なしのVanilla JSによるWeb Componentsの埋め込みに対応。多彩なUIコンポーネントをMarkdown内に記述可能です。

### 利用可能な Web Components 一覧

Monoでは外部依存なしのVanilla JSによる多彩なWeb Componentsを埋め込むことができます。各コンポーネントはカスタムMarkdown記法で記述します。

#### 明示的コンポーネント

| コンポーネント | 概要 | 記述例 | オプション |
|---|---|---|---|
| `mono-ab-test` | A/Bテスト用のコンポーネント。2つの画像やコンテンツを並べて比較します。 | `@[ab-test](src-a: "img1.png", src-b: "img2.png")` | `src-a`, `src-b` |
| `mono-account` | ログインなどのアカウント管理UIを表示します。 | `@[account]()` | なし |
| `mono-clock` | 時計を表示します。 | `@[clock](display: "analog")` | `display`, `format` |
| `mono-countdown` | カウントダウンタイマーを表示します。 | `@[countdown](time: "60", color: "red")` | `time`, `color` |
| `mono-dice` | サイコロを表示し、クリックで振ることができます。 | `@[dice](number: 2, faces: 6)` | `number`, `faces` |
| `mono-drawer` | 引き出し式のサイドメニュー（ドロワー）を表示します。ブロック要素。 | `@[drawer](position: "left", open: "false")\n...コンテンツ...\n@[/drawer]` | `position`, `open`, `label` |
| `mono-flipcard` | クリックまたはホバーで裏返るカード。 | `@[flipcard]()` | なし |
| `mono-group-assignment` | グループ分けを行うコンポーネント。 | `@[group-assignment](title: "グループ分け")` | `title` |
| `mono-hero` | ヒーローバナー領域を表示します。ブロック要素。 | `@[hero](bg-color: "#000", text-color: "#fff")\n...コンテンツ...\n@[/hero]` | `bg-color`, `text-color`, `image`, `mode` |
| `mono-icon` | アイコンを表示します。 | `@[icon: star](size: "24", color: "yellow")` | `size`, `color`, `display` |
| `mono-layout` | 行（row）や列（stack）などのレイアウトを構築します。ブロック要素。 | `@[row]\n:::column\n左側コンテンツ\n:::\n:::column\n右側コンテンツ\n:::\n@[/row]` | `class` |
| `mono-notebook` | 入力可能なノートブック領域を表示します。 | `@[notebook](title: "メモ", placeholder: "入力してください")` | `title`, `placeholder`, `id` |
| `mono-poll` | 投票システムを表示します。 | `@[poll](title: "好きな言語は？", options: "Python, JavaScript")` | `title`, `options` |
| `mono-reaction` | リアクション（いいね、など）ボタンを表示します。 | `@[reaction](options: "👍, 👎")` | `options` |
| `mono-score` | 楽譜を表示します。 | `@[score](clef: "treble", notes: "C4 D4 E4")` | `clef`, `notes`, `time` |
| `mono-section` | セクション領域を表示します。ブロック要素。 | `@[section](bg-color: "#f0f0f0")\n...コンテンツ...\n@[/section]` | `bg-color`, `text-color`, `image`, `mode`, `height` |
| `mono-session-join` | セッション（同期・データ収集）へ参加するボタン等を表示します。 | `@[session-join](title: "参加する")` | `title` |
| `mono-sound` | 効果音や音声を再生するボタンを表示します。 | `@[sound](src: "audio.mp3", label: "再生")` | `src`, `label` |
| `mono-spacer` | 空白（スペーサー）を挿入します。 | `@[spacer](width: "10px", height: "20px")` | `width`, `height` |
| `mono-textfield-input` | テキスト入力フィールドを表示します。 | `@[textfield](placeholder: "テキストを入力", size: "large")` | `placeholder`, `size` |
| `mono-theme` | テーマ切り替えコンポーネント。通常はMarkdownディレクティブでテーマを設定します。 | `@[theme: dark]()` | `show_ui` |

#### 暗黙的・システムコンポーネント

これらのコンポーネントはオプションやサーバー構成によって自動的に組み込まれます。

- `mono-brush`: 描画オーバーレイ機能。暗黙的に全ページに組み込まれるか、特定条件で有効化されます。
- `mono-export`: 外部エクスポート機能。`--export`オプションで強制的に有効になります。
- `mono-sync`: 状態同期・通信機能。サーバーとのWebSocket通信を管理し、暗黙的に組み込まれます。

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
