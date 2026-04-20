import re

html_content = "<div><span>text</span></div><p>hello</p>"
excluded = ["div", "span"]

def original(html_content, excluded_tags):
    if not excluded_tags:
        return html_content

    for tag in excluded_tags:
        # 自己終了タグ（<hr /> など）
        pattern_self_closing = re.compile(rf"<{tag}[^>]*/?\s*>", re.IGNORECASE)
        html_content = pattern_self_closing.sub("", html_content)

        # 開閉タグ（<div>...</div> など）
        pattern_paired = re.compile(
            rf"<{tag}[^>]*>.*?</{tag}>", re.IGNORECASE | re.DOTALL
        )
        html_content = pattern_paired.sub("", html_content)

    return html_content

print(original(html_content, excluded))
print(original("<div><p>hello</p></div><span>test</span>", excluded))
