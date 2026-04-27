import re

with open('src/components/mono-textfield-input/parser.py', 'r') as f:
    content = f.read()

# Make textfield support label attribute if requested, or just use label as placeholder
# Let's see what the original did:
#            if label and not placeholder:
#                placeholder = label.strip()
#            component_id = self.get_next_id("textfield")
#            return f'<mono-textfield-input id="{component_id}" placeholder="{safe_placeholder}"{size_attr}{self.get_common_attributes(args)}></mono-textfield-input>'
# If 'id' is in common attributes, we will have duplicate 'id' attributes unless we check.
# Better to change component_id = args.get('id', self.get_next_id("textfield"))
# And remove `id` from common_args if it is there?
# Actually, since we added `id` to common_attributes, it will append `id="..."` at the end.
# So we should remove `id="{component_id}"` from the template, and just inject it if `id` not in args.

content = content.replace('''            component_id = self.get_next_id("textfield")
            return f'<mono-textfield-input id="{component_id}" placeholder="{safe_placeholder}"{size_attr}{self.get_common_attributes(args)}></mono-textfield-input>''', '''            if 'id' not in args:
                args['id'] = self.get_next_id("textfield")

            label_attr = f' label="{self.escape_html(label)}"' if label else ""

            return f'<mono-textfield-input placeholder="{safe_placeholder}"{size_attr}{label_attr}{self.get_common_attributes(args)}></mono-textfield-input>''')

with open('src/components/mono-textfield-input/parser.py', 'w') as f:
    f.write(content)
