import re
from src.processors.base_parser import BaseComponentParser

class Parser(BaseComponentParser):
    PATTERN = r"@\[score(?:\:\s*([^\]]+))?\](?:\(((?:[^()]*|\([^()]*\))*)\))?"
    TEMPLATE = '<mono-score{notes_attr}{clef_attr}{time_signature_attr}{common_attr}></mono-score>'

    def process(self, markdown_content: str) -> str:
        pattern = re.compile(self.PATTERN)

        def replacer(match: re.Match) -> str:
            notes = match.group(1)
            if notes:
                notes = notes.strip()
                if (notes.startswith('"') and notes.endswith('"')) or (notes.startswith("'") and notes.endswith("'")):
                    notes = notes[1:-1].strip()

            args_str = match.group(2)
            args = {}
            if args_str:
                args = self.parse_key_value_args(args_str)

            if 'notes' in args:
                notes = args['notes']

            notes_attr = f' notes="{self.escape_html(notes)}"' if notes else ""

            clef_attr = ""
            if 'clef' in args:
                clef_attr = f' clef="{self.escape_html(args["clef"])}"'

            time_signature_attr = ""
            if 'time' in args:
                time_signature_attr = f' time="{self.escape_html(args["time"])}"'

            return self.TEMPLATE.format(
                notes_attr=notes_attr,
                clef_attr=clef_attr,
                time_signature_attr=time_signature_attr
            , common_attr=self.get_common_attributes(args))

        return pattern.sub(replacer, markdown_content)
