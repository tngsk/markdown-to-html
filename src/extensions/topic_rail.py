import re
from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor


class TopicRailPostprocessor(Postprocessor):
    """
    HTML内に class="topic" または class="section" を持つ見出しが存在する場合、
    自動的に <mono-topic-rail></mono-topic-rail> を末尾に注入するポストプロセッサ。
    """

    TOPIC_PATTERN = re.compile(
        r'<h[1-6][^>]*class="[^"]*?\b(?:topic|section)\b[^"]*?"',
        re.IGNORECASE,
    )

    def run(self, text: str) -> str:
        # 明示的な構文 @[topic-rail] の置換
        if "@[topic-rail" in text:
            text = re.sub(
                r"@\[topic-rail(?:(?:\:\s*)?([^\]]*))\](?:\(((?:[^()]*|\([^()]*\))*)\))?(?:\{([^}]*)\})?",
                "<mono-topic-rail></mono-topic-rail>",
                text,
            )

        # 見出しに .topic または .section クラスが存在し、まだタグがない場合
        if "<mono-topic-rail>" not in text and self.TOPIC_PATTERN.search(text):
            text = text + "\n<mono-topic-rail></mono-topic-rail>\n"

        return text


class TopicRailExtension(Extension):
    def extendMarkdown(self, md):
        md.postprocessors.register(TopicRailPostprocessor(md), "mono_topic_rail", 25)


def makeExtension(**kwargs):
    return TopicRailExtension(**kwargs)
