import timeit
import re

html_body = "<div>some normal text without components</div>\n" * 1000 + "<mono-notebook></mono-notebook>" + "\n<div>more text</div>" * 1000

components_dirs = [
    "mono-poll", "mono-ab-test", "mono-notebook", "mono-textfield-input",
    "mono-reaction", "mono-session-join", "mono-group-assignment",
    "mono-clock", "mono-countdown", "mono-score", "mono-hero",
    "mono-drawer", "mono-layout", "mono-spacer", "mono-flipcard",
    "mono-theme", "mono-icon", "mono-dice", "mono-sound",
    "mono-export", "mono-sync", "mono-brush"
]

def original(html_body):
    has_interactive_components = any(
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
    should_enable_export = has_interactive_components

    used_dirs = []
    for name in components_dirs:
        # 常に含めるコンポーネント
        if name in ["mono-sync", "mono-brush"]:
            used_dirs.append(name)
            continue

        # エクスポートコンポーネント
        if name == "mono-export":
            if should_enable_export:
                used_dirs.append(name)
            continue

        # HTML内で使用されているかチェック
        if f"<{name}" in html_body:
            used_dirs.append(name)

    return used_dirs

def optimized(html_body):
    found_mono_tags = set(re.findall(r"<(mono-[a-z0-9-]+)", html_body))

    has_interactive_components = any(
        tag in found_mono_tags
        for tag in [
            "mono-poll",
            "mono-ab-test",
            "mono-notebook",
            "mono-textfield-input",
            "mono-reaction",
            "mono-session-join",
            "mono-group-assignment",
        ]
    )
    should_enable_export = has_interactive_components

    used_dirs = []
    for name in components_dirs:
        if name in ["mono-sync", "mono-brush"]:
            used_dirs.append(name)
            continue

        if name == "mono-export":
            if should_enable_export:
                used_dirs.append(name)
            continue

        if name in found_mono_tags:
            used_dirs.append(name)

    return used_dirs

print("original: ", timeit.timeit("original(html_body)", globals=globals(), number=1000))
print("optimized: ", timeit.timeit("optimized(html_body)", globals=globals(), number=1000))
