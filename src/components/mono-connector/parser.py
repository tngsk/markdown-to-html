import re
from src.processors.base_parser import BaseComponentParser


class Parser(BaseComponentParser):
    PATTERN = r"@\[(connector|connect)(?:(?:\:\s*)?([^\]]*))\](?:\(((?:[^()]*|\([^()]*\))*)\))?(?:\s*\{([^}]*)\})?"
    FAST_PATH_MARKERS = ("@[connector", "@[connect")

    @property
    def block_level_tags(self) -> list[str]:
        return ["mono-connector"]

    def process(self, markdown_content: str) -> str:
        if not any(marker in markdown_content for marker in self.FAST_PATH_MARKERS):
            return markdown_content

        pattern = re.compile(self.PATTERN, re.IGNORECASE)

        def replacer(match: re.Match) -> str:
            bracket_content = (match.group(2) or "").strip()
            args_str = match.group(3) or ""
            trailing_str = match.group(4) or ""

            common_args = self.parse_key_value_args(args_str) if args_str else {}
            args = self.merge_trailing_attrs(common_args, trailing_str)

            # 矢印記法 (#a -> #b または #a -> #b | label) の解析
            if "->" in bracket_content:
                parts = bracket_content.split("|", 1)
                arrow_part = parts[0].strip()
                label_part = parts[1].strip() if len(parts) > 1 else None

                arrow_match = re.match(r"^([\S]+)\s*->\s*([\S]+)$", arrow_part)
                if arrow_match:
                    if "from" not in args:
                        args["from"] = arrow_match.group(1)
                    if "to" not in args:
                        args["to"] = arrow_match.group(2)

                if label_part and "label" not in args:
                    args["label"] = label_part
            elif bracket_content:
                label, specific_args = self.parse_bracket_content(bracket_content)
                args = {**specific_args, **args}
                if label and "label" not in args:
                    args["label"] = label

            attrs = []
            for k, v in args.items():
                if v is not None:
                    attrs.append(f'{k}="{self.escape_html(str(v))}"')

            attr_str = (" " + " ".join(attrs)) if attrs else ""
            return f"<mono-connector{attr_str}></mono-connector>"

        return pattern.sub(replacer, markdown_content)
