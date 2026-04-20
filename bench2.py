import timeit

def multi_replace(text):
    return text.replace("{TITLE}", "Title").replace("{CSP_META}", "Meta").replace("{CSS_BLOCK}", "CSS").replace("{HIGHLIGHT_JS_CSS}", "HL_CSS").replace("{CODE_BLOCK_CSS}", "CB_CSS").replace("{HIGHLIGHT_JS}", "HL_JS").replace("{COPY_BUTTON_JS}", "CB_JS").replace("{BODY}", "Body")

def dict_replace(text):
    import re
    replacements = {
        "{TITLE}": "Title",
        "{CSP_META}": "Meta",
        "{CSS_BLOCK}": "CSS",
        "{HIGHLIGHT_JS_CSS}": "HL_CSS",
        "{CODE_BLOCK_CSS}": "CB_CSS",
        "{HIGHLIGHT_JS}": "HL_JS",
        "{COPY_BUTTON_JS}": "CB_JS",
        "{BODY}": "Body",
    }
    def replacer(match):
        return replacements[match.group(0)]
    pattern = re.compile("|".join(re.escape(k) for k in replacements.keys()))
    return pattern.sub(replacer, text)


test_string = "Here is some HTML with {TITLE} and {BODY} and {CSS_BLOCK}." * 1000

print(timeit.timeit("multi_replace(test_string)", globals=globals(), number=1000))
print(timeit.timeit("dict_replace(test_string)", globals=globals(), number=1000))
