import re
from src.processors.base_parser import BaseComponentParser

class Parser(BaseComponentParser):
    # Fixed to allow nested brackets if needed, but standard is just stop at ']'
    # Actually standard pattern in base_parser is usually r"@\[type(?:\:\s*([^\]]+))?\](?:\(((?:[^()]*|\([^()]*\))*)\))?"
    # If the label has brackets, we might have issues, but let's stick to the standard for now.
    DRAWER_PATTERN = r"@\[drawer(?:\:\s*([^\]]+))?\](?:\(((?:[^()]*|\([^()]*\))*)\))?"
    END_PATTERN = r"@\[(?:end|/drawer)\]"

    @property
    def block_level_tags(self) -> list[str]:
        return ["mono-drawer"]

    def process(self, markdown_content: str) -> str:
        # drawer start
        pattern = re.compile(self.DRAWER_PATTERN)
        def drawer_replacer(match: re.Match) -> str:
            label_match = match.group(1)
            args_str = match.group(2)
            args = self.parse_key_value_args(args_str)

            label = label_match.strip() if label_match else ""
            if 'label' in args:
                label = args['label']

            # Strip outer quotes if they exist in label (e.g. "My Notes")
            if label.startswith('"') and label.endswith('"') and len(label) >= 2:
                label = label[1:-1]
            elif label.startswith("'") and label.endswith("'") and len(label) >= 2:
                label = label[1:-1]

            position = args.get('position', 'left')
            open_state = args.get('open', 'false')

            safe_label = self.escape_html(label)
            safe_position = self.escape_html(position)

            open_attr = ""
            if open_state.lower() == 'true':
                open_attr = ' open="true"'

            return f'<mono-drawer label="{safe_label}" position="{safe_position}"{open_attr} markdown="1"{self.get_common_attributes(args)}>'

        result = pattern.sub(drawer_replacer, markdown_content)

        # end
        end_pattern = re.compile(self.END_PATTERN)
        result = end_pattern.sub('</mono-drawer>', result)

        return result
