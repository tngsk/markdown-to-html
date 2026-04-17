import re
from src.processors.base_parser import BaseComponentParser

class Parser(BaseComponentParser):
    PATTERN = r"@\[dice\](?:\(((?:[^()]*|\([^()]*\))*)\))?"

    @property
    def block_level_tags(self) -> list[str]:
        return ["mono-dice"]

    def process(self, markdown_content: str) -> str:
        pattern = re.compile(self.PATTERN)

        def replacer(match: re.Match) -> str:
            args_str = match.group(1)
            args = self.parse_key_value_args(args_str)

            # Support both `faces` and `number`
            faces = args.get('number') or args.get('faces')

            attributes = []
            if faces:
                attributes.append(f'faces="{self.escape_html(faces)}"')

            attr_str = " " + " ".join(attributes) if attributes else ""
            return f'<mono-dice{attr_str}></mono-dice>'

        return pattern.sub(replacer, markdown_content)
