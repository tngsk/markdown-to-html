import re
from src.processors.base_parser import BaseComponentParser

class Parser(BaseComponentParser):
    PATTERN = r"@\[countdown\](?:\(((?:[^()]*|\([^()]*\))*)\))?"
    TEMPLATE = '<mono-countdown{time_attr}{color_attr}></mono-countdown>'

    def process(self, markdown_content: str) -> str:
        pattern = re.compile(self.PATTERN)

        def replacer(match: re.Match) -> str:
            args_str = match.group(1)
            args = self.parse_key_value_args(args_str) if args_str else {}

            time_attr = ""
            color_attr = ""

            if 'time' in args:
                time_attr = f' time="{self.escape_html(args["time"])}"'
            if 'color' in args:
                color_attr = f' color="{self.escape_html(args["color"])}"'

            return self.TEMPLATE.format(
                time_attr=time_attr,
                color_attr=color_attr
            )

        return pattern.sub(replacer, markdown_content)
