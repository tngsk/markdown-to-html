"""
Markdown Processor
==================
Converts Markdown content to intermediate HTML.
"""

import html
import logging
import re

import markdown

from src.config import ConversionError
from src.constants import (
    HTML_AB_TEST_COMPONENT_TEMPLATE,
    HTML_GROUP_ASSIGNMENT_COMPONENT_TEMPLATE,
    HTML_ICON_COMPONENT_TEMPLATE,
    HTML_NOTEBOOK_COMPONENT_TEMPLATE,
    HTML_POLL_COMPONENT_TEMPLATE,
    HTML_REACTION_COMPONENT_TEMPLATE,
    HTML_SESSION_JOIN_COMPONENT_TEMPLATE,
    HTML_SOUND_COMPONENT_TEMPLATE,
    HTML_TEXTFIELD_COMPONENT_TEMPLATE,
    MARKDOWN_AB_TEST_PATTERN,
    MARKDOWN_EXTENSIONS,
    MARKDOWN_GROUP_ASSIGNMENT_PATTERN,
    MARKDOWN_ICON_PATTERN,
    MARKDOWN_LAYOUT_END_PATTERN,
    MARKDOWN_LAYOUT_ROW_PATTERN,
    MARKDOWN_LAYOUT_STACK_PATTERN,
    MARKDOWN_COLUMN_START_PATTERN,
    MARKDOWN_COLUMN_END_PATTERN,
    MARKDOWN_NOTEBOOK_PATTERN,
    MARKDOWN_POLL_PATTERN,
    MARKDOWN_REACTION_PATTERN,
    MARKDOWN_SESSION_JOIN_PATTERN,
    MARKDOWN_SOUND_PATTERN,
    MARKDOWN_TEXTFIELD_PATTERN,
    MARKDOWN_SPACER_PATTERN,
    HTML_SPACER_COMPONENT_TEMPLATE,
)
from src.handlers.file import FileHandler
import markdown.util


