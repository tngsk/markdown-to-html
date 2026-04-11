#!/usr/bin/env python3
"""
Markdown to Single-File HTML Converter
======================================
Converts Markdown documents to self-contained HTML files with embedded
images (Base64) and CSS, designed for local distribution.

Author: Engineering Team
License: MIT
"""

import argparse
import base64
import logging
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import markdown

# ============================================================================
# Logging Configuration
# ============================================================================


def configure_logging(verbose: bool = False) -> logging.Logger:
    """
    標準的なロギング設定を初期化する。

    Args:
        verbose: True の場合、DEBUG レベルのログを出力

    Returns:
        設定済みのLoggerインスタンス
    """
    logger = logging.getLogger("markdown_converter")
    logger.handlers.clear()  # 既存ハンドラをリセット

    # ログレベルの決定
    level = logging.DEBUG if verbose else logging.INFO

    # コンソールハンドラ
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # ログフォーマッタ
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.setLevel(level)

    return logger


# ============================================================================
# Custom Exceptions
# ============================================================================


class ConversionError(Exception):
    """変換処理中に発生する汎用エラー"""

    pass


class FileProcessingError(ConversionError):
    """ファイル処理エラー"""

    pass


class ImageEmbeddingError(ConversionError):
    """画像埋め込みエラー"""

    pass


class CSSEmbeddingError(ConversionError):
    """CSS埋め込みエラー"""

    pass


# ============================================================================
# Data Classes & Configuration
# ============================================================================


@dataclass
class ConversionConfig:
    """変換処理の設定を保持するデータクラス"""

    input_file: Path
    output_file: Optional[Path]
    css_files: Optional[List[Path]]
    template_path: Optional[Path] = None
    verbose: bool = False
    excluded_tags: Optional[List[str]] = None

    def resolve_output_file(self) -> Path:
        """出力ファイルパスを決定する（未指定時は入力ファイル名から生成）"""
        if self.output_file:
            return self.output_file
        return self.input_file.with_suffix(".html")


@dataclass
class ConversionStats:
    """変換結果の統計情報"""

    images_embedded: int = 0
    css_files_embedded: int = 0
    output_file_size: int = 0
    markdown_file: Optional[str] = None
    output_file: Optional[str] = None


# ============================================================================
# MIME Type Management
# ============================================================================


class MIMETypeRegistry:
    """ファイル拡張子とMIMEタイプのマッピング管理"""

    DEFAULT_REGISTRY = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".svg": "image/svg+xml",
        ".bmp": "image/bmp",
        ".tiff": "image/tiff",
    }

    def __init__(self, registry: Optional[Dict[str, str]] = None):
        self.registry = registry or self.DEFAULT_REGISTRY.copy()

    def get_mime_type(self, file_path: Path) -> str:
        """ファイルパスからMIMEタイプを取得"""
        ext = file_path.suffix.lower()
        return self.registry.get(ext, "application/octet-stream")


# ============================================================================
# Core Processing Classes
# ============================================================================


