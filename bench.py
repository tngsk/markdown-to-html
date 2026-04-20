import timeit
import html

def escape1(text):
    replacements = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
    }
    for char, escaped in replacements.items():
        text = text.replace(char, escaped)
    return text

escapes = {
    ord("&"): "&amp;",
    ord("<"): "&lt;",
    ord(">"): "&gt;",
    ord('"'): "&quot;",
    ord("'"): "&#39;",
}
def escape2(text):
    return text.translate(escapes)

def escape3(text):
    return html.escape(text, quote=True)

test_string = "Hello <world> & \"friends\" 'who' are cool." * 100

print(timeit.timeit("escape1(test_string)", globals=globals(), number=10000))
print(timeit.timeit("escape2(test_string)", globals=globals(), number=10000))
print(timeit.timeit("escape3(test_string)", globals=globals(), number=10000))
