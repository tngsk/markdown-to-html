"""
CSS Embedder
============
Embeds CSS content into HTML documents.
"""

import logging
import re
from pathlib import Path
from typing import List

from config import FileProcessingError
from constants import HTML_HEAD_CLOSING_TAG, HTML_OPENING_TAG
from handlers.file import FileHandler


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
        head_match = re.search(HTML_HEAD_CLOSING_TAG, html_content, re.IGNORECASE)
        if head_match:
            insert_pos = head_match.start()
            return (
                html_content[:insert_pos] + style_tag + "\n" + html_content[insert_pos:]
            )

        # <html> タグを探す
        html_match = re.search(HTML_OPENING_TAG, html_content, re.IGNORECASE)
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
