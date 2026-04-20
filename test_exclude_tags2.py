import re
from src.processors.html import HTMLDocumentBuilder
import logging

logger = logging.getLogger(__name__)
builder = HTMLDocumentBuilder(logger)

# Normal structure
html_content = "<div><span>text</span></div><p>hello</p>"
excluded = ["div", "span"]
print(builder._remove_excluded_tags(html_content, excluded))

html_content = "<div><p>hello</p></div><span>test</span>"
excluded = ["div", "span"]
print(builder._remove_excluded_tags(html_content, excluded))
