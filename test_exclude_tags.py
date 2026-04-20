import re

excluded_tags = ["div", "span"]
tags_pattern = "|".join(re.escape(tag) for tag in excluded_tags)

html_content = "<div><span>text</span></div>"

pattern_paired = re.compile(
    rf"<({tags_pattern})[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL
)

print(pattern_paired.sub("", html_content))
