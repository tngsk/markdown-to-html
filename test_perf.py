import re
import html
import timeit

class DummyLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass

def extract_title_from_html_regex(html_content: str) -> str:
    match = re.search(r"<h1>(.+?)</h1>", html_content)
    if match:
        title = re.sub(r"<[^>]+>", "", match.group(1))
        return title[:60]
    return "Document"

def extract_title_from_html_fast(html_content: str) -> str:
    start_idx = html_content.find("<h1>")
    if start_idx != -1:
        end_idx = html_content.find("</h1>", start_idx + 4)
        if end_idx != -1:
            title_html = html_content[start_idx + 4:end_idx]
            # Simple strip of tags, though regex might be needed for nested tags
            title = re.sub(r"<[^>]+>", "", title_html)
            return title[:60]
    return "Document"

html_test = "<div>some stuff</div>" * 1000 + "<h1>My Awesome <b>Title</b></h1>" + "<div>more stuff</div>" * 1000

print("extract_title regex: ", timeit.timeit("extract_title_from_html_regex(html_test)", globals=globals(), number=1000))
print("extract_title fast: ", timeit.timeit("extract_title_from_html_fast(html_test)", globals=globals(), number=1000))
