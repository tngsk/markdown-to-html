import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
# Note: component folders have dashes, but in python they are normally imported via dynamic import.
# The component is at src/components/mono-score/parser.py
# We should probably use importlib to import it or just add the folder to sys.path
import importlib.util

spec = importlib.util.spec_from_file_location("mono_score_parser", "src/components/mono-score/parser.py")
mono_score_parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mono_score_parser)
Parser = mono_score_parser.Parser

def test_mono_score_parser_basic():
    parser = Parser()
    markdown = '@[score](notes: "C4/q, D4/q")'
    result = parser.process(markdown)
    assert '<mono-score notes="C4/q, D4/q"></mono-score>' in result

def test_mono_score_parser_with_clef_and_time():
    parser = Parser()
    markdown = '@[score](notes: "C4/q", clef: "bass", time: "3/4")'
    result = parser.process(markdown)
    assert '<mono-score notes="C4/q" clef="bass" time="3/4"></mono-score>' in result

def test_mono_score_parser_with_colon_syntax():
    parser = Parser()
    markdown = '@[score: C4/q, E4/q](clef: treble)'
    result = parser.process(markdown)
    assert '<mono-score notes="C4/q, E4/q" clef="treble"></mono-score>' in result
