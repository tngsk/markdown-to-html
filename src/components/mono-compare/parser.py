import re
from src.processors.base_parser import BaseComponentParser

class Parser(BaseComponentParser):
    PATTERN = r"(?s)@\[compare(?:(?:\:\s*)?([^\]]*))\](?:\(((?:[^()]*|\([^()]*\))*)\))?(?:\s*\{([^}]*)\})?((?:(?!@\[compare).)*?)@\[(?:end|/(?:compare))\]"
    FAST_PATH_MARKERS = ("@[compare",)

    @property
    def block_level_tags(self) -> list[str]:
        return ["mono-compare"]

    def process(self, markdown_content: str) -> str:
        if "@[compare" not in markdown_content:
            return markdown_content

        pattern = re.compile(self.PATTERN, re.IGNORECASE)

        def replacer(match: re.Match) -> str:
            bracket_content = match.group(1) or ""
            args_str = match.group(2) or ""
            trailing_str = match.group(3) or ""
            inner_content = match.group(4) or ""

            label, specific_args = self.parse_bracket_content(bracket_content)
            common_args = self.parse_key_value_args(args_str)
            args = {**specific_args, **common_args}
            args = self.merge_trailing_attrs(args, trailing_str)

            # Split inner content by `:::` or `:::column` or `:::item`
            parts = re.split(r'\n?\s*:::(?:column|item)?\s*\n?', inner_content)
            valid_parts = [p.strip() for p in parts if p.strip()]

            # Determine mode: explicit argument > child count detection (3 -> 3, otherwise 2)
            explicit_mode = args.get('mode')
            if explicit_mode in ('2', '3'):
                mode = explicit_mode
            else:
                mode = '3' if len(valid_parts) == 3 else '2'

            items = []
            for p in valid_parts:
                items.append(f'<div class="compare-item" markdown="1">\n{p}\n</div>')

            inner_html = "\n".join(items)

            # Clean mode from args so it's not redundantly added to common attributes
            args_for_common = {k: v for k, v in args.items() if k != 'mode'}
            common_attrs = self.get_common_attributes(args_for_common)

            return f'<mono-compare mode="{mode}"{common_attrs} markdown="1">\n{inner_html}\n</mono-compare>'

        return pattern.sub(replacer, markdown_content)
