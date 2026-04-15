"""
Markdown Processor
==================
Converts Markdown content to intermediate HTML.
"""

import html
import importlib.util
import logging
import re
import sys

import markdown
import markdown.util

from src.config import ConversionError
from src.constants import (
    HTML_ICON_COMPONENT_TEMPLATE,
    HTML_SOUND_COMPONENT_TEMPLATE,
    MARKDOWN_EXTENSIONS,
    MARKDOWN_ICON_PATTERN,
    MARKDOWN_SOUND_PATTERN,
    TEMPLATES_DIR,
)
from src.handlers.file import FileHandler


class MarkdownProcessor:
    """Markdownから中間HTMLへの変換処理"""

    def __init__(self, logger: logging.Logger, file_handler: FileHandler):
        self.logger = logger
        self.file_handler = file_handler
        self.parsers = self._load_component_parsers()

    def _preprocess_icon(self, markdown_content: str) -> str:
        """
        @[icon: name](size, color, display) を <mono-icon> に変換する
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
                    if char == "(":
                        depth += 1
                        current += char
                    elif char == ")":
                        depth -= 1
                        current += char
                    elif char == "," and depth == 0:
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
                display_attr=display_attr,
            )

        result = pattern.sub(replacer, markdown_content)
        if markdown_content != result:
            self.logger.debug("アイコンコンポーネント前処理完了: @[icon] → <mono-icon>")
        return result

    def _load_component_parsers(self):
        """
        src/templates/components/ 配下の各コンポーネントディレクトリにある
        parser.py を動的に読み込み、インスタンス化してリストで返す
        """
        parsers = []
        components_dir = TEMPLATES_DIR / "components"
        if not components_dir.exists() or not components_dir.is_dir():
            self.logger.warning(
                f"コンポーネントディレクトリが見つかりません: {components_dir}"
            )
            return parsers

        for component_dir in sorted(components_dir.iterdir()):
            if not component_dir.is_dir():
                continue

            parser_file = component_dir / "parser.py"
            if parser_file.exists():
                try:
                    module_name = (
                        f"src.templates.components.{component_dir.name}.parser"
                    )
                    spec = importlib.util.spec_from_file_location(
                        module_name, parser_file
                    )
                    if spec is None or spec.loader is None:
                        self.logger.warning(
                            f"パーサーモジュールのロードに失敗しました（spec不在）: {parser_file}"
                        )
                        continue
                    module = importlib.util.module_from_spec(spec)
                    if module is None:
                        self.logger.warning(
                            f"module_from_spec が None を返しました: {parser_file}"
                        )
                        continue
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)

                    if hasattr(module, "Parser"):
                        parser_instance = module.Parser()
                        parsers.append(parser_instance)
                        self.logger.debug(
                            f"パーサーをロードしました: {component_dir.name}"
                        )
                except Exception as e:
                    self.logger.warning(
                        f"パーサーのロードに失敗しました ({parser_file}): {e}"
                    )

        return parsers

    def _preprocess_sound(self, markdown_content: str) -> str:
        """
        @[sound: ラベル](file) または @[sound](file) を <mono-sound> に変換する
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
            self.logger.debug("効果音コンポーネント前処理完了: @[sound] → <mono-sound>")
        return result

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
        """
        for placeholder, original in blocks.items():
            processed_content = processed_content.replace(placeholder, original)
        return processed_content

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
            block_level = markdown.util.BLOCK_LEVEL_ELEMENTS
            if isinstance(block_level, list):
                if "mono-layout" not in block_level:
                    block_level.append("mono-layout")
            elif isinstance(block_level, set):
                block_level.add("mono-layout")
            else:
                add_fn = getattr(block_level, "add", None)
                if callable(add_fn):
                    add_fn("mono-layout")

            html = markdown.markdown(markdown_content, extensions=MARKDOWN_EXTENSIONS)
            self.logger.debug("Markdown → HTML 変換完了")
            return html
        except Exception as e:
            raise ConversionError(f"Markdown変換エラー: {e}") from e
