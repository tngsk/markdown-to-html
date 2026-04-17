import re
from src.processors.base_parser import BaseComponentParser

class Parser(BaseComponentParser):
    # Pattern: @[flipcard: "Front Text"](args)
    # The first group matches the text after the colon.
    # The second group matches the arguments inside parentheses.
    PATTERN = r"@\[flipcard(?:\:\s*([^\]]+))?\](?:\(((?:[^()]*|\([^()]*\))*)\))?"

    def process(self, markdown_content: str) -> str:
        pattern = re.compile(self.PATTERN)

        def replacer(match: re.Match) -> str:
            # Front text is passed in the main label part.
            # Handle possible quotes.
            front_text = match.group(1) or ""
            front_text = front_text.strip()
            if (front_text.startswith('"') and front_text.endswith('"')) or \
               (front_text.startswith("'") and front_text.endswith("'")):
                front_text = front_text[1:-1]

            args_str = match.group(2)
            args = self.parse_key_value_args(args_str)

            # Accept 'a', 'A', 'ans', 'answer' as keys for the back text
            back_text = ""
            for key in ['a', 'A', 'ans', 'answer']:
                if key in args:
                    back_text = args[key]
                    break

            safe_front = self.escape_html(front_text)
            safe_back = self.escape_html(back_text)

            return f'<mono-flipcard front="{safe_front}" back="{safe_back}"></mono-flipcard>'

        return pattern.sub(replacer, markdown_content)
