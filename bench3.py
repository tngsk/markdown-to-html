import timeit
import re

html_content = "<table><tr><td style='text-align: left;'>Cell</td></tr></table>" * 1000
pattern = re.compile(r"<(td|th) style=\"[^\"]*\">", re.IGNORECASE)

def remove_table_inline_styles(html_content):
    result = pattern.sub(r"<\1", html_content)
    return result

print(timeit.timeit("remove_table_inline_styles(html_content)", globals=globals(), number=1000))
