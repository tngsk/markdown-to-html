import re
from src.processors.base_parser import BaseComponentParser

class Parser(BaseComponentParser):
    PATTERN = r"@\[icon(?:\:\s*([^\]]+))?\](?:\(((?:[^()]*|\([^()]*\))*)\))?"
    TEMPLATE = '<mono-icon name="{name}"{size_attr}{color_attr}{display_attr}></mono-icon>'

    def process(self, markdown_content: str) -> str:
        pattern = re.compile(self.PATTERN)

        def replacer(match: re.Match) -> str:
            name = match.group(1)
            if name:
                name = name.strip()
                if (name.startswith('"') and name.endswith('"')) or (name.startswith("'") and name.endswith("'")):
                    name = name[1:-1].strip()

            args_str = match.group(2)
            args = self.parse_key_value_args(args_str)

            if 'name' in args:
                name = args['name']

            size_attr = ""
            color_attr = ""
            display_attr = ""

            if 'size' in args:
                size_attr = f' size="{self.escape_html(args["size"])}"'
            if 'color' in args:
                color_attr = f' color="{self.escape_html(args["color"])}"'
            if 'display' in args:
                display_attr = f' display="{self.escape_html(args["display"])}"'

            safe_name = self.escape_html(name) if name else ""

            return self.TEMPLATE.format(
                name=safe_name,
                size_attr=size_attr,
                color_attr=color_attr,
                display_attr=display_attr
            )

        return pattern.sub(replacer, markdown_content)
