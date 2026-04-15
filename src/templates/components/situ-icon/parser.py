import re
from src.processors.base_parser import BaseComponentParser

class Parser(BaseComponentParser):
    PATTERN = r"@\[icon:\s*([^\]]+)\](?:\(((?:[^()]*|\([^()]*\))*)\))?"
    TEMPLATE = '<situ-icon name="{name}"{size_attr}{color_attr}{display_attr}></situ-icon>'

    def process(self, markdown_content: str) -> str:
        pattern = re.compile(self.PATTERN)

        def replacer(match: re.Match) -> str:
            name = match.group(1).strip()
            # Strip surrounding quotes if present
            if (name.startswith('"') and name.endswith('"')) or (name.startswith("'") and name.endswith("'")):
                name = name[1:-1].strip()

            args_str = match.group(2)

            size_attr = ""
            color_attr = ""
            display_attr = ""

            if args_str:
                # Need to handle commas inside parentheses, like rgba(255, 0, 0, 0.5)
                # A simple split(',') won't work perfectly.
                # Let's use a regex to split by commas that are outside parentheses
                # Since we know the prefixes, we can extract them directly

                size_match = re.search(r'size:\s*([^,]+)(?:,|$)', args_str)
                if size_match:
                    size_val = size_match.group(1).strip()
                    size_attr = f' size="{self.escape_html(size_val)}"'

                color_match = re.search(r'color:\s*((?:rgba\([^)]+\)|[^,]+))(?:,|$)', args_str)
                if color_match:
                    color_val = color_match.group(1).strip()
                    color_attr = f' color="{self.escape_html(color_val)}"'

                display_match = re.search(r'display:\s*([^,]+)(?:,|$)', args_str)
                if display_match:
                    display_val = display_match.group(1).strip()
                    display_attr = f' display="{self.escape_html(display_val)}"'

            safe_name = self.escape_html(name)

            return self.TEMPLATE.format(
                name=safe_name,
                size_attr=size_attr,
                color_attr=color_attr,
                display_attr=display_attr
            )

        return pattern.sub(replacer, markdown_content)
