import re
import glob
import os

def main():
    # 1. Read README.md
    with open("README.md", "r", encoding="utf-8") as f:
        readme_content = f.read()

    # 2. Extract current table rows to preserve Description and Syntax
    table_match = re.search(r"\| コンポーネント \| 概要.*?(\n\n|$)", readme_content, re.DOTALL)
    if not table_match:
        print("Could not find the components table in README.md.")
        return

    table_block = table_match.group(0)
    lines = table_block.split("\n")

    header = lines[0:2]
    body = lines[2:]

    # component_name -> { desc: "...", syntax: "..." }
    table_data = {}
    for line in body:
        if line.strip() and "|" in line:
            parts = line.split("|")
            if len(parts) >= 5:
                comp_name = parts[1].strip().strip("`")
                desc = parts[2].strip()
                syntax = parts[3].strip()
                table_data[comp_name] = {
                    "desc": desc,
                    "syntax": syntax
                }

    # 3. Read options from source
    components_info = []
    for parser_path in sorted(glob.glob("src/components/*/parser.py")):
        comp_name = os.path.basename(os.path.dirname(parser_path))
        options_str = ""
        with open(parser_path, "r", encoding="utf-8") as f:
            for line in f:
                if "# OPTIONS:" in line:
                    opt_str = line.split("# OPTIONS:")[1].strip()
                    if opt_str:
                        options = [f"`{o.strip()}`" for o in opt_str.split(",")]
                        options_str = ", ".join(options)
                    break

        if not options_str:
            options_str = "なし"

        desc = table_data.get(comp_name, {}).get("desc", "説明なし")
        syntax = table_data.get(comp_name, {}).get("syntax", f"`@[{comp_name.replace('mono-', '')}]()`")

        components_info.append({
            "name": comp_name,
            "desc": desc,
            "syntax": syntax,
            "options": options_str
        })

    # 4. Generate new table
    new_table_lines = [
        "| コンポーネント | 概要 | 記述例 | オプション |",
        "|---|---|---|---|"
    ]
    for c in components_info:
        new_table_lines.append(f"| `{c['name']}` | {c['desc']} | {c['syntax']} | {c['options']} |")

    new_table_block = "\n".join(new_table_lines) + "\n\n"

    # 5. Replace in README
    new_readme_content = readme_content.replace(table_block, new_table_block)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_readme_content)

    print("Successfully updated README.md")

if __name__ == "__main__":
    main()
