# GIFアニメーション生成サポートツール 設計書 (ANIMATION_TOOL_DESIGN.md)

## 1. ツール概要

本ツールは、複数のスクリーンショット画像（PNG/JPG）を任意の順番で連結し、設定されたリサイズやトリミングを施した上で、Markdownに埋め込み可能なGIFアニメーションを生成する、独立したCLIサポートツールです。動画変換の手間を省き、手順を示す短いGIFを簡単に作成・更新できることを目的としています。

## 2. コア要件とアーキテクチャ

*   **独立したツール:** 本体アプリケーション（Interactive-MD）とは切り離された、ドキュメント作成補助のための独立したCLIスクリプト（例: `tools/make_gif.py` または別プロジェクト）として実装します。
*   **シンプルな構成:** 初期フェーズ（MVP）では `Pillow` (PIL) を使用して基本的なGIF連結・最適化を行います。
*   **依存関係とポータビリティ:** Interactive-MD本体の設計思想（Dependency Minimalism）に従い、`uv` を利用して依存関係を管理し、`uv run` で即座に実行できる構成とします。
*   **柔軟な設定:** CLI引数に加え、設定ファイル (TOML/YAML/JSON) による一括指定をサポートします。
*   **自動化へのアプローチ:** 手動トリミングの手間を省くため、CLI/設定ファイルによる座標指定に加え、テンプレートマッチング等の先進的な自動化機能（後述）をサポートします。

## 3. UI/UX設計 (CLI & 設定ファイル)

### 3.1 CLIインターフェース

```bash
# 基本的な使用方法 (カレントディレクトリの画像を名前順でGIF化)
$ uv run tools/make_gif.py ./screenshots/*.png -o output.gif

# フレームレートやリサイズ、トリミングの指定
$ uv run tools/make_gif.py ./screenshots/*.png -o output.gif --fps 2 --resize 800x600 --crop 100,50,700,550

# 設定ファイルを使用した一括処理
$ uv run tools/make_gif.py --config gif_config.toml
```

### 3.2 設定ファイル (gif_config.toml) の例

プロジェクトごとに設定ファイルを置くことで、再現性を高めます。学習者の理解を深めるための表示時間の調整やアノテーション機能、Interactive-MDとの連携機能を含みます。

```toml
[general]
output_dir = "./docs/assets/gifs"
default_fps = 1.5
loop = 0 # 無限ループ

[[animations]]
name = "login_flow"
output = "login_flow.gif"
fps = 2.0
# 手順を示すGIFで学習者が結果を確認できるよう、最終フレームの停止時間を調整 (ms)
final_delay = 2000
# Interactive-MD の特定の Markdown ファイルに紐付ける
associated_md = "docs/tutorial.md"

# 入力画像。ファイル名によるパターンマッチやリスト指定。
inputs = ["./screenshots/login_1.png", "./screenshots/login_2.png"]
# 共通処理
resize = [800, 600] # [width, height]
crop = [100, 50, 700, 550] # [left, upper, right, lower]

[[animations]]
name = "setting_update"
output = "setting_update.gif"
inputs = ["./screenshots/setting_*.png"]
# 各画像に個別の処理を施す場合（より複雑な要件）
[animations.overrides]
"setting_1.png" = { crop = [0, 0, 800, 400] }
# 学習者の注意を引くためのアノテーション（赤い枠で囲むなど）
"setting_2.png" = { annotation = { type = "rect", color = "red", bounds = [200, 100, 300, 150] } }
```

## 4. 先進的なトリミング・加工機能の模索 (The "Smart Crop" Feature)

単なる座標指定のトリミングでは、OSや画面サイズの違いでUIがずれた場合に毎回座標を再設定する必要があります。そこで、以下の段階的なアプローチでトリミングの手間を軽減します。

### Level 1: テンプレートマッチング (Computer Vision アプローチ)
*   **概要:** OpenCV等を使用し、「トリミングの基準点」となる小さな画像（例: アプリのロゴ、特定のボタン）をテンプレートとして用意します。ツールが各スクリーンショットからそのテンプレートを探し出し、相対的な座標からトリミング範囲を自動計算します。
*   **依存関係:** `tools/` 専用の依存として `opencv-python-headless` を追加します。
*   **メリット:** 軽量で高速。macOSのメニューバーやUIの絶対位置が数ピクセルずれても対応可能。

### Level 2: UI要素の自動検出とフォーカス
*   **概要:** `pytesseract` (OCR) や、UI検出に特化した軽量な物体検出モデルを利用して、特定のテキスト（例: "設定を保存"）やUIコンポーネント（ボタン、ダイアログ）のバウンディングボックスを特定し、その周囲を自動でトリミングします。

### Level 3: ローカルLLM (VLM) による座標生成補助機能
*   **概要:** Ollama等のローカル環境で動く軽量なVision-Language Model (例: `llava`, `moondream2`) を統合します。
*   **位置づけ:** CI/CD環境や低スペック環境での都度実行は避け、「ローカルで1回実行して、得られた座標を \`gif_config.toml\` に書き戻す」座標生成補助機能として実装します。
*   **プロンプト例:**
    `"Extract the bounding box coordinates [xmin, ymin, xmax, ymax] of the main 'Login' dialog in this screenshot."`
*   **メリット:** ピクセル座標を気にせず、自然言語による抽象的な指示でトリミング領域を特定可能。

## 5. 最適化とファイルサイズ管理対策

Interactive-MD本体の「1ファイル30MB制限」に準拠するため、本ツールでは以下の対策を行います。

1.  **パレット最適化:**
    *   色数の増加によるディザリング・画質劣化やサイズ増大を防ぐため、Pillowの `save` メソッドで `optimize=True` を指定します。
    *   可能であれば、複数画像にまたがるグローバルパレットの使用を検討します。
2.  **Base64サイズ見積もり機能:**
    *   GIF画像はBase64化されるとサイズが約1.3倍に膨らむため、本ツールの実行終了時に「このGIFを埋め込んだ際の推定Base64サイズ」を標準出力に表示し、事前に警告します。

## 6. 推奨する実装フェーズ

1.  **フェーズ 1 (MVP):**
    *   `uv` 管理によるスクリプト実行基盤の構築。
    *   CLI引数およびTOML (`gif_config.toml`) によるファイル入力、名前順のソート。
    *   固定ピクセル座標での手動トリミング (`--crop`)、リサイズ (`--resize`) 機能。
    *   `Pillow` を用いたGIF生成（`optimize=True` を活用）。
    *   `final_delay`、アノテーション描画、および Base64 推定サイズ表示のサポート。
2.  **フェーズ 2 (Smart Targeting):**
    *   OpenCV (`opencv-python-headless`) によるテンプレートマッチング (`--align-with template.png`) を用いた自動位置合わせ。
3.  **フェーズ 3 (VLM Integration - 実験的) & ビルド自動化:**
    *   ローカルOllama APIへの接続を利用した座標生成補助機能。
    *   Interactive-MD のビルドプロセス (`main.py`) の前段に、このツールを呼び出す `pre-build` オプションを導入し、ドキュメント生成の「真の自動化」を実現する。

## 7. まとめ

このツールは「画面を録画して編集する」従来のアプローチから、「複数枚のスクリーンショットを投げるだけで、設定やAIに基づいて自動で切り抜かれ、手順GIFが生成される」というアプローチへシフトさせるものです。ドキュメント保守（Interactive-MDのユーザー向けドキュメント等）のコストを大幅に削減します。
