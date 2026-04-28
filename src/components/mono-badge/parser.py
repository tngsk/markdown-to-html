import re
from src.processors.base_parser import BaseComponentParser

class Parser(BaseComponentParser):
    # OPTIONS: text, color, soft, outline
    PATTERN = r"@\[badge(?:(?:\:\s*)?([^\]]*))\](?:\(((?:[^()]*|\([^()]*\))*)\))?"
    TEMPLATE = '<mono-badge{color_attr}{soft_attr}{outline_attr}{common_attr}>{text}</mono-badge>'

    def process(self, markdown_content: str) -> str:
        pattern = re.compile(self.PATTERN)

        def replacer(match: re.Match) -> str:
            bracket_content = match.group(1)

            args_str = match.group(2)

            text, specific_args = self.parse_bracket_content(bracket_content)

            common_args = self.parse_key_value_args(args_str)

            args = {**specific_args, **common_args}

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
                outline_attr=outline_attr,
            common_attr=self.get_common_attributes(args)
            )

        return pattern.sub(replacer, markdown_content)
