import re
html_content = "<div><span>text</span></div><p>hello</p>"
tag="div"

# Original logic:
# 1. self-closing
pattern_self_closing = re.compile(rf"<{tag}[^>]*/?\s*>", re.IGNORECASE)
html1 = pattern_self_closing.sub("", html_content)
print("after self closing:", html1)

# 2. paired
pattern_paired = re.compile(rf"<{tag}[^>]*>.*?</{tag}>", re.IGNORECASE | re.DOTALL)
html2 = pattern_paired.sub("", html1)
print("after paired:", html2)
