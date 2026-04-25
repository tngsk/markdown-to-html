import re
from src.processors.base_parser import BaseComponentParser

class Parser(BaseComponentParser):
    # Pattern to match @[theme: THEME_NAME]()
    PATTERN = r"@\[theme:\s*([^\]]+)\](?:\(((?:[^()]*|\([^()]*\))*)\))?"

    def process(self, markdown_content: str) -> str:
        pattern = re.compile(self.PATTERN)
        def replacer(match: re.Match) -> str:
            theme_name = match.group(1).strip()

            # The args inside () are optional for now, but could be used to toggle UI in the future
            args_str = match.group(2)
            args = self.parse_key_value_args(args_str) if args_str else {}

            show_ui = args.get('show_ui', 'false').lower() == 'true'
            config_file = args.get('config', '')

            safe_theme = self.escape_html(theme_name)
            safe_show_ui = "true" if show_ui else "false"
            safe_config = self.escape_html(config_file)

            return f'<mono-theme theme="{safe_theme}" show-ui="{safe_show_ui}" config="{safe_config}"{self.get_common_attributes(args)}></mono-theme>'

        return pattern.sub(replacer, markdown_content)
