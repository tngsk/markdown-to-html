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
    HTML_AB_TEST_COMPONENT_TEMPLATE,
    HTML_GROUP_ASSIGNMENT_COMPONENT_TEMPLATE,
    HTML_NOTEBOOK_COMPONENT_TEMPLATE,
    HTML_POLL_COMPONENT_TEMPLATE,
    HTML_REACTION_COMPONENT_TEMPLATE,
    HTML_SESSION_JOIN_COMPONENT_TEMPLATE,
    HTML_TEXTFIELD_COMPONENT_TEMPLATE,
    MARKDOWN_AB_TEST_PATTERN,
    MARKDOWN_EXTENSIONS,
    MARKDOWN_GROUP_ASSIGNMENT_PATTERN,
    MARKDOWN_NOTEBOOK_PATTERN,
    MARKDOWN_POLL_PATTERN,
    MARKDOWN_REACTION_PATTERN,
    MARKDOWN_SESSION_JOIN_PATTERN,
    MARKDOWN_TEXTFIELD_PATTERN,
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

    def _preprocess_textfield(self, markdown_content: str) -> str:
        """
        @[textfield: placeholder] または @[textfiled: placeholder] または @[textfield: size:X (placeholder)] を <situ-textfield-input> に変換する
        """
        pattern = re.compile(MARKDOWN_TEXTFIELD_PATTERN)

        def replacer(match: re.Match) -> str:
            content = match.group(1).strip()

            # Check for size:X (placeholder) format
            size_match = re.match(r"size:\s*(\d+)(?:\s*\((.*?)\))?", content)
            if size_match:
                size = size_match.group(1)
                placeholder = size_match.group(2)
                if placeholder is None:
                    placeholder = ""
                placeholder = placeholder.strip()
                size_attr = f' size="{size}"'
            else:
                placeholder = content
                size_attr = ""

            safe_placeholder = placeholder.replace('"', "&quot;")
            return HTML_TEXTFIELD_COMPONENT_TEMPLATE.format(
                placeholder=safe_placeholder,
                size_attr=size_attr
            )

        result = pattern.sub(replacer, markdown_content)
        if markdown_content != result:
            self.logger.debug(
                "テキストフィールドコンポーネント前処理完了: @[textfield] → <situ-textfield-input>"
            )
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
            self.logger.debug(
                "ノートブックコンポーネント前処理完了: @[notebook-input] → <situ-notebook-input>"
            )
        return result

    def _preprocess_ab_tests(self, markdown_content: str) -> str:
        """
        @[ab-test: タイトル](file_a, file_b) を <situ-ab-test> に変換する
        Markdownパーサーがリンクと誤認する前に前処理を行う。
        """
        pattern = re.compile(MARKDOWN_AB_TEST_PATTERN)

        def replacer(match: re.Match) -> str:
            title = match.group(1).strip()
            src_a = match.group(2).strip()
            src_b = match.group(3).strip()

            # HTML属性用にエスケープ
            safe_title = title.replace('"', "&quot;")
            safe_src_a = src_a.replace('"', "&quot;")
            safe_src_b = src_b.replace('"', "&quot;")

            return HTML_AB_TEST_COMPONENT_TEMPLATE.format(
                title=safe_title, src_a=safe_src_a, src_b=safe_src_b
            )

        result = pattern.sub(replacer, markdown_content)
        if markdown_content != result:
            self.logger.debug("A/Bテスト前処理完了: @[ab-test] → <situ-ab-test>")
        return result

    def _preprocess_reactions(self, markdown_content: str) -> str:
        pattern = re.compile(MARKDOWN_REACTION_PATTERN)

        def replacer(match: re.Match) -> str:
            options = match.group(1).strip()
            safe_options = options.replace('"', "&quot;")
            return HTML_REACTION_COMPONENT_TEMPLATE.format(options=safe_options)

        result = pattern.sub(replacer, markdown_content)
        if markdown_content != result:
            self.logger.debug("リアクション前処理完了: @[reaction] → <situ-reaction>")
        return result

    def _preprocess_session_join(self, markdown_content: str) -> str:
        pattern = re.compile(MARKDOWN_SESSION_JOIN_PATTERN)

        def replacer(match: re.Match) -> str:
            title = match.group(1).strip()
            safe_title = title.replace('"', "&quot;")
            return HTML_SESSION_JOIN_COMPONENT_TEMPLATE.format(title=safe_title)

        result = pattern.sub(replacer, markdown_content)
        if markdown_content != result:
            self.logger.debug(
                "セッション参加前処理完了: @[session-join] → <situ-session-join>"
            )
        return result

    def _preprocess_group_assignment(self, markdown_content: str) -> str:
        pattern = re.compile(MARKDOWN_GROUP_ASSIGNMENT_PATTERN)

        def replacer(match: re.Match) -> str:
            title = match.group(1).strip()
            safe_title = title.replace('"', "&quot;")
            return HTML_GROUP_ASSIGNMENT_COMPONENT_TEMPLATE.format(title=safe_title)

        result = pattern.sub(replacer, markdown_content)
        if markdown_content != result:
            self.logger.debug(
                "グループ分け前処理完了: @[group-assignment] → <situ-group-assignment>"
            )
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
            markdown_content = self._preprocess_ab_tests(markdown_content)
            markdown_content = self._preprocess_notebooks(markdown_content)
            markdown_content = self._preprocess_textfield(markdown_content)
            markdown_content = self._preprocess_reactions(markdown_content)
            markdown_content = self._preprocess_session_join(markdown_content)
            markdown_content = self._preprocess_group_assignment(markdown_content)
            html = markdown.markdown(markdown_content, extensions=MARKDOWN_EXTENSIONS)
            self.logger.debug("Markdown → HTML 変換完了")
            return html
        except Exception as e:
            raise ConversionError(f"Markdown変換エラー: {e}") from e
