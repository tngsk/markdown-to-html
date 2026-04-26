# プロジェクト情報と設計指針 (NOTES.md)

## 1. プロジェクト概要
Monoは、Markdownファイルを解析し、特定ドメインに特化したインタラクティブな単一HTMLファイルを生成するビルドシステムである。

ターゲット環境: ユーザーのブラウザ（幅広いデバイス。主対象は参加者・ユーザー）
コアバリュー: 依存関係ゼロのポータビリティ、フィードバックの即時性、および高精度なメディア同期制御。
基本原則: オフライン環境でも最低限のHTMLテキストと解説画像が必ず表示・保証されること（情報の欠落防止）。
埋め込み戦略: アンケートや実験用の重いアセット（音声等）は、現場の要件に応じて実施者が「Base64完全埋め込み（ポータビリティ優先）」か「外部リンク参照（パフォーマンス優先）」かを選択可能なアーキテクチャとする。

## 2. システムアーキテクチャ（Senior Research Engineer 視点）
### 2.1 レイヤード・モジュール・アプローチ
保守性と拡張性を担保するため、以下のモジュール分割アーキテクチャを採用している。
- **Interface Layer (CLI & Config)**: `main.py` および `config.py` による入出力制御。設定が複雑化した場合、MarkdownへのFrontmatter埋め込みではなく、独立した外部ファイル（`config.toml`等）により関心の分離を徹底する。
- **Processing Layer**: `processors/` にて変換処理を担当。`MarkdownProcessor`、`HTMLDocumentBuilder`、およびオプションのPDF生成を行う `PDFProcessor` （Playwrightを使用）を含む。
- **Embedding Layer**: `embedders/` にて、メディアのBase64インライン化 (`MediaEmbedder`)、およびテーマとCSSの動的注入 (`CSSEmbedder`) を行う。
- **Data I/O Layer**: `handlers/` にてファイル読み書き、MIMEタイプ判定を行う。
- **Component Templates Layer**: `components/` にて、Web ComponentsのHTML/JS/CSSをコンポーネント単位で分割管理。ビルド時に動的スキャンし1ファイルへパッキングする「Component-Based Split」アーキテクチャ。

### 2.2 技術スタック（Dependency Minimalism）
- **Parser**: `markdown` (Python) - 標準的で拡張性に優れる。
- **DOM Manipulation**: Python標準の `re` (正規表現) - `BeautifulSoup4` のような重い依存を排除し、高速かつメモリ効率の高いストリームライクな置換を実現。
- **Dependency Management**: `uv` - 爆速かつ再現性の高いモダンなPython環境構築。
- **Frontend Runtime**: Vanilla JS / Web Components (No Heavy Frameworks)。
  - すべてのコンポーネント用JS/CSSは、コンバータ実行時に1つのHTML内に完全にインライン展開（パッキング）される。
  - インタラクティブなコンポーネントは、状態や認証管理（`localStorage`、`mono-auth-changed`イベントの発火と購読）のボイラープレートを抽象化した共通基底クラス `MonoInteractiveElement` を継承する。
- **Communication (Server)**: FastAPI + WebSockets (`server.py`)
  - リアルタイム同期用の `/ws/sync` およびデータ収集用の `/api/data` エンドポイントを提供。
  - DoS攻撃（メモリ枯渇）防止のため、`config.toml` の `max-upload-size` を用いてペイロードサイズ制限を実施。また、非同期環境下でのファイル書き込みの競合を防ぐため `asyncio.Queue` を用いたバックグラウンドワーカーで直列化する堅牢な設計。
- **Optional Heavy Dependencies**: Playwright (PDFエクスポート用) などの重い依存はローカルインポートとし、インストールされていなくてもコアシステムがクラッシュしないようグレースフル・デグラデーションを実現している。

## 3. UI/UX 設計指針 (UX Designer 視点)
- **Typography & Style**: 参加者の「見やすさ」を最優先とし、CSS変数を活用したDaisyUIインスパイアのテーマシステム（`themes.toml`）を導入。デフォルトテーマの他、ドキュメント単位での切り替えが可能（`@[theme: name]()` 経由など）。
- **Visual Feedback**: ユーザーの入力に対し、即座に視覚的変化（色の変化、チェックマーク等）を返す。
- **Multi-sensory Interaction**: 操作に対し、適切なマルチメディア・フィードバックを考慮。
- **Accessibility**: セマンティックなHTML構造を維持。キーボード操作によるフォーカス移動を保証。

## 4. 運用上の制約と堅牢性 (Operational Safety)
- **Resource Monitoring**: リソース制約のあるエッジデバイス環境でのビルド時、大量のメディアファイルのBase64変換によるメモリ消費を考慮し、正規表現ベースの省メモリ処理を採用。
- **Robustness**: ネットワーク切断時、ユーザーの入力データを一時的にLocal Storageへ退避し、再接続時に自動再送するロジックや、コンポーネント初期化時のフォールバックモードを備える。
- **Configuration Strategy (Frontmatter Exclusion)**: 「1ファイル・ポータビリティ」は出力HTMLに対する要求であり、入力（Markdown）と設定は分離すべきである。外部依存（`PyYAML`等）の混入を防ぐため、設定は独立ファイル（`config.toml`）に委譲する設計を維持する。
- **Non-Goals (やらないこと)**: 独自のGUIエディタの開発。複雑なユーザー認証（LMS）の実装。Markdownファイル内へのフロントマター（Frontmatter）の組み込み。Tailwindのような巨大CSSユーティリティフレームワークの導入（コンポーネントの完全なカプセル化とファイルサイズ肥大化防止のため）。

## 5. Web Components インタラクティブ機能（実装済み）
参加者の能動的なインタラクションとセッション運用性を向上させる多数のコンポーネント群が実装済みである。各機能は独立コンポーネントとして実装し、依存先がない場合は安全に非表示になるグレースフル・デグラデーション設計となっている。

### 主なインタラクティブコンポーネント（抜粋）
- **mono-reaction（ユーザーリアクション）**: ユーザーが「手を挙げる」「？」などのリアクションを送れるUI。
- **mono-session-join（セッション参加）**: セッション番号を入力して参加するためのコンポーネント。参加状態はLocal Storageに保存され、他コンポーネントと連動する。
- **mono-group-assignment（グループ分け）**: セッション参加中のユーザーを指定のロジックでグループ分配しフィードバックする。
- **mono-account**: 認証・ユーザー状態の管理・発信（イベントドリブン）を担う。
- その他: `mono-ab-test`, `mono-poll`, `mono-notebook`, `mono-sound`, `mono-dice`, `mono-hero` など多数。

### 暗黙的コンポーネントの非推奨化 (Deprecation Plan)
Markdown上に明示的なディレクティブを持たず、システムによって自動注入される以下の「暗黙的コンポーネント」は、設計の透過性と一貫性を高めるため将来的に非推奨とし、明示的なディレクティブを持つコンポーネントへの移行が予定されている。
- `mono-brush`
- `mono-code-block`
- `mono-export`
- `mono-sync`
## Security Fix: DOM XSS in Lazy Load & Audio components

* **Vulnerability:** Unsafe parsing of JSON assets using `innerHTML` and assigning URLs to `src` attributes without checking the protocol could lead to XSS attacks using `javascript:` payloads.
* **Fix Applied:** Modified `lazy_load.js` and `mono-sound/script.js` to securely extract JSON string using `textContent`. Furthermore, added a robust URL validation checking the parsed URL protocol against a strict allowlist (`http:`, `https:`, `data:`).
