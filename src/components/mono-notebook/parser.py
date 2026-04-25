import re
from src.processors.base_parser import BaseComponentParser

class Parser(BaseComponentParser):
    # OPTIONS: id, placeholder, title
    PATTERN = r"@\[(?:notebook|notebook-input)(?:\:\s*([^\]]+))?\](?:\(((?:[^()]*|\([^()]*\))*)\))?"

    def process(self, markdown_content: str) -> str:
        pattern = re.compile(self.PATTERN)

        def replacer(match: re.Match) -> str:
            title = match.group(1)
            args_str = match.group(2)
            args = self.parse_key_value_args(args_str)

            input_id = args.get('id', '')
            placeholder = args.get('placeholder', '')
            if 'title' in args:
                title = args['title']

            safe_id = self.escape_html(input_id)
            attrs = [f'id="{safe_id}"'] if safe_id else []

            if title:
                safe_title = self.escape_html(title.strip())
                attrs.append(f'title="{safe_title}"')

            if placeholder:
                safe_placeholder = self.escape_html(placeholder.strip())
                attrs.append(f'placeholder="{safe_placeholder}"')

            attrs_str = " ".join(attrs)
            return f'<mono-notebook {attrs_str}{self.get_common_attributes(args)}></mono-notebook>'

        return pattern.sub(replacer, markdown_content)
