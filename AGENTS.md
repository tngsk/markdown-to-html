# 開発ルール (AGENTS.md)

## コーディング規約と構造
* **HTML/CSS/JSのハードコード禁止:** モジュール化を促進し、ロジックとデザインを分離し、機能の追加や削除を容易にするため、HTML、CSS、Javascriptのハードコードは厳格に禁止されている。常にセットアップを最小限に保ち、PythonやHTMLテンプレート内のインラインスタイルやスクリプトの代わりに、別のCSS/JSファイルやクラスを使用すること。
* **ビルドアーティファクトの直接編集禁止:** 自動生成された出力ファイル（例：`output.html`）を直接編集してはならない。常に基盤となる変換ロジック、ジェネレーター、またはテンプレートを変更すること。リポジトリの汚染を防ぐため、これらの生成されたテスト成果物をリポジトリにコミットしてはならない。
* **依存関係管理:** プロジェクトは依存関係管理に `uv` を使用している。開発環境は `uv sync` を使ってセットアップすること。
* **FastAPIバックエンド:** `src/server.py` はWebSocket (`/ws/sync`) 経由でリアルタイムの視覚同期を処理し、HTTP POST (`/api/data`) で送信されたユーザー入力データをJSONL形式で保存する。サーバーの起動には `uv run server.py` を使用する。
* **テスト実行:** プロジェクトでのテスト実行には `uv run pytest` コマンドを使用する。
* **ドキュメントの記述:** ユーザー向けドキュメント（例：`README.md`）の作成・更新時は、使用手順に焦点を絞り簡潔に記述し、内部の開発ポリシーやガイドラインは含めないこと。

## コンバーターと出力の仕様
* **Markdownコンバーターの実行:** `uv run main.py <input.md> -o <output.html>`
* **ファイルサイズ制限:** ビルド時の検証では、HTMLファイルサイズの最大制限30MBを厳格に適用する（`--force` CLIフラグで回避可能）。ファイルサイズが20MBを超えた場合は警告を発し、埋め込みアセットのサイズ寄与をログに記録する。
* **アセットの最適化:** 'Mono'は非同期注入戦略（Asynchronous Injection Strategy）を使用して、隠しJSONテンプレートストアからBase64アセットを遅延読み込みし、Pillowで画像をWebPに変換し、SVG XMLを直接インライン化してパフォーマンスを最適化する。
* **TOC拡張:** Markdownコンバーターには `toc` 拡張が含まれており、見出しのIDを自動生成する。これは `<mono-sync>` Webコンポーネントがスクロールやチャプターの同期に利用する。

## Webコンポーネントの仕様
* **Vanilla JSによる実装:** Web Componentsは外部依存なしのVanilla JSを使用して実装され、「テンプレート注入戦略（Template Injection Strategy）」を活用する。コンポーネントファイルは `templates/components/<component-name>/` ディレクトリ内に `template.html` と `script.js` として構成されなければならない。
* **スクリプトのインライン化の回避:** グローバルの `window` 変数を設定するインライン `<script>` タグを避けるため、バックエンド設定値（APIやWebSocket URLなど）は `<meta>` タグ（例：`<meta name="mono-api-url" content="...">`）を使ってフロントエンドに渡す。コンポーネントのスクリプトは `document.querySelector('meta[...]').content` を使ってこれらの値を読み取ること。
* **データ保存:** `<mono-poll>`, `<mono-ab-test>`, `<mono-notebook-input>` のようなインタラクティブコンポーネントは、`mono_` をプレフィックスとしたキーを使用して `localStorage` にユーザーデータを保存する。
* **エクスポート機能:** `<mono-export>` コンポーネントはこのデータを集約し、これらのインタラクティブコンポーネントが検出された場合、または `--export` CLIフラグが指定された場合に変換時に自動的に注入される。
* **オプションコンポーネントの除外:** `templates/components/` 内のコンポーネントテンプレートとスクリプトは、`processors/html.py`（`_load_component_templates` と `_load_mono_components_script` 経由）によって自動的に結合され出力HTMLに注入されるため、無効化されたオプションコンポーネント（`mono-export`など）の生のHTML/JSが表示されないよう、この読み込みフェーズでそのディレクトリを明示的にフィルタリングで除外しなければならない。
* **エラーハンドリング:** フロントエンドのエラーハンドリング（特にネットワーク/オフラインの問題）では、ユーザーをガイドするために、生のスタックトレースや標準の `console.error` ログに依存するのではなく、状況に応じた親しみやすい日本語メッセージを使用すること（例：説明文を伴う `console.info` やユーザー向けの `alert`）。

## セキュリティに関する仕様
* **CSPヘッダーの構成:** アプリケーションはリポジトリルートの `config.toml` をセキュリティ設定のために読み込み、`[security]` セクションから `connect-src` と `ws-src` を抽出して Content-Security-Policy (CSP) のmetaタグに入力する。
* **新規リソースの許可:** フロントエンドに導入される新しい外部CDNやリソースが、`processors/html.py` で動的に生成される Content-Security-Policy (CSP) のmetaタグで明示的に許可されていることを確認すること。

## 【厳守ルール】およびAIへの指示
* **Gitの強制オプション（`git add -f`, `git push --force` 等）の使用は一切禁止する。** `.gitignore` に記載された非公開ファイルを強制追加してはならない。
* 全てのスクリプトは堅牢なエラーハンドリングを含み、SIGINT等に対して安全に終了する構造とすること。
* Markdownの独自拡張記法は、将来的に外部センサーデータと統合することを想定して設計すること。
* 高速かつメモリ効率の高いストリームライクな置換を実現するためDOM操作にはPython標準の `re` (正規表現) を用いること。
* YAML Frontmatterの使用は避け、設定ファイル管理（config.toml）を使用すること。

## 実行計画のフォーマットルール
* 実行計画（Execution Plan）を作成する際、pre-commitのステップはハイフンを含めて正確に「Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.」と記述しなければならない。
