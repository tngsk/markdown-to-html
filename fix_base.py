import re

with open('src/processors/base_parser.py', 'r') as f:
    content = f.read()

# Add `class` and `id` handling to `get_common_attributes`
content = content.replace('''        if 'padding' in args:
            attrs.append(f'padding="{self.escape_html(args["padding"])}"')''', '''        if 'class' in args:
            attrs.append(f'class="{self.escape_html(args["class"])}"')
        if 'id' in args:
            attrs.append(f'id="{self.escape_html(args["id"])}"')
        if 'padding' in args:
            attrs.append(f'padding="{self.escape_html(args["padding"])}"')''')

with open('src/processors/base_parser.py', 'w') as f:
    f.write(content)
