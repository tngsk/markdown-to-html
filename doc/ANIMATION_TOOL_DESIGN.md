# GIFアニメーション生成サポートツール 設計書 (ANIMATION_TOOL_DESIGN.md)

## 1. ツール概要

本ツールは、複数のスクリーンショット画像（PNG/JPG）を任意の順番で連結し、設定されたリサイズやトリミングを施した上で、Markdownに埋め込み可能なGIFアニメーションを生成する、独立したCLIサポートツールです。動画変換の手間を省き、手順を示す短いGIFを簡単に作成・更新できることを目的としています。

## 2. コア要件とアーキテクチャ

*   **独立したツール:** 本体アプリケーション（Interactive-MD）とは切り離された、ドキュメント作成補助のための独立したCLIスクリプト（例: `tools/make_gif.py` または別プロジェクト）として実装します。
*   **シンプルな構成:** `Pillow` (PIL) や `imageio` などの標準的な画像処理ライブラリを使用します。
*   **柔軟な設定:** CLI引数に加え、設定ファイル (TOML/YAML/JSON) による一括指定をサポートします。
*   **自動化へのアプローチ:** 手動トリミングの手間を省くため、CLI/設定ファイルによる座標指定に加え、先進的な自動化機能（後述）を検討します。

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

プロジェクトごとに設定ファイルを置くことで、再現性を高めます。

```toml
[general]
output_dir = "./docs/assets/gifs"
default_fps = 1.5
loop = 0 # 無限ループ

[[animations]]
name = "login_flow"
output = "login_flow.gif"
fps = 2.0
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
```

## 4. 先進的なトリミング・加工機能の模索 (The "Smart Crop" Feature)

単なる座標指定のトリミングでは、OSや画面サイズの違いでUIがずれた場合に毎回座標を再設定する必要があります。そこで、以下の段階的なアプローチでトリミングの手間を軽減します。

### Level 1: テンプレートマッチング (Computer Vision アプローチ)
*   **概要:** OpenCV等を使用し、「トリミングの基準点」となる小さな画像（例: アプリのロゴ、特定のボタン）をテンプレートとして用意します。ツールが各スクリーンショットからそのテンプレートを探し出し、相対的な座標からトリミング範囲を自動計算します。
*   **メリット:** 軽量で高速。ローカルLLMは不要。UIの絶対位置がずれても対応可能。
*   **デメリット:** テンプレート画像を用意する手間。UIデザインの変更に弱い。

### Level 2: UI要素の自動検出とフォーカス
*   **概要:** `pytesseract` (OCR) や、UI検出に特化した軽量な物体検出モデルを利用して、特定のテキスト（例: "設定を保存"）やUIコンポーネント（ボタン、ダイアログ）のバウンディングボックスを特定し、その周囲を自動でトリミングします。

### Level 3: ローカルLLM (VLM) によるROI (Region of Interest) 抽出
*   **概要:** Ollama等のローカル環境で動く軽量なVision-Language Model (例: `llava`, `moondream2`) を統合します。
*   **プロンプト例:**
    `"Extract the bounding box coordinates [xmin, ymin, xmax, ymax] of the main 'Login' dialog in this screenshot."`
*   **ワークフロー:**
    1.  スクリプトが画像をローカルVLMに投げる。
    2.  VLMが「注目すべき領域（ダイアログや主要コンテンツ）」の座標を返す。
    3.  その座標を少し拡張（パディング）して自動トリミングする。
*   **メリット:** 非常に抽象的で強力な指示が可能。「メインのウィンドウを切り抜いて」といった指示で、ピクセル座標を気にせずトリミングできる。
*   **デメリット:** 推論に時間がかかる（数秒〜十数秒/枚）。環境構築のハードル（GPU/Ollamaのインストール）。

## 5. 推奨する実装フェーズ

1.  **フェーズ 1 (MVP):**
    *   CLI引数およびTOMLによるファイル入力、名前順のソート。
    *   固定ピクセル座標での手動トリミング (`--crop`) とリサイズ (`--resize`) 機能。
    *   `Pillow` を用いたGIF生成。
2.  **フェーズ 2 (Smart Targeting):**
    *   OpenCVによるテンプレートマッチング (`--align-with template.png`) による自動位置合わせ。
3.  **フェーズ 3 (VLM Integration - 実験的):**
    *   オプション機能としてローカルOllama APIへの接続。
    *   `--auto-crop "dialog box"` のような自然言語でのトリミング指定の実装。

## 6. まとめ

このツールは「画面を録画して編集する」従来のアプローチから、「複数枚のスクリーンショットを投げるだけで、設定やAIに基づいて自動で切り抜かれ、手順GIFが生成される」というアプローチへシフトさせるものです。ドキュメント保守（Interactive-MDのユーザー向けドキュメント等）のコストを大幅に削減します。
