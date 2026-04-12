# 開発ステップとフェーズ管理 (NEXTSTEPS.md)

## 3. 実装フェーズとコンポーネント設計
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

Phase 3: Sync & Collection (Experience Design 優先) - ✅ 実装完了
- Focus Sync (Visual First): 主催者の操作（スクロール、チャプター切り替え）を多数の参加者端末にリアルタイム同期（WebSocket）。
- Data Recovery: ユーザーの入力データをJSONL形式で中央サーバー（FastAPI）へ送信。
- Metadata: ISO8601タイムスタンプ、および環境コンテキストの付与。

Phase 4: Advanced Media & Visual Insight
- Media Integration: 外部エクスポートモジュールのシームレスな埋め込みと高度な視覚化表示。
- Data Visualization: 多次元データの対話的UI。情報伝達効率を最大化する設計とする。

## 6. 開発プロセスへの指示
本プロジェクトを実装するAIは、以下のステップおよびルールで進めること：
- 基盤(完了): クリーンアーキテクチャに基づく、画像・CSSを埋め込んだ単一HTMLジェネレータの構築。
- 拡張(完了): 汎用対話コンポーネント群（汎用A/Bテスト、投票UI、メモ欄）の設計とメディアファイル参照形式（埋め込み/外部リンク）の選択機能の実装。
- 継続(完了): 設定ファイル管理（config.toml）の導入。
- 同期(完了): FastAPIを用いた同期プロトコルの最小実装（PoC）。
- 発展(Next): 外部エクスポートモジュール（situ-export）の統合と高度なデータ可視化UIの実装。
