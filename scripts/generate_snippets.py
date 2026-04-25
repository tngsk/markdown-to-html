import json
import os
from pathlib import Path

def generate_snippets():
    snippets = {}

    # Basic markdown extensions / attr_list
    snippets["Markdown attr_list (class, id)"] = {
        "prefix": "[",
        "body": ["[${1:text}]{${2:.class #id}}"],
        "description": "Markdown attr_list extension for custom CSS classes and IDs"
    }

    # Components
    components = {
        "badge": {
            "attrs": "color: \"${1:blue}\", soft: \"${2:true}\", outline: \"${3:true}\"",
            "desc": "Badge component"
        },
        "icon": {
            "attrs": "name: \"${1:lucide-icon-name}\", size: \"${2:24}\", color: \"${3:currentColor}\"",
            "desc": "Icon component using Lucide"
        },
        "row": {
            "attrs": "class: \"${1:gap-md center}\"",
            "desc": "Row layout component"
        },
        "stack": {
            "attrs": "class: \"${1:gap-md center}\"",
            "desc": "Stack (column) layout component"
        },
        "theme": {
            "attrs": "name: \"${1:theme-name}\", config: \"${2:custom.toml}\"",
            "desc": "Theme component to apply CSS variables"
        },
        "ab-test": {
            "attrs": "name: \"${1:test-name}\"",
            "desc": "A/B test component"
        },
        "account": {
            "attrs": "",
            "desc": "Account management component"
        },
        "brush": {
            "attrs": "",
            "desc": "Brush component"
        },
        "clock": {
            "attrs": "",
            "desc": "Clock component"
        },
        "code-block": {
            "attrs": "language: \"${1:python}\"",
            "desc": "Code block component"
        },
        "countdown": {
            "attrs": "target: \"${1:2025-01-01T00:00:00}\"",
            "desc": "Countdown timer component"
        },
        "dice": {
            "attrs": "sides: \"${1:6}\"",
            "desc": "Dice roller component"
        },
        "drawer": {
            "attrs": "open: \"${1:false}\"",
            "desc": "Drawer component"
        },
        "export": {
            "attrs": "filename: \"${1:export.pdf}\"",
            "desc": "Export button component"
        },
        "flipcard": {
            "attrs": "",
            "desc": "Flipcard component"
        },
        "flow": {
            "attrs": "",
            "desc": "Flow diagram component"
        },
        "group-assignment": {
            "attrs": "",
            "desc": "Group assignment component"
        },
        "hero": {
            "attrs": "title: \"${1:Hero Title}\", subtitle: \"${2:Hero Subtitle}\"",
            "desc": "Hero section component"
        },
        "notebook": {
            "attrs": "",
            "desc": "Notebook component"
        },
        "poll": {
            "attrs": "question: \"${1:Question?}\"",
            "desc": "Poll component"
        },
        "reaction": {
            "attrs": "",
            "desc": "Reaction component"
        },
        "score": {
            "attrs": "",
            "desc": "Score component"
        },
        "section": {
            "attrs": "class: \"${1:bg-primary}\"",
            "desc": "Section layout component"
        },
        "session-join": {
            "attrs": "",
            "desc": "Session join component"
        },
        "sound": {
            "attrs": "src: \"${1:audio.mp3}\"",
            "desc": "Sound player component"
        },
        "spacer": {
            "attrs": "height: \"${1:2rem}\"",
            "desc": "Spacer component"
        },
        "sync": {
            "attrs": "",
            "desc": "Sync component"
        },
        "textfield-input": {
            "attrs": "placeholder: \"${1:Enter text...}\"",
            "desc": "Textfield input component"
        }
    }

    for comp, data in components.items():
        prefix = f"@[{comp}"
        if data["attrs"]:
            body = f"@[{comp}]({data['attrs']})"
        else:
            body = f"@[{comp}]"

        snippets[f"Mono Component: {comp}"] = {
            "prefix": prefix,
            "body": [body],
            "description": data["desc"]
        }

    # Ensure directories exist
    os.makedirs(".zed/snippets", exist_ok=True)
    os.makedirs(".vscode", exist_ok=True)

    # Write for Zed
    zed_path = Path(".zed/snippets/markdown.json")
    with open(zed_path, "w") as f:
        json.dump(snippets, f, indent=2)
    print(f"Generated {zed_path}")

    # Write for VSCode
    vscode_path = Path(".vscode/mono.code-snippets")
    with open(vscode_path, "w") as f:
        json.dump(snippets, f, indent=2)
    print(f"Generated {vscode_path}")


if __name__ == "__main__":
    generate_snippets()
