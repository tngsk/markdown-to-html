import json
import os
import glob
from pathlib import Path

def generate_snippets():
    snippets = {}

    # 1. Basic markdown extensions / attr_list
    snippets["Markdown attr_list (class, id)"] = {
        "prefix": "[",
        "body": ["[${1:text}]{${2:.class #id}}"],
        "description": "Markdown attr_list extension for custom CSS classes and IDs"
    }

    # 2. Dynamically gather options from parser.py files
    components_with_parsers = {}
    for parser_path in glob.glob("src/components/*/parser.py"):
        comp_name = os.path.basename(os.path.dirname(parser_path)).replace("mono-", "")
        options = []
        with open(parser_path, "r") as f:
            for line in f:
                if "# OPTIONS:" in line:
                    opt_str = line.split("# OPTIONS:")[1].strip()
                    if opt_str:
                        options = [o.strip() for o in opt_str.split(",")]
                    break
        components_with_parsers[comp_name] = options

    # Some components might not have parser.py (e.g. implicitly injected ones)
    # or we might want to manually define them if they don't take markdown arguments.
    # Currently mono-brush, mono-sync, mono-export are mostly parameter-less from a markdown perspective,
    # but we can add them to the dictionary for completion.
    implicit_components = {
        "brush": [],
        "sync": [],
        "export": ["filename"],
        "code-block": ["language"]
    }

    # Merge them together (parsers take precedence)
    all_components = {**implicit_components, **components_with_parsers}

    for comp, options in all_components.items():
        prefix = f"@[{comp}"

        # Build the arguments string
        # e.g., color: "${1:val}", soft: "${2:val}"
        if options:
            attr_parts = []
            for i, opt in enumerate(options, start=2): # start at 2 since 1 is usually the label
                # Provide a generic placeholder based on the option name
                attr_parts.append(f'{opt}: \"${{{i}:val}}\"')

            attrs = ", ".join(attr_parts)
            # Use pattern A: specific options in []
            body = f"@[{comp}: \"${{1:Label}}\", {attrs}]"
        else:
            body = f"@[{comp}: \"${{1:Label}}\"]"

        snippets[f"Mono Component: {comp}"] = {
            "prefix": prefix,
            "body": [body],
            "description": f"Mono {comp} component"
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
