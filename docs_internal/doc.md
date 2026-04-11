プロジェクト名：SITU-MD (SITU Markdown-to-HTML Packager)

本ドキュメントは、開発担当AIが、指示された役割（Instructional Designer / Senior Research Engineer）に基づき、一貫性のある実装を行うための設計仕様書である。

1. プロジェクト概要
SITU-MDは、Markdownファイルを解析し、研究・教育に特化したインタラクティブな単一HTMLファイルを生成するビルドシステムである。

ターゲット環境: ユーザーのブラウザ（幅広いデバイス。主対象は学生・生徒）
コアバリュー: 依存関係ゼロのポータビリティ、教育的フィードバックの即時性、および音響的な時間精度（Sample-Accurate）。
基本原則: オフライン環境でも最低限のHTMLテキストと解説画像が必ず表示・保証されること（情報の欠落防止）。
埋め込み戦略: アンケートや実験用の重いアセット（音声等）は、現場の要件に応じて教員（実施者）が「Base64完全埋め込み（ポータビリティ優先）」か「外部リンク参照（パフォーマンス優先）」かを選択可能なアーキテクチャとする。

2. システムアーキテクチャ（Senior Research Engineer 視点）
2.1 レイヤード・モジュール・アプローチ（現在実装済み）
保守性と拡張性を担保するため、以下のモジュール分割アーキテクチャを採用している。
- Interface Layer (CLI): `main.py` および `config.py` による入出力制御。
- Processing Layer: `processors/` (Markdown変換、HTMLテンプレート構築、カスタム記法処理)。
- Embedding Layer: `embedders/` (画像等のBase64化、CSS/JSのインライン展開)。
- Data I/O Layer: `handlers/` (ファイル読み書き、MIMEタイプ判定)。

2.2 技術スタック（Dependency Minimalism）
- Parser: `markdown` (Python) - 標準的で拡張性に優れる。
- DOM Manipulation: Python標準の `re` (正規表現) - `BeautifulSoup4` のような重い依存を排除し、高速かつメモリ効率の高いストリームライクな置換を実現。
- Dependency Management: `uv` - 爆速かつ再現性の高いモダンなPython環境構築。
- Frontend Runtime: Vanilla JS / Web Components (No Heavy Frameworks)。
- Communication: FastAPI + WebSockets (Phase 2以降、Render等へのデプロイ想定)。

3. 実装フェーズとコンポーネント設計
Phase 1: Core Packager (Foundation) - ✅ 実装完了・安定化
- 1-File Build: CSS, JS, および画像を data:uri (Base64) としてHTMLに埋め込む。
- Syntax Highlighting: Highlight.jsの軽量ロードとコピーボタンの統合。
- Custom Directives (教育向け機能):
  - `{{テキスト}}` → 改行を防ぐ `nowrap` 処理。
  - **Open in Colab 自動変換** → `.ipynb` リンクを検知し、Google Colabのバッジ付き起動リンクへ自動置換。

Phase 2: Scaffolding, Polling & Universal A/B Test (次期開発)
- `@[poll: タイトル](選択肢1, 選択肢2, ...)`：リアルタイム投票コンポーネント（`<situ-poll>`）。イベント駆動設計により通信インフラ（Phase 3）とUIを分離し、現状はLocal Storageに状態をモックする。
- `@[ab-test: タイトル](file_a, file_b)`：汎用A/Bテストコンポーネント（`<situ-ab-test>`）。拡張子からメディア（画像、音声等）を自動判別し、対象に応じた最適な比較UI（クロスフェードやBefore/Afterスライダー等）を提供する。
- `@[notebook-input](id)`：localStorageに永続化される学生用メモ欄。
- 各種メディアファイル (WAV/MP3等) の取り扱い。CLIオプション等でBase64埋め込みと外部リンク参照を教員が切り替えられる設計。

Phase 3: Sync & Collection (Instructional Design 優先)
- Focus Sync (Visual First): 教員の操作（スクロール、チャプター切り替え）を100名までの学生端末にリアルタイム同期（WebSocket）。
- Data Recovery: 学生の入力データをJSONL形式で中央サーバー（FastAPI）へ送信。
- Metadata: ISO8601タイムスタンプ、SITU空間コンテキストの付与。

Phase 4: Acoustic & Visual Insight
- Acoustic Integration: RNBO Web Exportのシームレスな埋め込み。Web Audio APIによるスペクトログラム表示。
- Data Visualization: PCAマップ（散布図）の対話的UI。Tufteの原則に基づき、Data-Ink Ratioを最大化する。

4. UI/UX 設計指針 (Instructional Designer 視点)
- Typography & Style: 学生・生徒の「見やすさ」を最優先とし、現行のクリーンで視認性の高いテンプレートCSSをデフォルトとして維持する。インダストリアル/計測器風（Lab-Gear）のデザインは「選択可能なテーマ機能」として提供する。
- Visual Feedback: 学生の入力に対し、即座に視覚的変化（色の変化、チェックマーク等）を返す。
- Multi-sensory Interaction: 評価ボタンのクリックに対し、適切なオーディオ・フィードバックを考慮。
- Accessibility: セマンティックなHTML構造を維持。キーボード操作によるフォーカス移動を保証。

5. 運用上の制約と堅牢性 (Operational Safety)
- Resource Monitoring: Raspberry Pi 5でのビルド時、大量のメディアファイルのBase64変換によるメモリ消費を考慮し、正規表現ベースの省メモリ処理を採用。
- Robustness: ネットワーク切断時、学生の入力データを一時的にLocal Storageへ退避し、再接続時に自動再送するロジックを実装予定。
- Non-Goals (やらないこと): 独自のGUIエディタの開発。複雑なユーザー認証（LMS）の実装。

6. 開発プロセスへの指示
本プロジェクトを実装するAIは、以下のステップおよびルールで進めること：
- 基盤(完了): クリーンアーキテクチャに基づく、画像・CSSを埋め込んだ単一HTMLジェネレータの構築。
- 拡張(Next): 汎用対話コンポーネント群（汎用A/Bテスト、投票UI、メモ欄）の設計とメディアファイル参照形式（埋め込み/外部リンク）の選択機能の実装。
- 同期(Future): FastAPIを用いた同期プロトコルの最小実装（PoC）。

**【厳守ルール】**
- **Gitの強制オプション（`git add -f`, `git push --force` 等）の使用は一切禁止する。** `.gitignore` に記載された非公開ファイルを強制追加してはならない。

Note to AI Developer: 全てのスクリプトは堅牢なエラーハンドリングを含み、SIGINT等に対して安全に終了する構造とすること。また、Markdownの独自拡張記法は、将来的にSITUの空間センサーデータと統合することを想定して設計せよ。
