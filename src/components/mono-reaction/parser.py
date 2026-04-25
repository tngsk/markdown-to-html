import re
from src.processors.base_parser import BaseComponentParser

class Parser(BaseComponentParser):
    # OPTIONS: options
    PATTERN = r"@\[reaction(?:\:\s*([^\]]+))?\](?:\(((?:[^()]*|\([^()]*\))*)\))?"

    def process(self, markdown_content: str) -> str:
        pattern = re.compile(self.PATTERN)
        def replacer(match: re.Match) -> str:
            label = match.group(1)
            args_str = match.group(2)
            args = self.parse_key_value_args(args_str)

            options = args.get('options', '')
            # Backward compatibility or shorthand if label provided but no options
            if label and not options and not args_str:
                if (label.startswith('"') and label.endswith('"')) or (label.startswith("'") and label.endswith("'")):
                    label = label[1:-1]
                options = label

            safe_options = self.escape_html(options)
            component_id = self.get_next_id("reaction")
            return f'<mono-reaction id="{component_id}" options="{safe_options}"{self.get_common_attributes(args)}></mono-reaction>'
        return pattern.sub(replacer, markdown_content)
