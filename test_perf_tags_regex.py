import re
import timeit

html_content = "<div><p>some text</p></div>\n" * 1000 + "<span>test</span>" * 1000
excluded = ["div", "span"]

def original(html_content, excluded_tags):
    if not excluded_tags:
        return html_content

    for tag in excluded_tags:
        pattern_self_closing = re.compile(rf"<{tag}[^>]*/?\s*>", re.IGNORECASE)
        html_content = pattern_self_closing.sub("", html_content)

        pattern_paired = re.compile(
            rf"<{tag}[^>]*>.*?</{tag}>", re.IGNORECASE | re.DOTALL
        )
        html_content = pattern_paired.sub("", html_content)

    return html_content

def optimized(html_content, excluded_tags):
    if not excluded_tags:
        return html_content

    tags_pattern = "|".join(re.escape(tag) for tag in excluded_tags)

    pattern_self_closing = re.compile(rf"<(?:{tags_pattern})[^>]*/?\s*>", re.IGNORECASE)
    html_content = pattern_self_closing.sub("", html_content)

    pattern_paired = re.compile(
        rf"<({tags_pattern})[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL
    )
    html_content = pattern_paired.sub("", html_content)

    return html_content

print(timeit.timeit("original(html_content, excluded)", globals=globals(), number=10))
print(timeit.timeit("optimized(html_content, excluded)", globals=globals(), number=10))

# Wait, `original` does things in order!
# The original code's behavior on nested tags of different types might be different
# For `<div><span>text</span></div>` excluded=["div", "span"]:
# original:
# tag="div": removes `<div><span>text</span></div>`, leaves ``, result ``, done.
# BUT wait, the original output was `text</span></div><p>hello</p>` for `<div><span>text</span></div><p>hello</p>` because `.*?` is non-greedy, so `<div><span>text</span></div>` is matched as `<div[^>]*>.*?</div[^>]*>` -> wait, `</{tag}>` is exactly `</div>`.
# Oh! The original regex `.*?` means it matches up to the *first* `</div>` it finds.
# Let's see: `<div><span>text</span></div>` -> `<div>` ... `</div>` -> matches the whole thing. Replaced with `""`.
# But wait, why did `original` output `text</span></div><p>hello</p>`?
