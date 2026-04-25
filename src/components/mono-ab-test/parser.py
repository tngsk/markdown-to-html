import re
from src.processors.base_parser import BaseComponentParser

class Parser(BaseComponentParser):
    PATTERN = r"@\[ab-test(?:\:\s*([^\]]+))?\](?:\(((?:[^()]*|\([^()]*\))*)\))?"

    def process(self, markdown_content: str) -> str:
        pattern = re.compile(self.PATTERN)
        def replacer(match: re.Match) -> str:
            title = match.group(1)
            args_str = match.group(2)
            args = self.parse_key_value_args(args_str)

            src_a = args.get('src-a', '')
            if not src_a:
                src_a = args.get('src_a', '')
            src_b = args.get('src-b', '')
            if not src_b:
                src_b = args.get('src_b', '')

            safe_title = self.escape_html(title) if title else ""
            safe_src_a = self.escape_html(src_a)
            safe_src_b = self.escape_html(src_b)
            component_id = self.get_next_id("abtest")
            return f'<mono-ab-test id="{component_id}" title="{safe_title}" src-a="{safe_src_a}" src-b="{safe_src_b}"{self.get_common_attributes(args)}></mono-ab-test>'
        return pattern.sub(replacer, markdown_content)
