import re
from src.processors.base_parser import BaseComponentParser

class Parser(BaseComponentParser):
    # OPTIONS: text, color, soft, outline
    PATTERN = r"@\[badge(?:\:\s*([^\]]+))?\](?:\(((?:[^()]*|\([^()]*\))*)\))?"
    TEMPLATE = '<mono-badge{color_attr}{soft_attr}{outline_attr}>{text}</mono-badge>'

    def process(self, markdown_content: str) -> str:
        pattern = re.compile(self.PATTERN)

        def replacer(match: re.Match) -> str:
            text = match.group(1)
            if text:
                text = text.strip()
                if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
                    text = text[1:-1].strip()

            args_str = match.group(2)
            args = self.parse_key_value_args(args_str)

            if 'text' in args:
                text = args['text']

            color_attr = ""
            soft_attr = ""
            outline_attr = ""

            if 'color' in args:
                color_attr = f' color="{self.escape_html(args["color"])}"'
            if 'soft' in args and args['soft'].lower() in ['true', '1', 'yes']:
                soft_attr = f' soft=""'
            if 'outline' in args and args['outline'].lower() in ['true', '1', 'yes']:
                outline_attr = f' outline=""'

            safe_text = self.escape_html(text) if text else ""

            return self.TEMPLATE.format(
                text=safe_text,
                color_attr=color_attr,
                soft_attr=soft_attr,
                outline_attr=outline_attr
            )

        return pattern.sub(replacer, markdown_content)
