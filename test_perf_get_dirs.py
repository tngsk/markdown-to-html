import timeit
import re

html_body = "<div>some normal text without components</div>\n" * 10000 + "<mono-notebook></mono-notebook>" + "\n<div>more text</div>" * 10000

component_names = [
    "mono-poll", "mono-ab-test", "mono-notebook", "mono-textfield-input",
    "mono-reaction", "mono-session-join", "mono-group-assignment",
    "mono-clock", "mono-countdown", "mono-score", "mono-hero",
    "mono-drawer", "mono-layout", "mono-spacer", "mono-flipcard",
    "mono-theme", "mono-icon", "mono-dice", "mono-sound"
]

def search_loop(html_body):
    used = []
    for name in component_names:
        if f"<{name}" in html_body:
            used.append(name)
    return used

def search_regex(html_body):
    # Find all components actually present in the body
    found_tags = set(re.findall(r"<(mono-[a-z0-9-]+)", html_body))
    used = []
    for name in component_names:
        if name in found_tags:
            used.append(name)
    return used

print("search_loop: ", timeit.timeit("search_loop(html_body)", globals=globals(), number=100))
print("search_regex: ", timeit.timeit("search_regex(html_body)", globals=globals(), number=100))
