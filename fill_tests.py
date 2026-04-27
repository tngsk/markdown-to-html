import os
import re

components = {
    "mono_ab_test": {
        "markdown": '@[ab-test: "A/B Title"](src-a: "a.html", src-b: "b.html")',
        "expected": '<mono-ab-test'
    },
    "mono_clock": {
        "markdown": '@[clock](time: "10:00")',
        "expected": '<mono-clock time="10:00">'
    },
    "mono_group_assignment": {
        "markdown": '@[group-assignment](groups: 3)',
        "expected": '<mono-group-assignment'
    },
    "mono_icon": {
        "markdown": '@[icon: "home"](size: "md")',
        "expected": '<mono-icon name="home" size="md"'
    },
    "mono_notebook": {
        "markdown": '@[notebook: "test"]()',
        "expected": '<mono-notebook'
    },
    "mono_poll": {
        "markdown": '@[poll: "Question"](options: "A,B")',
        "expected": '<mono-poll'
    },
    "mono_reaction": {
        "markdown": '@[reaction: "👍"]()',
        "expected": '<mono-reaction'
    },
    "mono_session_join": {
        "markdown": '@[session-join: "Room 1"]()',
        "expected": '<mono-session-join'
    },
    "mono_sound": {
        "markdown": '@[sound](src: "test.mp3")',
        "expected": '<mono-sound src="test.mp3"'
    },
    "mono_spacer": {
        "markdown": '@[spacer: "lg"]()',
        "expected": '<mono-spacer'
    },
    "mono_textfield_input": {
        "markdown": '@[textfield: "Name"]()',
        "expected": '<mono-textfield-input'
    }
}

for comp, data in components.items():
    file_path = f"tests/components/test_{comp}.py"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            content = f.read()

        test_func = f"""def test_{comp}_basic(parser):
    markdown = '{data["markdown"]}'
    html = parser.process(markdown)
    assert '{data["expected"]}' in html"""

        content = re.sub(r'def test_.*?_basic\(parser\):\n.*?assert True', test_func, content, flags=re.DOTALL)

        with open(file_path, "w") as f:
            f.write(content)
