import timeit
import re

html_content = "<div><p>Testing</p><hr /></div>" * 1000
excluded_tags = ["hr", "div"]

def remove_excluded_tags_original(html_content, excluded_tags):
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

def remove_excluded_tags_fast(html_content, excluded_tags):
    if not excluded_tags:
        return html_content

    tags = "|".join(re.escape(tag) for tag in excluded_tags)

    pattern_self_closing = re.compile(rf"<(?:{tags})[^>]*/?\s*>", re.IGNORECASE)
    html_content = pattern_self_closing.sub("", html_content)

    pattern_paired = re.compile(
        rf"<(?:{tags})[^>]*>.*?</(?:{tags})>", re.IGNORECASE | re.DOTALL
    )
    html_content = pattern_paired.sub("", html_content)

    return html_content

print(timeit.timeit("remove_excluded_tags_original(html_content, excluded_tags)", globals=globals(), number=100))
print(timeit.timeit("remove_excluded_tags_fast(html_content, excluded_tags)", globals=globals(), number=100))
