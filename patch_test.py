import re

html_body = "here is a <mono-poll id='test'></mono-poll> and a <mono-icon></mono-icon>"
found_mono_tags = set(re.findall(r"<(mono-[a-z0-9-]+)", html_body))
print(found_mono_tags)
