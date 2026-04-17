import pytest
import importlib.util
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# Load the parser module dynamically since it's in a hyphenated directory
components_dir = Path("src/components/mono-dice")
parser_file = components_dir / "parser.py"

spec = importlib.util.spec_from_file_location("src.components.mono_dice.parser", parser_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
Parser = module.Parser

@pytest.fixture
def parser():
    return Parser()

def test_dice_basic(parser):
    markdown = "@[dice]"
    expected = "<mono-dice></mono-dice>"
    assert parser.process(markdown) == expected

def test_dice_with_faces(parser):
    markdown = "@[dice](faces: 6)"
    expected = '<mono-dice faces="6"></mono-dice>'
    assert parser.process(markdown) == expected

def test_dice_with_number(parser):
    markdown = "@[dice](number: 10)"
    expected = '<mono-dice faces="10"></mono-dice>'
    assert parser.process(markdown) == expected

def test_dice_with_both_faces_and_number(parser):
    markdown = "@[dice](number: 10, faces: 12)"
    # number has priority over faces depending on dict order / parsing implementation
    # Based on our implementation: faces = args.get('number') or args.get('faces')
    # So number has priority
    expected = '<mono-dice faces="10"></mono-dice>'
    assert parser.process(markdown) == expected

def test_dice_inline(parser):
    markdown = "Here is a dice: @[dice](number: 8)"
    expected = 'Here is a dice: <mono-dice faces="8"></mono-dice>'
    assert parser.process(markdown) == expected

def test_block_level_tags(parser):
    assert "mono-dice" in parser.block_level_tags