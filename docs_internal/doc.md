プロジェクト名：Interactive-MD (Interactive Markdown-to-HTML Packager)

本ドキュメントは、開発担当AIが、指示された役割（UX Designer / Senior Engineer）に基づき、一貫性のある実装を行うための設計仕様書である。

1. プロジェクト概要
Interactive-MDは、Markdownファイルを解析し、特定ドメインに特化したインタラクティブな単一HTMLファイルを生成するビルドシステムである。

ターゲット環境: ユーザーのブラウザ（幅広いデバイス。主対象は参加者・ユーザー）
コアバリュー: 依存関係ゼロのポータビリティ、フィードバックの即時性、および高精度なメディア同期制御。
基本原則: オフライン環境でも最低限のHTMLテキストと解説画像が必ず表示・保証されること（情報の欠落防止）。
埋め込み戦略: アンケートや実験用の重いアセット（音声等）は、現場の要件に応じて実施者が「Base64完全埋め込み（ポータビリティ優先）」か「外部リンク参照（パフォーマンス優先）」かを選択可能なアーキテクチャとする。

2. システムアーキテクチャ（Senior Research Engineer 視点）
2.1 レイヤード・モジュール・アプローチ（現在実装済み）
保守性と拡張性を担保するため、以下のモジュール分割アーキテクチャを採用している。
- Interface Layer (CLI & Config): `main.py` および `config.py` による入出力制御。設定が複雑化した場合、MarkdownへのFrontmatter埋め込みではなく、独立した外部ファイル（`config.toml`等）により関心の分離を徹底する。
- Processing Layer: `processors/` (Markdown変換、HTMLテンプレート構築、カスタム記法処理)。
- Embedding Layer: `embedders/` (画像・音声等のメディアBase64化、CSS/JSのインライン展開)。
- Data I/O Layer: `handlers/` (ファイル読み書き、MIMEタイプ判定)。
- Component Templates Layer: `templates/components/` (Web ComponentsのHTML/JS/CSSをコンポーネント単位で分割管理。ビルド時に動的スキャンし1ファイルへパッキングする「Component-Based Split」アーキテクチャ)。

2.2 技術スタック（Dependency Minimalism）
- Parser: `markdown` (Python) - 標準的で拡張性に優れる。
- DOM Manipulation: Python標準の `re` (正規表現) - `BeautifulSoup4` のような重い依存を排除し、高速かつメモリ効率の高いストリームライクな置換を実現。
- Dependency Management: `uv` - 爆速かつ再現性の高いモダンなPython環境構築。
- Frontend Runtime: Vanilla JS / Web Components (No Heavy Frameworks)。すべてのコンポーネント用JS/CSSは、コンバータ実行時に1つのHTML内に完全にインライン展開（パッキング）される。また、JS内にHTML文字列を直書きすることを避け、純粋な `<template>` タグをパッキングしてJS側で `cloneNode` する手法（Template Injection Strategy）を採用し、デザイナーの編集容易性（DX）と堅牢性を両立している。
- Communication: FastAPI + WebSockets (Phase 2以降、Render等へのデプロイ想定)。

3. 実装フェーズとコンポーネント設計
Phase 1: Core Packager (Foundation) - ✅ 実装完了・安定化
- 1-File Build: CSS, JS, および画像を data:uri (Base64) としてHTMLに埋め込む。
- Syntax Highlighting: Highlight.jsの軽量ロードとコピーボタンの統合。
- Custom Directives (教育向け機能):
  - `{{テキスト}}` → 改行を防ぐ `nowrap` 処理。
  - **Open in Colab 自動変換** → `.ipynb` リンクを検知し、Google Colabのバッジ付き起動リンクへ自動置換。

Phase 2: Scaffolding, Polling & Universal A/B Test (✅ 実装完了)
- ✅ `@[poll: タイトル](選択肢1, 選択肢2, ...)`：リアルタイム投票コンポーネント（`<situ-poll>`）。実装完了。
  - 状態モックとペイロード: 通信インフラとUIを分離。投票イベントは `タイムスタンプ` と `コンポーネントID` を含む Phase 3 互換の JSON フォーマットで発火させ、現状は Local Storage に保存・モックする設計を実現。
