"""
Markdown Processor
==================
Converts Markdown content to intermediate HTML.
"""

import logging
import re

import markdown

from config import ConversionError
from constants import (
    HTML_POLL_COMPONENT_TEMPLATE,
    HTML_NOTEBOOK_COMPONENT_TEMPLATE,
    MARKDOWN_EXTENSIONS,
    MARKDOWN_POLL_PATTERN,
    MARKDOWN_NOTEBOOK_PATTERN,
)
from handlers.file import FileHandler


class MarkdownProcessor:
    """Markdownから中間HTMLへの変換処理"""

    def __init__(self, logger: logging.Logger, file_handler: FileHandler):
        self.logger = logger
        self.file_handler = file_handler

    def _preprocess_polls(self, markdown_content: str) -> str:
        """
        @[poll: タイトル](選択肢A, 選択肢B, ...) を <situ-poll> に変換する
        Markdownパーサーがリンクと誤認する前に前処理を行う。
        """
        pattern = re.compile(MARKDOWN_POLL_PATTERN)

        def replacer(match: re.Match) -> str:
            title = match.group(1).strip()
            options = match.group(2).strip()

            # HTML属性用にエスケープ
            safe_title = title.replace('"', "&quot;")
            safe_options = options.replace('"', "&quot;")

            return HTML_POLL_COMPONENT_TEMPLATE.format(
                title=safe_title, options=safe_options
            )

        result = pattern.sub(replacer, markdown_content)
        if markdown_content != result:
            self.logger.debug("投票コンポーネント前処理完了: @[poll] → <situ-poll>")
        return result

    def _preprocess_notebooks(self, markdown_content: str) -> str:
        """
        @[notebook-input](id) を <situ-notebook-input> に変換する
        Markdownパーサーがリンクと誤認する前に前処理を行う。
        """
        pattern = re.compile(MARKDOWN_NOTEBOOK_PATTERN)

        def replacer(match: re.Match) -> str:
            input_id = match.group(1).strip()
            # エスケープ
            safe_id = input_id.replace('"', "&quot;")
            return HTML_NOTEBOOK_COMPONENT_TEMPLATE.format(id=safe_id)

        result = pattern.sub(replacer, markdown_content)
        if markdown_content != result:
            self.logger.debug("ノートブックコンポーネント前処理完了: @[notebook-input] → <situ-notebook-input>")
        return result

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
            markdown_content = self._preprocess_polls(markdown_content)
            markdown_content = self._preprocess_notebooks(markdown_content)
            html = markdown.markdown(markdown_content, extensions=MARKDOWN_EXTENSIONS)
            self.logger.debug("Markdown → HTML 変換完了")
            return html
        except Exception as e:
            raise ConversionError(f"Markdown変換エラー: {e}") from e
