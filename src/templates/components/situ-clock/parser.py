import re
from src.processors.base_parser import BaseComponentParser

class Parser(BaseComponentParser):
    PATTERN = r"@\[clock\](?:\(((?:[^()]*|\([^()]*\))*)\))?"
    TEMPLATE = '<situ-clock{format_attr}{display_attr}></situ-clock>'

    def process(self, markdown_content: str) -> str:
        pattern = re.compile(self.PATTERN)

        def replacer(match: re.Match) -> str:
            args_str = match.group(1)

            format_attr = ""
            display_attr = ""

            if args_str:
                format_match = re.search(r'format:\s*([^,]+)(?:,|$)', args_str)
                if format_match:
                    # Remove potential surrounding quotes from format
                    format_val = format_match.group(1).strip()
                    if (format_val.startswith('"') and format_val.endswith('"')) or (format_val.startswith("'") and format_val.endswith("'")):
                        format_val = format_val[1:-1]
                    format_attr = f' format="{self.escape_html(format_val)}"'

                display_match = re.search(r'display:\s*([^,]+)(?:,|$)', args_str)
                if display_match:
                    display_val = display_match.group(1).strip()
                    display_attr = f' display="{self.escape_html(display_val)}"'

            return self.TEMPLATE.format(
                format_attr=format_attr,
                display_attr=display_attr
            )

        return pattern.sub(replacer, markdown_content)
