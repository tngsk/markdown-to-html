import timeit
import re
import html

html_content = "some text & < > \" '" * 1000

def escape1(text: str) -> str:
    """HTML特殊文字をエスケープ"""
    replacements = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
    }
    for char, escaped in replacements.items():
        text = text.replace(char, escaped)
    return text

def escape2(text: str) -> str:
    return html.escape(text, quote=True)

print(timeit.timeit("escape1(html_content)", globals=globals(), number=10000))
print(timeit.timeit("escape2(html_content)", globals=globals(), number=10000))
