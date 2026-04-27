import re
from src.processors.base_parser import BaseComponentParser
import html

class Parser(BaseComponentParser):
    # OPTIONS: image, mode, bg-color, text-color, height, width
    # Match @[section: title](key: value, ...) or @[section](key: value, ...)
    START_PATTERN = r"@\[section(?:(?:\:\s*)?([^\]]*))\](?:\(((?:[^()]*|\([^()]*\))*)\))?"
    END_PATTERN = r"@\[/section\]"

    @property
    def block_level_tags(self) -> list[str]:
        return ["mono-section"]

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

            if 'height' in args:
                height_val = args['height'].strip("'\"")
                attrs.append(f'height="{html.escape(height_val)}"')

            if 'width' in args:
                width_val = args['width'].strip("'\"")
                attrs.append(f'width="{html.escape(width_val)}"')

            attrs_str = " ".join(attrs)

            result = f'<mono-section {attrs_str}{self.get_common_attributes(args)}>'

            if title and title.strip():
                safe_title = html.escape(title.strip())
                result += f'\n<h2>{safe_title}</h2>\n'

            return result

        result = pattern.sub(start_replacer, markdown_content)

        # end tag
        end_pattern = re.compile(self.END_PATTERN)
        result = end_pattern.sub('</mono-section>', result)

        return result
