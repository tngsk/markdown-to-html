import re
from src.processors.base_parser import BaseComponentParser

class Parser(BaseComponentParser):
    ROW_PATTERN = r"@\[row(?:\:\s*([^\]]+))?\](?:\(((?:[^()]*|\([^()]*\))*)\))?"
    STACK_PATTERN = r"@\[stack(?:\:\s*([^\]]+))?\](?:\(((?:[^()]*|\([^()]*\))*)\))?"
    END_PATTERN = r"@\[end\]"
    COLUMN_START_PATTERN = r":::column"
    COLUMN_END_PATTERN = r":::(?!\S)"

    def process(self, markdown_content: str) -> str:
        # row
        pattern = re.compile(self.ROW_PATTERN)
        def row_replacer(match: re.Match) -> str:
            label = match.group(1)
            args_str = match.group(2)
            args = self.parse_key_value_args(args_str)

            classes = label.strip() if label else ""
            if 'class' in args:
                classes = args['class']

            if classes:
                return f'<mono-layout type="row" class="{classes}" markdown="1">'
            return '<mono-layout type="row" markdown="1">'
        result = pattern.sub(row_replacer, markdown_content)

        # stack
        pattern = re.compile(self.STACK_PATTERN)
        def stack_replacer(match: re.Match) -> str:
            label = match.group(1)
            args_str = match.group(2)
            args = self.parse_key_value_args(args_str)

            classes = label.strip() if label else ""
            if 'class' in args:
                classes = args['class']

            if classes:
                return f'<mono-layout type="stack" class="{classes}" markdown="1">'
            return '<mono-layout type="stack" markdown="1">'
        result = pattern.sub(stack_replacer, result)

        # end
        pattern = re.compile(self.END_PATTERN)
        result = pattern.sub('</mono-layout>', result)

        # column start
        pattern = re.compile(self.COLUMN_START_PATTERN)
        result = pattern.sub('<div class="column" markdown="1">', result)

        # column end
        pattern = re.compile(self.COLUMN_END_PATTERN)
        result = pattern.sub('</div>', result)

        return result
