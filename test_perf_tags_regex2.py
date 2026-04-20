import re
html_content = "<div><span>text</span></div><p>hello</p>"
pattern = re.compile(r"<div>.*?</div>", re.IGNORECASE | re.DOTALL)
print("regex test:", pattern.sub("", html_content))

# Oh! In the original code, the self closing tag regex matches `<div>`!
tag="div"
pattern_self_closing = re.compile(rf"<{tag}[^>]*/?\s*>", re.IGNORECASE)
print("self closing match:", pattern_self_closing.sub("", html_content))
