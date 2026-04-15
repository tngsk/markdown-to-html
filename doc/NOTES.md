# プロジェクト情報と設計指針 (NOTES.md)

## 1. プロジェクト概要
Monoは、Markdownファイルを解析し、特定ドメインに特化したインタラクティブな単一HTMLファイルを生成するビルドシステムである。

ターゲット環境: ユーザーのブラウザ（幅広いデバイス。主対象は参加者・ユーザー）
コアバリュー: 依存関係ゼロのポータビリティ、フィードバックの即時性、および高精度なメディア同期制御。
基本原則: オフライン環境でも最低限のHTMLテキストと解説画像が必ず表示・保証されること（情報の欠落防止）。
埋め込み戦略: アンケートや実験用の重いアセット（音声等）は、現場の要件に応じて実施者が「Base64完全埋め込み（ポータビリティ優先）」か「外部リンク参照（パフォーマンス優先）」かを選択可能なアーキテクチャとする。

## 2. システムアーキテクチャ（Senior Research Engineer 視点）
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

## 4. UI/UX 設計指針 (UX Designer 視点)
- Typography & Style: 参加者の「見やすさ」を最優先とし、現行のクリーンで視認性の高いテンプレートCSSをデフォルトとして維持する。インダストリアル/計測器風（Lab-Gear）のデザインは「選択可能なテーマ機能」として提供する。
- Visual Feedback: ユーザーの入力に対し、即座に視覚的変化（色の変化、チェックマーク等）を返す。
- Multi-sensory Interaction: 操作に対し、適切なマルチメディア・フィードバックを考慮。
- Accessibility: セマンティックなHTML構造を維持。キーボード操作によるフォーカス移動を保証。

## 5. 運用上の制約と堅牢性 (Operational Safety)
- Resource Monitoring: リソース制約のあるエッジデバイス環境でのビルド時、大量のメディアファイルのBase64変換によるメモリ消費を考慮し、正規表現ベースの省メモリ処理を採用。
- Robustness: ネットワーク切断時、ユーザーの入力データを一時的にLocal Storageへ退避し、再接続時に自動再送するロジックを実装予定。
- Configuration Strategy (Frontmatter Exclusion): 「1ファイル・ポータビリティ」は出力HTMLに対する要求であり、入力（Markdown）と設定は分離すべきである。Feature Creepおよび外部依存（`PyYAML`等）の混入を防ぐため、MarkdownへのYAML Frontmatterの実装は却下し、ビルド設定は独立ファイル（`config.toml`）に委譲する設計を維持する。
- Non-Goals (やらないこと): 独自のGUIエディタの開発。複雑なユーザー認証（LMS）の実装。Markdownファイル内へのフロントマター（Frontmatter）の組み込み。


以下は実装済みの機能詳細である。必要に応じて参照すること。

## Phase 3.5 インタラクティブ機能（新規追加）
目的: 参加者の能動的なインタラクションとセッション運用性を向上させる小規模コンポーネント群を追加する。各機能は独立コンポーネントとして実装し、依存先がない場合は安全に非表示（エラーを出さずドキュメントに含めない）になる設計とする。

### 1) mono-reaction（ユーザーリアクション）
- マークダウン構文案: `@[reaction: "手を挙げる,？マーク"]`
- 概要: ユーザーが手を挙げる、質問あり（？）などのリアクションを送れる小さなUI。各リアクションはカウントされ、表示される。
- 実装場所（推奨）:
  - templates/components/mono-reaction/
    - mono-reaction.html
    - mono-reaction.js
    - mono-reaction.css
- 動作:
  - Local Storage キー: `mono_reaction_{component_id}`
  - 送信ペイロード（例）:
    {
      "timestamp": "ISO8601",
      "componentId": "reaction-xxx",
      "reactionType": "hand_up",
      "reactionLabel": "手を挙げる"
    }
  - オフライン時も Local Storage に蓄え、通信復帰時に送信可能。
  - WebSocket インフラが存在する場合は主催者へリアルタイム通知（オプション）。
- 依存: なし（独立で機能）

### 2) mono-session-join（セッション参加）
- マークダウン構文案: `@[session-join: "セッション参加"]`
- 概要: セッション番号を入力して参加するためのコンポーネント。参加状態は Local Storage に保存され、他コンポーネントはこれを参照できる。
- 実装場所（推奨）:
  - templates/components/mono-session-join/
    - mono-session-join.html
    - mono-session-join.js
    - mono-session-join.css
- 動作:
  - Local Storage キー: `mono_session_id`（ドキュメント/ブラウザ単位）
  - 送信ペイロード（例）:
    {
      "timestamp": "ISO8601",
      "sessionId": "SESSION-12345",
      "userId": "generated-uuid"
    }
  - 入力バリデーション（英数字、ハイフン許可）。参加後は確認表示に切替、変更可能。
  - 依存: なし（独立で機能）

### 3) mono-group-assignment（グループ分け）
- マークダウン構文案: `@[group-assignment: "グループ分け"]`
- 概要: セッション参加中のユーザーを指定のロジックでグループ分配し、割り当てられたグループをユーザーにフィードバックする。
- 実装場所（推奨）:
  - templates/components/mono-group-assignment/
    - mono-group-assignment.html
    - mono-group-assignment.js
    - mono-group-assignment.css
- 動作:
  - Local Storage キー: `mono_group_assignment`
  - 送信ペイロード（例）:
    {
      "timestamp": "ISO8601",
      "sessionId": "SESSION-12345",
      "userId": "generated-uuid",
      "groupId": "GROUP-A",
      "groupName": "グループA",
      "assignmentMethod": "round-robin"
    }
  - グループ分配アルゴリズム（選択肢）:
    - round-robin（参加順で割当）
    - random（ランダム）
    - server-driven（サーバからの指示を受信）
  - 依存:
    - 基本動作は mono-session-join の sessionId を参照（セッション未参加時は「セッションに参加してください」と表示し、コンポーネント自体はドキュメントに含めない）。
    - WebSocket やサーバAPI が存在する場合はサーバ側の割当情報を優先して反映。
- エラー挙動:
  - セッション未参加や分配情報未取得時はエラーにせず、ユーザー向けの案内表示のみ行う。
