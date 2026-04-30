import html
import logging

logger = logging.getLogger("markdown_converter")


class BaseComponentParser:
    """コンポーネント用Markdownパーサーの基底クラス"""

    def __init__(self):
        self.counter = 0

    @property
    def block_level_tags(self) -> list[str]:
        """
        このパーサーが生成するブロックレベル要素のタグ名リストを返す。
        Markdown変換時に <p> タグで囲まれるのを防ぐために使用される。
        サブクラスで必要に応じてオーバーライドする。
        """
        return []

    def get_next_id(self, prefix: str) -> str:
        """ユニークなIDを生成して返す"""
        self.counter += 1
        return f"{prefix}-{self.counter}"

    @staticmethod
    def escape_html(text: str) -> str:
        """HTML特殊文字をエスケープする"""
        if text is None:
            return ""
        return html.escape(text.strip())

    @staticmethod
    def parse_bracket_content(content: str) -> tuple[str, dict]:
        """
        Parse the content inside `[]` which can be:
        - Label only: `"My Label"` or `My Label`
        - Label and args: `"My Label", id: "123"`
        - Args only: `id: "123"`
        Returns (label_str, args_dict)
        """
        if not content:
            return "", {}

        content = content.strip()

        has_paren = '(' in content
        has_quote = '"' in content or "'" in content

        parts = []

        # Fast path for simple cases without nested parens or quotes
        if not has_paren and not has_quote:
            parts = [p.strip() for p in content.split(',') if p.strip()]
        else:
            paren_depth = 0
            in_quote = None
            start_idx = 0

            if not has_paren:
                raw_parts = content.split(',')
                current_part = ""
                in_quote = None

                for p in raw_parts:
                    if current_part:
                        current_part += "," + p
                    else:
                        current_part = p

                    if not in_quote and "'" not in p:
                        if p.count('"') % 2 == 0:
                            parts.append(current_part.strip())
                            current_part = ""
                            continue
                    elif not in_quote and '"' not in p:
                        if p.count("'") % 2 == 0:
                            parts.append(current_part.strip())
                            current_part = ""
                            continue

                    search_start = 0
                    while True:
                        if in_quote:
                            idx = p.find(in_quote, search_start)
                            if idx == -1:
                                break
                            in_quote = None
                            search_start = idx + 1
                        else:
                            idx_q1 = p.find('"', search_start)
                            idx_q2 = p.find("'", search_start)

                            if idx_q1 == -1 and idx_q2 == -1:
                                break
                            elif idx_q1 != -1 and idx_q2 != -1:
                                m = idx_q1 if idx_q1 < idx_q2 else idx_q2
                            else:
                                m = idx_q1 if idx_q1 != -1 else idx_q2

                            in_quote = p[m]
                            search_start = m + 1

                    if not in_quote:
                        parts.append(current_part.strip())
                        current_part = ""

                start_idx = len(content)
                if current_part:
                    parts.append(current_part.strip())
            else:
                for i, char in enumerate(content):
                    if in_quote:
                        if char == in_quote:
                            in_quote = None
                    elif char in "\"'":
                        in_quote = char
                    elif char == '(':
                        paren_depth += 1
                    elif char == ')':
                        paren_depth -= 1
                    elif char == ',' and paren_depth == 0 and not in_quote:
                        parts.append(content[start_idx:i].strip())
                        start_idx = i + 1

            if start_idx < len(content):
                parts.append(content[start_idx:].strip())

        label = ""
        args_dict = {}

        if parts:
            first_part = parts[0]
            in_q = None
            has_kv_separator = False
            for char in first_part:
                if in_q:
                    if char == in_q:
                        in_q = None
                elif char in "\"'":
                    in_q = char
                elif char in (':', '='):
                    has_kv_separator = True
                    break

            if not has_kv_separator:
                label = first_part
                if len(label) >= 2 and label[0] == label[-1] and label[0] in "\"'":
                    label = label[1:-1]
                parts = parts[1:]

        for part in parts:
            if not part:
                continue
            idx_colon = part.find(':')
            idx_equal = part.find('=')

            if idx_colon != -1 and idx_equal != -1:
                split_idx = min(idx_colon, idx_equal)
            elif idx_colon != -1:
                split_idx = idx_colon
            elif idx_equal != -1:
                split_idx = idx_equal
            else:
                split_idx = -1

            if split_idx != -1:
                if split_idx == idx_equal:
                    logger.warning(
                        f"Deprecated syntax: Use ':' instead of '=' for component options. Found in: '{part}'"
                    )
                k = part[:split_idx].strip()
                v = part[split_idx+1:].strip()
                if len(v) >= 2 and v[0] == v[-1] and (v[0] == '"' or v[0] == "'"):
                    v = v[1:-1]
                args_dict[k] = v

        return label, args_dict

    @staticmethod
    def parse_key_value_args(args_str: str) -> dict:
        if not args_str:
            return {}
        result = {}

        has_paren = '(' in args_str
        has_quote = '"' in args_str or "'" in args_str

        # Fast path for simple cases without nested parens or quotes
        if not has_paren and not has_quote:
            for part in args_str.split(','):
                part = part.strip()
                if not part:
                    continue

                idx_colon = part.find(':')
                idx_equal = part.find('=')

                # Find the earliest occurrence
                if idx_colon != -1 and idx_equal != -1:
                    split_idx = min(idx_colon, idx_equal)
                elif idx_colon != -1:
                    split_idx = idx_colon
                elif idx_equal != -1:
                    split_idx = idx_equal
                else:
                    split_idx = -1

                if split_idx != -1:
                    if split_idx == idx_equal:
                        logger.warning(
                            f"Deprecated syntax: Use ':' instead of '=' for component options. Found in: '{part}'"
                        )
                    result[part[:split_idx].strip()] = part[split_idx+1:].strip()
            return result

        parts = []
        paren_depth = 0
        in_quote = None
        start_idx = 0

        if not has_paren:
            raw_parts = args_str.split(',')
            current_part = ""
            in_quote = None

            for p in raw_parts:
                if current_part:
                    current_part += "," + p
                else:
                    current_part = p

                if not in_quote and "'" not in p:
                    if p.count('"') % 2 == 0:
                        parts.append(current_part.strip())
                        current_part = ""
                        continue
                elif not in_quote and '"' not in p:
                    if p.count("'") % 2 == 0:
                        parts.append(current_part.strip())
                        current_part = ""
                        continue

                search_start = 0
                while True:
                    if in_quote:
                        idx = p.find(in_quote, search_start)
                        if idx == -1:
                            break
                        in_quote = None
                        search_start = idx + 1
                    else:
                        idx_q1 = p.find('"', search_start)
                        idx_q2 = p.find("'", search_start)

                        if idx_q1 == -1 and idx_q2 == -1:
                            break
                        elif idx_q1 != -1 and idx_q2 != -1:
                            m = idx_q1 if idx_q1 < idx_q2 else idx_q2
                        else:
                            m = idx_q1 if idx_q1 != -1 else idx_q2

                        in_quote = p[m]
                        search_start = m + 1

                if not in_quote:
                    parts.append(current_part.strip())
                    current_part = ""

            start_idx = len(args_str)
            if current_part:
                parts.append(current_part.strip())
        else:
            for i, char in enumerate(args_str):
                if in_quote:
                    if char == in_quote:
                        in_quote = None
                elif char in "\"'":
                    in_quote = char
                elif char == '(':
                    paren_depth += 1
                elif char == ')':
                    paren_depth -= 1
                elif char == ',' and paren_depth == 0 and not in_quote:
                    parts.append(args_str[start_idx:i].strip())
                    start_idx = i + 1

        if start_idx < len(args_str):
            parts.append(args_str[start_idx:].strip())

        for part in parts:
            if not part:
                continue

            idx_colon = part.find(':')
            idx_equal = part.find('=')

            # Find the earliest occurrence
            if idx_colon != -1 and idx_equal != -1:
                split_idx = min(idx_colon, idx_equal)
            elif idx_colon != -1:
                split_idx = idx_colon
            elif idx_equal != -1:
                split_idx = idx_equal
            else:
                split_idx = -1

            if split_idx != -1:
                if split_idx == idx_equal:
                    logger.warning(
                        f"Deprecated syntax: Use ':' instead of '=' for component options. Found in: '{part}'"
                    )
                k = part[:split_idx].strip()
                v = part[split_idx+1:].strip()
                if len(v) >= 2 and v[0] == v[-1] and (v[0] == '"' or v[0] == "'"):
                    v = v[1:-1]
                result[k] = v
        return result

    def get_common_attributes(self, args: dict) -> str:
        """
        全コンポーネント共通の属性（例: padding）を抽出し、HTML属性文字列として返す。
        """
        attrs = []
        if 'class' in args:
            attrs.append(f'class="{self.escape_html(args["class"])}"')
        if 'id' in args:
            attrs.append(f'id="{self.escape_html(args["id"])}"')
        if 'padding' in args:
            attrs.append(f'padding="{self.escape_html(args["padding"])}"')
        if 'padding-x' in args:
            attrs.append(f'padding-x="{self.escape_html(args["padding-x"])}"')
        if 'padding-y' in args:
            attrs.append(f'padding-y="{self.escape_html(args["padding-y"])}"')

        return " " + " ".join(attrs) if attrs else ""

    def process(self, markdown_content: str) -> str:
        """
        Markdownテキストを受け取り、コンポーネント固有の前処理（置換）を行った結果を返す。
        サブクラスで必ずオーバーライドすること。
        """
        raise NotImplementedError("Subclasses must implement process()")