class FileHandler:
    """ファイルI/O操作を管理するクラス"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def read_text(self, file_path: Path, encoding: str = "utf-8") -> str:
        """テキストファイルを読み込む"""
        try:
            self.logger.debug(f"読み込み中: {file_path}")
            return file_path.read_text(encoding=encoding)
        except FileNotFoundError as e:
            raise FileProcessingError(f"ファイルが見つかりません: {file_path}") from e
        except Exception as e:
            raise FileProcessingError(
                f"ファイル読み込みエラー ({file_path}): {e}"
            ) from e

    def read_binary(self, file_path: Path) -> bytes:
        """バイナリファイルを読み込む"""
        try:
            self.logger.debug(f"読み込み中 (バイナリ): {file_path}")
            return file_path.read_bytes()
        except FileNotFoundError as e:
            raise FileProcessingError(f"ファイルが見つかりません: {file_path}") from e
        except Exception as e:
            raise FileProcessingError(
                f"バイナリファイル読み込みエラー ({file_path}): {e}"
            ) from e

    def write_text(
        self, file_path: Path, content: str, encoding: str = "utf-8"
    ) -> None:
        """テキストファイルを書き込む"""
        try:
            self.logger.debug(f"書き込み中: {file_path}")
            file_path.write_text(content, encoding=encoding)
        except Exception as e:
            raise FileProcessingError(
                f"ファイル書き込みエラー ({file_path}): {e}"
            ) from e


class ImageEmbedder:
    """画像ファイルをBase64エンコードして埋め込むクラス"""

    def __init__(self, logger: logging.Logger, file_handler: FileHandler):
        self.logger = logger
        self.file_handler = file_handler
        self.mime_registry = MIMETypeRegistry()

    def encode_image_to_base64(self, image_path: Path) -> str:
        """画像ファイルをBase64エンコード"""
        if not image_path.exists():
            raise ImageEmbeddingError(f"画像ファイルが見つかりません: {image_path}")

        try:
            image_data = self.file_handler.read_binary(image_path)
            return base64.b64encode(image_data).decode("utf-8")
        except FileProcessingError:
            raise
        except Exception as e:
            raise ImageEmbeddingError(
                f"Base64エンコード失敗 ({image_path}): {e}"
            ) from e

    def embed_images_in_html(
        self, html_content: str, markdown_dir: Path
    ) -> Tuple[str, int]:
        """
        HTMLの<img>タグをBase64埋め込みデータに置換

        Args:
            html_content: 変換対象のHTML文字列
            markdown_dir: Markdownファイルが存在するディレクトリ

        Returns:
            (変換後のHTML, 埋め込み画像数)
        """
        # パターン: <img ...src="..." ... > 形式の画像タグを検索
        pattern = re.compile(r'<img\s+([^>]*?)src="([^"]+)"([^>]*)/?>', re.IGNORECASE)

        image_count = 0

        def replacer(match: re.Match) -> str:
            nonlocal image_count
            before_src = match.group(1)
            src_value = match.group(2)
            after_src = match.group(3)

            # 相対パスを絶対パスに解決
            image_path = (markdown_dir / src_value).resolve()

            if not image_path.exists():
                self.logger.warning(f"画像ファイルが見つかりません: {src_value}")
                return match.group(0)

            try:
                base64_data = self.encode_image_to_base64(image_path)
                mime_type = self.mime_registry.get_mime_type(image_path)
                image_count += 1
                self.logger.debug(f"埋め込み: {image_path.name} ({mime_type})")
                return f'<img {before_src}src="data:{mime_type};base64,{base64_data}"{after_src}>'
            except ImageEmbeddingError as e:
                self.logger.error(f"画像埋め込み失敗: {e}")
                return match.group(0)

        result = pattern.sub(replacer, html_content)
        return result, image_count


class CSSEmbedder:
    """CSSファイルを<style>タグで埋め込むクラス"""

    def __init__(self, logger: logging.Logger, file_handler: FileHandler):
        self.logger = logger
        self.file_handler = file_handler

    def load_css_files(self, css_file_paths: List[Path]) -> str:
        """
        複数のCSSファイルを読み込む

        Args:
            css_file_paths: CSSファイルパスのリスト

        Returns:
            結合されたCSS文字列
        """
        css_contents = []

        for css_path in css_file_paths:
            css_path = Path(css_path)
            if not css_path.exists():
                self.logger.warning(f"CSSファイルが見つかりません: {css_path}")
                continue

            try:
                content = self.file_handler.read_text(css_path)
                css_contents.append(content)
                self.logger.debug(f"CSS読み込み完了: {css_path.name}")
            except FileProcessingError as e:
                self.logger.error(f"CSS読み込み失敗: {e}")

        return "\n".join(css_contents)

    def embed_css_in_html(self, html_content: str, css_content: str) -> str:
        """
        CSSコンテンツを<style>タグで埋め込む

        Args:
            html_content: 対象のHTML
            css_content: 埋め込むCSS

        Returns:
            CSS埋め込み後のHTML
        """
        if not css_content:
            return html_content

        style_tag = f"<style>\n{css_content}\n</style>"

        # </head> の直前に挿入
        head_match = re.search(r"</head>", html_content, re.IGNORECASE)
        if head_match:
            insert_pos = head_match.start()
            return (
                html_content[:insert_pos] + style_tag + "\n" + html_content[insert_pos:]
            )

        # <html> タグを探す
        html_match = re.search(r"<html[^>]*>", html_content, re.IGNORECASE)
        if html_match:
            insert_pos = html_match.end()
            return (
                html_content[:insert_pos]
                + "\n"
                + style_tag
                + "\n"
                + html_content[insert_pos:]
            )

        # どちらもない場合は最初に挿入
        return style_tag + "\n" + html_content


class MarkdownProcessor:
    """Markdownから中間HTMLへの変換処理"""

    def __init__(self, logger: logging.Logger, file_handler: FileHandler):
        self.logger = logger
        self.file_handler = file_handler

    def convert_markdown_to_html(self, markdown_content: str) -> str:
        """
        MarkdownをHTMLに変換

        Args:
            markdown_content: Markdown形式の文字列

        Returns:
            HTML形式の文字列

        Raises:
            ConversionError: 変換に失敗した場合
        """
        try:
            html = markdown.markdown(
                markdown_content, extensions=["fenced_code", "tables", "nl2br"]
            )
            self.logger.debug("Markdown → HTML 変換完了")
            return html
        except Exception as e:
            raise ConversionError(f"Markdown変換エラー: {e}") from e


class HTMLDocumentBuilder:
    """テンプレートベースのHTMLドキュメント生成クラス"""

    # ファイルパス定数
    TEMPLATES_DIR = Path(__file__).parent / "templates"
    DEFAULT_TEMPLATE_PATH = TEMPLATES_DIR / "default.html"

    # 外部リソースURL定数
    HIGHLIGHT_JS_VERSION = "11.9.0"
    HIGHLIGHT_JS_CDN_CSS = f"https://cdnjs.cloudflare.com/ajax/libs/highlight.js/{HIGHLIGHT_JS_VERSION}/styles/atom-one-dark.min.css"
    HIGHLIGHT_JS_CDN_JS = f"https://cdnjs.cloudflare.com/ajax/libs/highlight.js/{HIGHLIGHT_JS_VERSION}/highlight.min.js"

    def __init__(self, logger: logging.Logger, template_path: Optional[Path] = None):
        self.logger = logger
        self.template_path = template_path or self.DEFAULT_TEMPLATE_PATH

    def build_document(
        self,
        html_body: str,
        css_content: Optional[str] = None,
        title: str = "Document",
        excluded_tags: Optional[List[str]] = None,
    ) -> str:
        """
        テンプレートとHTML断片からドキュメントを生成

        Args:
            html_body: <body>に挿入するHTML
            css_content: <head>に挿入するCSS（オプション）
            title: ドキュメントのタイトル

        Returns:
            完全なHTMLドキュメント
        """
        try:
            # テンプレートを読み込む
            template_content = self.template_path.read_text(encoding="utf-8")
            self.logger.debug(f"テンプレート読み込み: {self.template_path}")
        except FileNotFoundError as e:
            raise ConversionError(
                f"テンプレートファイルが見つかりません: {self.template_path}"
            ) from e
        except Exception as e:
            raise ConversionError(f"テンプレート読み込みエラー: {e}") from e

        # コードブロック拡張（コピーボタン、シンタックスハイライト準備）
        html_body = self._enhance_code_blocks(html_body)

        # テーブルインラインスタイル削除
        html_body = self._remove_table_inline_styles(html_body)

        # 除外タグ削除
        html_body = self._remove_excluded_tags(html_body, excluded_tags)

        # カスタム記法処理（{{...}} → <span class="nowrap">...</span>）
        html_body = self._replace_custom_nowrap(html_body)

        # プレースホルダーを置換
        safe_title = self._escape_html(title)
        css_block = self._build_css_block(css_content)

        # コードブロック用リソース（CSS/JS）を読み込む
        highlight_js_css = self._build_highlight_js_link()
        code_block_css = self._load_code_block_css()
        highlight_js = self._load_highlight_js_script()
        copy_button_js = self._load_copy_button_script()

        doc = template_content.replace("{TITLE}", safe_title)
        doc = doc.replace("{CSS_BLOCK}", css_block)
        doc = doc.replace("{HIGHLIGHT_JS_CSS}", highlight_js_css)
        doc = doc.replace("{CODE_BLOCK_CSS}", code_block_css)
        doc = doc.replace("{BODY}", html_body)
        doc = doc.replace("{HIGHLIGHT_JS}", highlight_js)
        doc = doc.replace("{COPY_BUTTON_JS}", copy_button_js)

        return doc

    def _build_css_block(self, css_content: Optional[str]) -> str:
        """CSSブロックを構築（ない場合は空文字列）"""
        if not css_content:
            return ""
        return f"    <style>\n{css_content}\n    </style>\n"

    def extract_title_from_html(self, html_content: str) -> str:
        """
        HTMLから最初の<h1>をタイトルとして抽出

        Args:
            html_content: HTML文字列

        Returns:
            抽出されたタイトル（デフォルト: "Document"）
        """
        match = re.search(r"<h1>(.+?)</h1>", html_content)
        if match:
            # HTMLタグを削除
            title = re.sub(r"<[^>]+>", "", match.group(1))
            return title[:60]  # 最大60文字
        return "Document"

    @staticmethod
    def _escape_html(text: str) -> str:
        """HTML特殊文字をエスケープ"""
        replacements = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;",
        }
        for char, escaped in replacements.items():
            text = text.replace(char, escaped)
        return text

    def _enhance_code_blocks(self, html_content: str) -> str:
        """
        コードブロックを拡張（コピーボタン、シンタックスハイライト対応）

        <pre><code class="language-python">...</code></pre> 形式に変換
        """
        # <pre><code ...>...</code></pre> パターンを検索
        pattern = re.compile(
            r'<pre><code(?:\s+class="([^"]*)")?>(.*?)</code></pre>', re.DOTALL
        )

        def replacer(match: re.Match) -> str:
            lang_class = match.group(1) or ""
            code_content = match.group(2)

            # 言語クラスから言語名を抽出（"language-python" → "python"）
            language = ""
            if lang_class:
                lang_match = re.search(r"language-(\w+)", lang_class)
                if lang_match:
                    language = lang_match.group(1)

            # コードブロックの新しい構造を構築
            enhanced = f'''<div class="code-block-wrapper" data-language="{language}">
    <div class="code-block-header">
        <span class="code-language">{language.capitalize() if language else "CODE"}</span>
        <button class="copy-button" title="コードをコピー">📋 Copy</button>
    </div>
    <pre><code class="hljs language-{language}">{code_content}</code></pre>
</div>'''
            return enhanced

        result = pattern.sub(replacer, html_content)
        return result

    def _remove_table_inline_styles(self, html_content: str) -> str:
        """
        テーブルタグから不要なインラインスタイルを削除

        Markdownライブラリが付与する text-align: left; などを除去
        """
        # <td style="..."> → <td>
        # <th style="..."> → <th>
        pattern = re.compile(r'<(td|th)\s+style="[^"]*?"', re.IGNORECASE)
        result = pattern.sub(r"<\1", html_content)
        return result

    def _remove_excluded_tags(
        self, html_content: str, excluded_tags: Optional[List[str]]
    ) -> str:
        """
        指定されたタグをHTMLから削除（タグとその中身も一緒に削除）

        Args:
            html_content: HTML文字列
            excluded_tags: 削除対象のタグ名リスト（例：["hr", "div"]）

        Returns:
            タグ削除後のHTML
        """
        if not excluded_tags:
            return html_content

        for tag in excluded_tags:
            # 自己終了タグ（<hr /> など）
            pattern_self_closing = re.compile(rf"<{tag}[^>]*/?\s*>", re.IGNORECASE)
            html_content = pattern_self_closing.sub("", html_content)

            # 開閉タグ（<div>...</div> など）
            pattern_paired = re.compile(
                rf"<{tag}[^>]*>.*?</{tag}>", re.IGNORECASE | re.DOTALL
            )
            html_content = pattern_paired.sub("", html_content)

            self.logger.debug(f"タグ削除完了: {tag}")

        return html_content

    def _replace_custom_nowrap(self, html_content: str) -> str:
        """
        カスタム記法 {{...}} をnowr改行しないテキストに変換

        {{連結テキスト}} → <span class="nowrap">連結テキスト</span>

        Args:
            html_content: HTML文字列

        Returns:
            記法処理後のHTML
        """
        pattern = re.compile(r"\{\{(.*?)\}\}")
        result = pattern.sub(r'<span class="nowrap">\1</span>', html_content)
        self.logger.debug(
            'カスタム記法処理完了: {{...}} → <span class="nowrap">...</span>'
        )
        return result

    def _build_highlight_js_link(self) -> str:
        """Highlight.js CDN リンクを構築"""
        return f'<link rel="stylesheet" href="{self.HIGHLIGHT_JS_CDN_CSS}">'

    def _load_code_block_css(self) -> str:
        """code-block.css ファイルを読み込んで <style> タグで返す"""
        css_file = self.TEMPLATES_DIR / "code-block.css"
        try:
            css_content = css_file.read_text(encoding="utf-8")
            return f"<style>\n{css_content}\n</style>"
        except FileNotFoundError:
            self.logger.warning(f"code-block.css が見つかりません: {css_file}")
            return ""
        except Exception as e:
            self.logger.warning(f"code-block.css の読み込みエラー: {e}")
            return ""

    def _load_highlight_js_script(self) -> str:
        """Highlight.js スクリプトタグを構築"""
        return f'<script src="{self.HIGHLIGHT_JS_CDN_JS}"></script>'

    def _load_copy_button_script(self) -> str:
        """copy-button.js ファイルを読み込んで <script> タグで返す"""
        js_file = self.TEMPLATES_DIR / "copy-button.js"
        try:
            js_content = js_file.read_text(encoding="utf-8")
            return f"<script>\n{js_content}\n</script>"
        except FileNotFoundError:
            self.logger.warning(f"copy-button.js が見つかりません: {js_file}")
            return ""
        except Exception as e:
            self.logger.warning(f"copy-button.js の読み込みエラー: {e}")
            return ""


# ============================================================================
# Main Converter Class
# ============================================================================


class MarkdownToHTMLConverter:
    """Markdown → 単一HTML変換の統合オーケストレータ"""

    def __init__(self, config: ConversionConfig, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.file_handler = FileHandler(logger)
        self.image_embedder = ImageEmbedder(logger, self.file_handler)
        self.css_embedder = CSSEmbedder(logger, self.file_handler)
        self.markdown_processor = MarkdownProcessor(logger, self.file_handler)
        self.html_document_builder = HTMLDocumentBuilder(
            logger, template_path=config.template_path
        )
        self.stats = ConversionStats()

    def convert(self) -> bool:
        """
        変換処理の実行

        Returns:
            成功時True、失敗時False
        """
        try:
            self.logger.info(f"変換開始: {self.config.input_file}")

            # 除外タグを出力
            if self.config.excluded_tags:
                tags_str = ", ".join(self.config.excluded_tags)
                self.logger.info(f"✓ 除外タグ: {tags_str}")

            # Step 1: Markdown読み込み
            markdown_content = self.file_handler.read_text(self.config.input_file)
            self.logger.info("✓ Markdownファイルを読み込みました")

            # Step 2: Markdown → HTML変換
            html_body = self.markdown_processor.convert_markdown_to_html(
                markdown_content
            )
            self.logger.info("✓ Markdownを中間HTMLに変換しました")

            # Step 3: CSS読み込み
            css_content = ""
            if self.config.css_files:
                css_content = self.css_embedder.load_css_files(self.config.css_files)
                if css_content:
                    self.stats.css_files_embedded = len(self.config.css_files)
                    self.logger.info(
                        f"✓ {len(self.config.css_files)} 個のCSSを読み込みました"
                    )

            # Step 4: 画像埋め込み
            markdown_dir = self.config.input_file.parent
            html_body, image_count = self.image_embedder.embed_images_in_html(
                html_body, markdown_dir
            )
            self.stats.images_embedded = image_count
            self.logger.info(f"✓ {image_count} 件の画像をBase64で埋め込みました")

            # Step 5: HTMLドキュメント生成
            title = self.html_document_builder.extract_title_from_html(html_body)
            html_document = self.html_document_builder.build_document(
                html_body=html_body,
                css_content=css_content if css_content else None,
                title=title,
                excluded_tags=self.config.excluded_tags,
            )
            self.logger.info(
                f"✓ HTMLドキュメント構造を生成しました (タイトル: {title})"
            )

            # Step 6: 出力
            output_file = self.config.resolve_output_file()
            self._write_output(html_document, output_file)

            return True

        except ConversionError as e:
            self.logger.error(f"変換失敗: {e}")
            return False
        except Exception as e:
            self.logger.error(f"予期しないエラー: {e}", exc_info=True)
            return False

    def _write_output(self, html_content: str, output_file: Path) -> None:
        """出力ファイルを書き込み"""
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            self.file_handler.write_text(output_file, html_content)
            self.stats.output_file_size = len(html_content.encode("utf-8"))
            self.logger.info(f"✅ 変換完了: {output_file}")
            self.logger.info(
                f"   ファイルサイズ: {self._format_size(self.stats.output_file_size)}"
            )
        except FileProcessingError as e:
            raise ConversionError(f"出力ファイル書き込み失敗: {e}") from e

    @staticmethod
    def _format_size(size_bytes: float) -> str:
        """バイト数をヒューマンリーダブルなサイズに変換"""
        for unit in ("B", "KB", "MB", "GB"):
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"


# ============================================================================
# CLI Interface
# ============================================================================


def create_argument_parser() -> argparse.ArgumentParser:
    """コマンドラインパーサーを構築"""
    parser = argparse.ArgumentParser(
        prog="markdown-to-html",
        description="Markdown をBase64埋め込み画像・CSS対応の単一HTMLファイルに変換します。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 基本的な変換
  python main.py document.md

  # CSSを埋め込み
  python main.py document.md -c style.css

  # 複数のCSSを埋め込み
  python main.py document.md -c style.css theme.css

  # 出力ファイルを指定
  python main.py document.md -o output.html -c style.css

  # 詳細ログを表示
  python main.py document.md -v

  # カスタムテンプレートを使用
  python main.py document.md -t custom_template.html

  # 除外タグを指定
  python main.py document.md -e hr div

  # 全オプション組み合わせ
  python main.py document.md -o output.html -c style.css -e hr -v
        """,
    )

    parser.add_argument(
        "input_file",
        type=Path,
        help="入力Markdownファイルのパス",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="出力HTMLファイルのパス（省略時は {入力ファイル名}.html）",
    )

    parser.add_argument(
        "-c",
        "--css",
        nargs="+",
        type=Path,
        default=None,
        help="埋め込むCSSファイルのパス（複数指定可能）",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="詳細なログを出力する",
    )

    parser.add_argument(
        "-t",
        "--template",
        type=Path,
        default=None,
        help="カスタムHTMLテンプレートファイルのパス",
    )

    parser.add_argument(
        "-e",
        "--excluded-tags",
        nargs="+",
        type=str,
        default=None,
        help="削除対象のHTMLタグ（複数指定可能。例：-e hr div span）",
    )

    return parser


def print_header(config: ConversionConfig) -> None:
    """処理開始時のヘッダー情報を表示"""
    print("\n" + "=" * 75)
    print("  Markdown → Single-File HTML Converter")
    print("=" * 75)
    print(f"  入力ファイル: {config.input_file}")
    print(f"  出力ファイル: {config.resolve_output_file()}")
    if config.css_files:
        print(f"  CSSファイル:  {', '.join(str(f) for f in config.css_files)}")
    if config.excluded_tags:
        print(f"  除外タグ:     {', '.join(config.excluded_tags)}")
    print("=" * 75 + "\n")


def main() -> int:
    """
    メイン処理

    Returns:
        終了コード（0=成功、1=失敗）
    """
    parser = create_argument_parser()
    args = parser.parse_args()

    # ロギング設定
    logger = configure_logging(verbose=args.verbose)

    # 設定の構築
    config = ConversionConfig(
        input_file=args.input_file,
        output_file=args.output,
        css_files=args.css,
        template_path=args.template,
        verbose=args.verbose,
        excluded_tags=args.excluded_tags,
    )

    # ヘッダー表示
    print_header(config)

    # 変換実行
    converter = MarkdownToHTMLConverter(config, logger)
    success = converter.convert()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
