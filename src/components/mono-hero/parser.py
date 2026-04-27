import re
from src.processors.base_parser import BaseComponentParser
import html

class Parser(BaseComponentParser):
    # OPTIONS: image, mode, bg-color, text-color
    # Match @[hero: title](key: value, ...) or @[hero](key: value, ...)
    START_PATTERN = r"@\[hero(?:(?:\:\s*)?([^\]]*))\](?:\(((?:[^()]*|\([^()]*\))*)\))?"
    END_PATTERN = r"@\[/hero\]"

    @property
    def block_level_tags(self) -> list[str]:
        return ["mono-hero"]

    def process(self, markdown_content: str) -> str:
        # start tag
        pattern = re.compile(self.START_PATTERN)

        def start_replacer(match: re.Match) -> str:
            bracket_content = match.group(1)
            args_str = match.group(2)
            title, specific_args = self.parse_bracket_content(bracket_content)
            common_args = self.parse_key_value_args(args_str)
            args = {**specific_args, **common_args}

            attrs = ['markdown="1"']

            if 'image' in args:
                # Strip quotes if present
                img_val = args['image'].strip("'\"")
                attrs.append(f'image="{html.escape(img_val)}"')

            if 'mode' in args:
                mode_val = args['mode'].strip("'\"")
                attrs.append(f'mode="{html.escape(mode_val)}"')

            if 'bg-color' in args:
                bg_val = args['bg-color'].strip("'\"")
                attrs.append(f'bg-color="{html.escape(bg_val)}"')

            if 'text-color' in args:
                text_val = args['text-color'].strip("'\"")
                attrs.append(f'text-color="{html.escape(text_val)}"')

            attrs_str = " ".join(attrs)

            result = f'<mono-hero {attrs_str}{self.get_common_attributes(args)}>'

            # If a title was provided, inject it as an h1 inside the hero component
            if title and title.strip():
                safe_title = html.escape(title.strip())
                result += f'\n<h1>{safe_title}</h1>\n'

            return result

        result = pattern.sub(start_replacer, markdown_content)

        # end tag
        end_pattern = re.compile(self.END_PATTERN)
        result = end_pattern.sub('</mono-hero>', result)

        return result
