import html

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
        parts = []
        current = []
        paren_depth = 0
        in_quote = None
        for char in args_str:
            if in_quote:
                current.append(char)
                if char == in_quote:
                    in_quote = None
            elif char in "\"'":
                in_quote = char
                current.append(char)
            elif char == '(':
                paren_depth += 1
                current.append(char)
            elif char == ')':
                paren_depth -= 1
                current.append(char)
            elif char == ',' and paren_depth == 0:
                parts.append(''.join(current).strip())
                current.clear()
            else:
                current.append(char)
        if current:
            parts.append(''.join(current).strip())

        for part in parts:
            if part:
                split_idx = part.find('=')
                if split_idx == -1:
                    split_idx = part.find(':')

                if split_idx != -1:
                    k = part[:split_idx].strip()
                    v = part[split_idx+1:].strip()
                    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                        v = v[1:-1]
                    result[k] = v
        return result

    def process(self, markdown_content: str) -> str:
        """
        Markdownテキストを受け取り、コンポーネント固有の前処理（置換）を行った結果を返す。
        サブクラスで必ずオーバーライドすること。
        """
        raise NotImplementedError("Subclasses must implement process()")