class MarkdownProcessor:
    """Markdownから中間HTMLへの変換処理"""

    def __init__(self, logger: logging.Logger, file_handler: FileHandler):
        self.logger = logger
        self.file_handler = file_handler

    def _preprocess_icon(self, markdown_content: str) -> str:
        """
        @[icon: name](size, color, display) を <situ-icon> に変換する
        """
        pattern = re.compile(MARKDOWN_ICON_PATTERN)

        def replacer(match: re.Match) -> str:
            name = match.group(1).strip()
            args_str = match.group(2)

            safe_name = html.escape(name)
            size_attr = ""
            color_attr = ""
            display_attr = ""

            if args_str is not None:
                parts = []
                current = ""
                depth = 0
                for char in args_str:
                    if char == '(':
                        depth += 1
                        current += char
                    elif char == ')':
                        depth -= 1
                        current += char
                    elif char == ',' and depth == 0:
                        parts.append(current.strip())
                        current = ""
                    else:
                        current += char
                parts.append(current.strip())

                args = parts

                if len(args) > 0 and args[0]:
                    size_attr = f' size="{html.escape(args[0])}"'
                if len(args) > 1 and args[1]:
                    color_attr = f' color="{html.escape(args[1])}"'
                if len(args) > 2 and args[2]:
                    display_attr = f' display="{html.escape(args[2])}"'

            return HTML_ICON_COMPONENT_TEMPLATE.format(
                name=safe_name,
                size_attr=size_attr,
                color_attr=color_attr,
                display_attr=display_attr
            )

        result = pattern.sub(replacer, markdown_content)
        if markdown_content != result:
            self.logger.debug("アイコンコンポーネント前処理完了: @[icon] → <situ-icon>")
        return result

    def _preprocess_sound(self, markdown_content: str) -> str:
        """
        @[sound: ラベル](file) または @[sound](file) を <situ-sound> に変換する
        """
        pattern = re.compile(MARKDOWN_SOUND_PATTERN)
        counter = 0

        def replacer(match: re.Match) -> str:
            nonlocal counter
            counter += 1
            label = match.group(1)
            src = match.group(2).strip()

            safe_label = html.escape(label.strip()) if label else ""
            safe_src = html.escape(src)

            return HTML_SOUND_COMPONENT_TEMPLATE.format(
                id=f"sound-{counter}", label=safe_label, src=safe_src
            )

        result = pattern.sub(replacer, markdown_content)
        if markdown_content != result:
            self.logger.debug("効果音コンポーネント前処理完了: @[sound] → <situ-sound>")
        return result

    def _preprocess_polls(self, markdown_content: str) -> str:
        """
        @[poll: タイトル](選択肢A, 選択肢B, ...) を <situ-poll> に変換する
        Markdownパーサーがリンクと誤認する前に前処理を行う。
        """
        pattern = re.compile(MARKDOWN_POLL_PATTERN)
        counter = 0

        def replacer(match: re.Match) -> str:
            nonlocal counter
            counter += 1
            title = match.group(1).strip()
            options = match.group(2).strip()

            # HTML属性用にエスケープ
            safe_title = html.escape(title)
            safe_options = html.escape(options)

            return HTML_POLL_COMPONENT_TEMPLATE.format(
                id=f"poll-{counter}", title=safe_title, options=safe_options
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
        counter = 0

        def replacer(match: re.Match) -> str:
            nonlocal counter
            counter += 1
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

            safe_placeholder = html.escape(placeholder)
            return HTML_TEXTFIELD_COMPONENT_TEMPLATE.format(
                id=f"textfield-{counter}",
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
            safe_id = html.escape(input_id)
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
        counter = 0

        def replacer(match: re.Match) -> str:
            nonlocal counter
            counter += 1
            title = match.group(1).strip()
            src_a = match.group(2).strip()
            src_b = match.group(3).strip()

            # HTML属性用にエスケープ
            safe_title = html.escape(title)
            safe_src_a = html.escape(src_a)
            safe_src_b = html.escape(src_b)

            return HTML_AB_TEST_COMPONENT_TEMPLATE.format(
                id=f"abtest-{counter}", title=safe_title, src_a=safe_src_a, src_b=safe_src_b
            )

        result = pattern.sub(replacer, markdown_content)
        if markdown_content != result:
            self.logger.debug("A/Bテスト前処理完了: @[ab-test] → <situ-ab-test>")
        return result

    def _preprocess_reactions(self, markdown_content: str) -> str:
        pattern = re.compile(MARKDOWN_REACTION_PATTERN)
        counter = 0

        def replacer(match: re.Match) -> str:
            nonlocal counter
            counter += 1
            options = match.group(1).strip()
            safe_options = html.escape(options)
            return HTML_REACTION_COMPONENT_TEMPLATE.format(id=f"reaction-{counter}", options=safe_options)

        result = pattern.sub(replacer, markdown_content)
        if markdown_content != result:
            self.logger.debug("リアクション前処理完了: @[reaction] → <situ-reaction>")
        return result

    def _preprocess_session_join(self, markdown_content: str) -> str:
        pattern = re.compile(MARKDOWN_SESSION_JOIN_PATTERN)

        def replacer(match: re.Match) -> str:
            title = match.group(1).strip()
            safe_title = html.escape(title)
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
            safe_title = html.escape(title)
            return HTML_GROUP_ASSIGNMENT_COMPONENT_TEMPLATE.format(title=safe_title)

        result = pattern.sub(replacer, markdown_content)
        if markdown_content != result:
            self.logger.debug(
                "グループ分け前処理完了: @[group-assignment] → <situ-group-assignment>"
            )
        return result

    def _preprocess_spacer(self, markdown_content: str) -> str:
        """
        @[spacer](width, height) または @[spacer](size) を <situ-spacer> に変換する
        """
        pattern = re.compile(MARKDOWN_SPACER_PATTERN)

        def replacer(match: re.Match) -> str:
            args = match.group(1).split(",")
            width = args[0].strip()
            height = args[1].strip() if len(args) > 1 else width

            safe_width = html.escape(width)
            safe_height = html.escape(height)

            return HTML_SPACER_COMPONENT_TEMPLATE.format(width=safe_width, height=safe_height)

        result = pattern.sub(replacer, markdown_content)
        if markdown_content != result:
            self.logger.debug("スペーサー前処理完了: @[spacer] → <situ-spacer>")
        return result

    def _preprocess_layout(self, markdown_content: str) -> str:
        """
        @[row], @[stack], @[end], :::column, ::: をレイアウトコンポーネントに変換する
        """
        # row
        pattern = re.compile(MARKDOWN_LAYOUT_ROW_PATTERN)
        def row_replacer(match: re.Match) -> str:
            classes = match.group(1).strip() if match.group(1) else ""
            if classes:
                return f'<situ-layout type="row" class="{classes}" markdown="1">'
            return '<situ-layout type="row" markdown="1">'
        result = pattern.sub(row_replacer, markdown_content)

        # stack
        pattern = re.compile(MARKDOWN_LAYOUT_STACK_PATTERN)
        def stack_replacer(match: re.Match) -> str:
            classes = match.group(1).strip() if match.group(1) else ""
            if classes:
                return f'<situ-layout type="stack" class="{classes}" markdown="1">'
            return '<situ-layout type="stack" markdown="1">'
        result = pattern.sub(stack_replacer, result)

        # end
        pattern = re.compile(MARKDOWN_LAYOUT_END_PATTERN)
        result = pattern.sub('</situ-layout>', result)

        # column start
        pattern = re.compile(MARKDOWN_COLUMN_START_PATTERN)
        result = pattern.sub('<div class="column" markdown="1">', result)

        # column end
        pattern = re.compile(MARKDOWN_COLUMN_END_PATTERN)
        result = pattern.sub('</div>', result)

        if markdown_content != result:
            self.logger.debug("レイアウトディレクティブ前処理完了")

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
            markdown_content = self._preprocess_icon(markdown_content)
            markdown_content = self._preprocess_sound(markdown_content)
            markdown_content = self._preprocess_polls(markdown_content)
            markdown_content = self._preprocess_ab_tests(markdown_content)
            markdown_content = self._preprocess_notebooks(markdown_content)
            markdown_content = self._preprocess_textfield(markdown_content)
            markdown_content = self._preprocess_reactions(markdown_content)
            markdown_content = self._preprocess_session_join(markdown_content)
            markdown_content = self._preprocess_group_assignment(markdown_content)
            markdown_content = self._preprocess_spacer(markdown_content)
            markdown_content = self._preprocess_layout(markdown_content)

            # Markdownパーサーにカスタムコンポーネントをブロックレベル要素として認識させる
            if isinstance(markdown.util.BLOCK_LEVEL_ELEMENTS, list) and "situ-layout" not in markdown.util.BLOCK_LEVEL_ELEMENTS:
                markdown.util.BLOCK_LEVEL_ELEMENTS.append("situ-layout")
            elif hasattr(markdown.util.BLOCK_LEVEL_ELEMENTS, "add"):
                markdown.util.BLOCK_LEVEL_ELEMENTS.add("situ-layout")

            html = markdown.markdown(markdown_content, extensions=MARKDOWN_EXTENSIONS)
            self.logger.debug("Markdown → HTML 変換完了")
            return html
        except Exception as e:
            raise ConversionError(f"Markdown変換エラー: {e}") from e
