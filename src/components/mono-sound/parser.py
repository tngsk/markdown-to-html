import re
from src.processors.base_parser import BaseComponentParser

class Parser(BaseComponentParser):
    # OPTIONS: src, label
    PATTERN = r"@\[sound(?:\:\s*([^\]]+))?\](?:\(((?:[^()]*|\([^()]*\))*)\))?"

    def process(self, markdown_content: str) -> str:
        pattern = re.compile(self.PATTERN)
        def replacer(match: re.Match) -> str:
            label = match.group(1)
            args_str = match.group(2)
            args = self.parse_key_value_args(args_str)

            src = args.get('src', '')
            if 'label' in args:
                label = args['label']

            safe_label = self.escape_html(label) if label else ""
            safe_src = self.escape_html(src)
            component_id = self.get_next_id("sound")
            return f'<mono-sound id="{component_id}" label="{safe_label}" src="{safe_src}"{self.get_common_attributes(args)}></mono-sound>'
        return pattern.sub(replacer, markdown_content)
