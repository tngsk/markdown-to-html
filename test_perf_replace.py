import timeit
import re

html_body = "here is a bunch of stuff. " * 100

def has_interactive_components_any(html_body):
    return any(
        tag in html_body
        for tag in [
            "<mono-poll",
            "<mono-ab-test",
            "<mono-notebook",
            "<mono-textfield-input",
            "<mono-reaction",
            "<mono-session-join",
            "<mono-group-assignment",
        ]
    )

def has_interactive_components_regex(html_body):
    pattern = re.compile(r"<(mono-poll|mono-ab-test|mono-notebook|mono-textfield-input|mono-reaction|mono-session-join|mono-group-assignment)")
    return bool(pattern.search(html_body))

print("any: ", timeit.timeit("has_interactive_components_any(html_body)", globals=globals(), number=100000))
print("regex: ", timeit.timeit("has_interactive_components_regex(html_body)", globals=globals(), number=100000))

html_body_with_match = "here is a bunch of stuff. " * 50 + "<mono-notebook" + "here is a bunch of stuff. " * 50

print("any (match): ", timeit.timeit("has_interactive_components_any(html_body_with_match)", globals=globals(), number=100000))
print("regex (match): ", timeit.timeit("has_interactive_components_regex(html_body_with_match)", globals=globals(), number=100000))