- ✅ `@[ab-test: タイトル](file_a, file_b)`：汎用A/Bテストコンポーネント（`<situ-ab-test>`）。拡張子からメディア（画像、音声等）を自動判別し、対象に応じた最適な比較UI（クロスフェード等）を提供する。
  - Web Audio API / Accessibility: Web Audio API による 20ms クロスフェード切り替え、Lazy Loading、およびキーボードショートカット（Space/A/B）と視覚的フォーカス管理（READY LED）を実装。
- ✅ `@[notebook-input](id)`：Local Storageに永続化されるユーザー用メモ欄。
- ✅ 埋め込み戦略の具体化: CLIオプションによる「全メディアBase64一括埋め込み（デフォルト）」を基本としつつ、マークダウン上でURL（`http://` 等）を直接指定した場合は外部リンクとして扱うハイブリッド仕様とする。

Phase 3: Sync & Collection (Experience Design 優先)
- Focus Sync (Visual First): 主催者の操作（スクロール、チャプター切り替え）を多数の参加者端末にリアルタイム同期（WebSocket）。
- Data Recovery: ユーザーの入力データをJSONL形式で中央サーバー（FastAPI）へ送信。
- Metadata: ISO8601タイムスタンプ、および環境コンテキストの付与。

Phase 4: Advanced Media & Visual Insight
- Media Integration: 外部エクスポートモジュールのシームレスな埋め込みと高度な視覚化表示。
- Data Visualization: 多次元データの対話的UI。情報伝達効率を最大化する設計とする。

4. UI/UX 設計指針 (UX Designer 視点)
- Typography & Style: 参加者の「見やすさ」を最優先とし、現行のクリーンで視認性の高いテンプレートCSSをデフォルトとして維持する。インダストリアル/計測器風（Lab-Gear）のデザインは「選択可能なテーマ機能」として提供する。
- Visual Feedback: ユーザーの入力に対し、即座に視覚的変化（色の変化、チェックマーク等）を返す。
- Multi-sensory Interaction: 操作に対し、適切なマルチメディア・フィードバックを考慮。
- Accessibility: セマンティックなHTML構造を維持。キーボード操作によるフォーカス移動を保証。

5. 運用上の制約と堅牢性 (Operational Safety)
- Resource Monitoring: リソース制約のあるエッジデバイス環境でのビルド時、大量のメディアファイルのBase64変換によるメモリ消費を考慮し、正規表現ベースの省メモリ処理を採用。
- Robustness: ネットワーク切断時、ユーザーの入力データを一時的にLocal Storageへ退避し、再接続時に自動再送するロジックを実装予定。
- Configuration Strategy (Frontmatter Exclusion): 「1ファイル・ポータビリティ」は出力HTMLに対する要求であり、入力（Markdown）と設定は分離すべきである。Feature Creepおよび外部依存（`PyYAML`等）の混入を防ぐため、MarkdownへのYAML Frontmatterの実装は却下し、ビルド設定は独立ファイル（`config.toml`）に委譲する設計を維持する。
- Non-Goals (やらないこと): 独自のGUIエディタの開発。複雑なユーザー認証（LMS）の実装。Markdownファイル内へのフロントマター（Frontmatter）の組み込み。

6. 開発プロセスへの指示
本プロジェクトを実装するAIは、以下のステップおよびルールで進めること：
- 基盤(完了): クリーンアーキテクチャに基づく、画像・CSSを埋め込んだ単一HTMLジェネレータの構築。
- 拡張(完了): 汎用対話コンポーネント群（汎用A/Bテスト、投票UI、メモ欄）の設計とメディアファイル参照形式（埋め込み/外部リンク）の選択機能の実装。
- 継続(Next): 設定ファイル管理（config.toml）の導入。
- 同期(Future): FastAPIを用いた同期プロトコルの最小実装（PoC）。

**【厳守ルール】**
- **Gitの強制オプション（`git add -f`, `git push --force` 等）の使用は一切禁止する。** `.gitignore` に記載された非公開ファイルを強制追加してはならない。

Note to AI Developer: 全てのスクリプトは堅牢なエラーハンドリングを含み、SIGINT等に対して安全に終了する構造とすること。また、Markdownの独自拡張記法は、将来的に外部センサーデータと統合することを想定して設計せよ。
