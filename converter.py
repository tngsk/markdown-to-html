"""
Markdown to HTML Converter
==========================
Main orchestrator that coordinates all conversion components.
"""

import logging
from pathlib import Path

from config import (
    ConversionConfig,
    ConversionError,
    ConversionStats,
    FileProcessingError,
)
from embedders.css import CSSEmbedder
from embedders.media import MediaEmbedder
from handlers.file import FileHandler
from processors.html import HTMLDocumentBuilder
from processors.markdown import MarkdownProcessor


class MarkdownToHTMLConverter:
    """Markdown → 単一HTML変換の統合オーケストレータ"""

    def __init__(self, config: ConversionConfig, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.file_handler = FileHandler(logger)
        self.media_embedder = MediaEmbedder(logger, self.file_handler)
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

            # Step 4: メディア埋め込み
            markdown_dir = self.config.input_file.parent
            html_body, media_count = self.media_embedder.embed_media_in_html(
                html_body, markdown_dir
            )
            self.stats.images_embedded = media_count
            self.logger.info(f"✓ {media_count} 件のメディアをBase64で埋め込みました")

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
