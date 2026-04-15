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
    MARKDOWN_EXTENSIONS,
    TEMPLATES_DIR,
)
from src.handlers.file import FileHandler
import markdown.util
import importlib.util
import sys
from pathlib import Path


class MarkdownProcessor:
    """Markdownから中間HTMLへの変換処理"""

    def __init__(self, logger: logging.Logger, file_handler: FileHandler):
        self.logger = logger
        self.file_handler = file_handler
        self.parsers = self._load_component_parsers()

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
        src/templates/components/ 配下の各コンポーネントディレクトリにある
        parser.py を動的に読み込み、インスタンス化してリストで返す
        """
        parsers = []
        components_dir = TEMPLATES_DIR / "components"
        if not components_dir.exists() or not components_dir.is_dir():
            self.logger.warning(f"コンポーネントディレクトリが見つかりません: {components_dir}")
            return parsers

        for component_dir in sorted(components_dir.iterdir()):
            if not component_dir.is_dir():
                continue

            parser_file = component_dir / "parser.py"
            if parser_file.exists():
                try:
                    module_name = f"src.templates.components.{component_dir.name}.parser"
                    spec = importlib.util.spec_from_file_location(module_name, parser_file)
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)

                    if hasattr(module, "Parser"):
                        parser_instance = module.Parser()
                        parsers.append(parser_instance)
                        self.logger.debug(f"パーサーをロードしました: {component_dir.name}")
                except Exception as e:
                    self.logger.warning(f"パーサーのロードに失敗しました ({parser_file}): {e}")

        return parsers

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
            for parser in self.parsers:
                try:
                    markdown_content = parser.process(markdown_content)
                except Exception as e:
                    self.logger.warning(f"コンポーネントパース処理でエラー: {e}")

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
