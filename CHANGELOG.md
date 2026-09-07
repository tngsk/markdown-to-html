# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `minimal` プロファイルによる完全静的ドキュメント出力（Zero-JS、画像直接Data URI埋め込み、コードブロックアンラップ、CSP `script-src 'none'`、未対応コンポーネント検知・中断）
- `BaseComponentParser`、`mono-badge`、`mono-link` における後置属性構文（`{.class #id}`）の共通解釈とマージ機能
- 蛍光マーカー記法（`==テキスト=={color}`）および蛍光アンダーライン記法（`++テキスト++{color}`）の軽量インライン構文（5色対応: yellow, pink, green, cyan, orange）
- 複数行改行に対応したグラデーション強調描画スタイル（`box-decoration-break: clone`）
- プレゼンテーションモード（`-p presentation`）における手書き蛍光ブラシ機能（`mono-brush`）の標準統合

### Changed
- `mono-link` パーサーにおいて明示指定されたラベルをカードタイトルとして最優先し、OGPタイトルをフォールバックとして扱うよう仕様統一
- `mono-export` においてサーバー送信時のHTTPステータスおよびレスポンスJSON内の `status === 'success'` の二重検証を実装
- 手書きブラシのトグル操作を `B` キー（および `Esc` で解除）へと刷新し、マーカー調の蛍光赤ピンク（`rgba(244, 63, 94, 0.75)`）による一定ストローク描画へ変更
- プレゼンター機能（`mono-presenter`）のステータスを開発中（wip / experimental）へ変更
- ドキュメント体系（`README.md`, `doc/SKILL.md`, `AGENTS.md`）の実装整合性訂正（PDFコマンド、サーバー起動コマンド、テキストサイズ記法、教育系コンポーネントの仕様等）

### Fixed
- `MediaEmbedder` におけるパス境界検証（`markdown_dir` および `Path.cwd()`）と通常ファイル検証（`is_file()`）を復元し、ディレクトリトラバーサルによる意図しないファイル埋め込みを防止
- `ComponentRegistry` において `ALLOWED_COMPONENTS` リストによる明示的なコンポーネント走査・インポート制限を復元
- PDF出力失敗時の戻り値検証とCLI終了コード（非ゼロ）へのエラー伝播
- HTML出力先とPDF出力先に同一パスが指定された場合の書込み前衝突検出（`ConfigurationError`）および未知プロファイルの検証

## [2.0.0] - 2026-09-03

### Added
- 3×3 ミニマリスト・デザイントークン体系（Typography Trinity: .text-display, .text-body, .text-compact / Spacing Trinity: --space-flow, --space-group, --space-item）
- @interactive オプトイン・パッケージングアーキテクチャ
- Playwright E2E による完全均一余白・流体スケール自動検証
- CLI `--version`（`-V`）フラグ

### Changed
- 全コアWebコンポーネント（mono-layout, mono-section, mono-zoom, mono-theme, mono-link等）のトークン直結リファクタリング
- mono-image の非WebComponentパーサー最適化（アセット探索スキップ）
- フルスクリーン流体CSS Grid（最大1800px、画面占有率92%）

### Deprecated
- mono-brush（将来的な手書き描画機能の非推奨化）

### Removed
- mono-spacer（空ディレクトリ）
- mono-sync（SSE同期用コンポーネント）

### Fixed
- 流体タイポグラフィにおけるvw係数過大によるスケール停止不具合の解消
- 要素間垂直マージンの完全均一化（112px）
