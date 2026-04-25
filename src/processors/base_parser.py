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
    def parse_key_value_args(args_str: str) -> dict:
        if not args_str:
            return {}
        result = {}

        # Fast path for simple cases without nested parens or complex quotes
        if '(' not in args_str and '"' not in args_str and "'" not in args_str:
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
            elif char == ',' and paren_depth == 0:
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

    def process(self, markdown_content: str) -> str:
        """
        Markdownテキストを受け取り、コンポーネント固有の前処理（置換）を行った結果を返す。
        サブクラスで必ずオーバーライドすること。
        """
        raise NotImplementedError("Subclasses must implement process()")
