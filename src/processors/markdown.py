"""
Markdown Processor
==================
Converts Markdown content to intermediate HTML.
"""

import importlib
import logging
import re
import sys

import markdown
import markdown.util

from src.config import ConversionError
from src.constants import (
    MARKDOWN_EXTENSIONS,
    ALLOWED_COMPONENTS,
)
from src.handlers.file import FileHandler


class MarkdownProcessor:
    """Markdownから中間HTMLへの変換処理"""

    def __init__(self, logger: logging.Logger, file_handler: FileHandler):
        self.logger = logger
        self.file_handler = file_handler
        self.parsers = self._load_component_parsers()

    def _load_component_parsers(self):
        """
        明示的に許可されたコンポーネントのみをインポートしてインスタンス化し、リストで返す
        """
        parsers = []

        for component_name in ALLOWED_COMPONENTS:
            module_name = f"src.components.{component_name}.parser"
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, "Parser"):
                    parser_instance = module.Parser()
                    parsers.append(parser_instance)
                    self.logger.debug(
                        f"パーサーをロードしました: {component_name}"
                    )
            except Exception as e:
                self.logger.warning(
                    f"パーサーのロードに失敗しました ({component_name}): {e}"
                )

        return parsers

    def _protect_code_blocks(self, markdown_content: str) -> tuple[str, dict[str, str]]:
        """
        コードブロック（フェンスおよびインライン）を保護するための一時的なプレースホルダーに置換する。
        """
        blocks = {}
        counter = 0

        def replace_fenced(match: re.Match) -> str:
            nonlocal counter
            placeholder = f"@@FENCED_CODE_BLOCK_{counter}@@"
            blocks[placeholder] = match.group(0)
            counter += 1
            return placeholder

        # 複数行のコードブロックを保護 (``` または ~~~)
        fenced_pattern = re.compile(r'(?s)(^[ \t]*(`{3,}|~{3,}).*?\n[ \t]*\2[ \t]*(?=\n|$))', re.MULTILINE)
        processed = fenced_pattern.sub(replace_fenced, markdown_content)

        def replace_inline(match: re.Match) -> str:
            nonlocal counter
            placeholder = f"@@INLINE_CODE_BLOCK_{counter}@@"
            blocks[placeholder] = match.group(0)
            counter += 1
            return placeholder

        # インラインのコードブロックを保護
        inline_pattern = re.compile(r'(`+)(.*?)\1')
        processed = inline_pattern.sub(replace_inline, processed)

        return processed, blocks

    def _restore_code_blocks(self, processed_content: str, blocks: dict[str, str]) -> str:
        """
        保護されたプレースホルダーを元のコードブロックに戻す。

        Note:
            Performance optimization: Uses a single regex pass instead of O(M*N) sequential string replacements,
            significantly improving render times for documents with many code blocks.
        """
        if not blocks:
            return processed_content

        pattern = re.compile(r'@@(?:FENCED|INLINE)_CODE_BLOCK_\d+@@')

        def replacer(match: re.Match) -> str:
            return blocks.get(match.group(0), match.group(0))

        return pattern.sub(replacer, processed_content)

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
            # コンポーネントパース前にコードブロックを保護
            protected_content, blocks = self._protect_code_blocks(markdown_content)

            for parser in self.parsers:
                try:
                    protected_content = parser.process(protected_content)
                except Exception as e:
                    self.logger.warning(f"コンポーネントパース処理でエラー: {e}")

            # コードブロックを復元
            markdown_content = self._restore_code_blocks(protected_content, blocks)

            # Markdownパーサーにカスタムコンポーネントをブロックレベル要素として認識させる
            tags_to_add = []
            for parser in self.parsers:
                if hasattr(parser, 'block_level_tags'):
                    tags_to_add.extend(parser.block_level_tags)

            if tags_to_add:
                block_level = markdown.util.BLOCK_LEVEL_ELEMENTS
                if isinstance(block_level, list):
                    for tag in tags_to_add:
                        if tag not in block_level:
                            block_level.append(tag)
                elif isinstance(block_level, set):
                    for tag in tags_to_add:
                        block_level.add(tag)
                else:
                    add_fn = getattr(block_level, "add", None)
                    if callable(add_fn):
                        for tag in tags_to_add:
                            add_fn(tag)

            html = markdown.markdown(markdown_content, extensions=MARKDOWN_EXTENSIONS)
            self.logger.debug("Markdown → HTML 変換完了")
            return html
        except Exception as e:
            raise ConversionError(f"Markdown変換エラー: {e}") from e
