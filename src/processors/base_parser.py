import html

class BaseComponentParser:
    """コンポーネント用Markdownパーサーの基底クラス"""

    def __init__(self):
        self.counter = 0

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

    def process(self, markdown_content: str) -> str:
        """
        Markdownテキストを受け取り、コンポーネント固有の前処理（置換）を行った結果を返す。
        サブクラスで必ずオーバーライドすること。
        """
        raise NotImplementedError("Subclasses must implement process()")
