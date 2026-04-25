import importlib.util
import os
import sys

# Because the folder is "mono-drawer" (with a hyphen), we have to dynamically import it
parser_file = os.path.join("src", "components", "mono-drawer", "parser.py")
spec = importlib.util.spec_from_file_location("mono_drawer_parser", parser_file)
drawer_parser = importlib.util.module_from_spec(spec)
sys.modules["mono_drawer_parser"] = drawer_parser
spec.loader.exec_module(drawer_parser)

Parser = drawer_parser.Parser

def test_mono_drawer_parser():
    parser = Parser()

    # Test basic default drawer
    markdown = '@[drawer: Notes]\nHello\n@[/drawer]'
    html = parser.process(markdown)
    assert '<mono-drawer label="Notes" position="left" markdown="1">' in html
    assert 'Hello' in html
    assert '</mono-drawer>' in html

    # Test drawer with arguments
    markdown = '@[drawer: Notes](position: right, open: true)\nHello\n@[/drawer]'
    html = parser.process(markdown)
    assert '<mono-drawer label="Notes" position="right" open="true" markdown="1">' in html

    # Test drawer with quoted label and position
    markdown = '@[drawer: "My Notes"](position: top, open: "false")\nHello\n@[/drawer]'
    html = parser.process(markdown)
    assert '<mono-drawer label="My Notes" position="top" markdown="1">' in html

    # Test label in arguments
    markdown = '@[drawer](label: Sidebar, position: bottom)\nWorld\n@[/drawer]'
    html = parser.process(markdown)
    assert '<mono-drawer label="Sidebar" position="bottom" markdown="1">' in html
