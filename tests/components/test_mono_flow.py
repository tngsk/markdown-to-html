import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import pytest
import importlib.util
from pathlib import Path
import json

# Load the parser dynamically as per AGENTS.md rules for hypenated directories
def load_parser():
    parser_file = Path("src/components/mono-flow/parser.py")
    spec = importlib.util.spec_from_file_location("mono_flow_parser", parser_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Parser()

@pytest.fixture
def parser():
    return load_parser()

def test_mono_flow_basic(parser):
    markdown = """
@[flow: My Flow]
Phase 1 -> Phase 2 : Process
Phase 2 -> Phase 3
@[/flow]
"""
    html = parser.process(markdown)

    # Assert tag and title
    assert '<mono-flow' in html
    assert 'title="My Flow"' in html

    # Assert nodes
    assert '<div class="flow-node" data-id="Phase 1">Phase 1</div>' in html
    assert '<div class="flow-node" data-id="Phase 2">Phase 2</div>' in html
    assert '<div class="flow-node" data-id="Phase 3">Phase 3</div>' in html

    # Assert layers (Phase 1 = 0, Phase 2 = 1, Phase 3 = 2)
    assert '<div class="flow-layer" data-layer="0">' in html
    assert '<div class="flow-layer" data-layer="1">' in html
    assert '<div class="flow-layer" data-layer="2">' in html

    # Extract and parse JSON edges
    json_start = html.find('<script type="application/json" class="flow-connections">')
    assert json_start != -1
    json_start += len('<script type="application/json" class="flow-connections">')
    json_end = html.find('</script>', json_start)
    edges_json = html[json_start:json_end]

    edges = json.loads(edges_json)
    assert len(edges) == 2

    edge1 = next(e for e in edges if e["from"] == "Phase 1")
    assert edge1["to"] == "Phase 2"
    assert edge1["label"] == "Process"

    edge2 = next(e for e in edges if e["from"] == "Phase 2")
    assert edge2["to"] == "Phase 3"
    assert edge2["label"] == ""

def test_mono_flow_branch_and_merge(parser):
    markdown = """
@[flow]
Start -> Branch A
Start -> Branch B
Branch A -> End
Branch B -> End
@[/flow]
"""
    html = parser.process(markdown)

    # Verify nodes
    assert 'data-id="Start"' in html
    assert 'data-id="Branch A"' in html
    assert 'data-id="Branch B"' in html
    assert 'data-id="End"' in html

    # Layers logic: Start=0, BranchA/B=1, End=2
    # Check that Start is in layer 0
    layer0_idx = html.find('data-layer="0"')
    layer1_idx = html.find('data-layer="1"')
    layer2_idx = html.find('data-layer="2"')

    assert layer0_idx < html.find('data-id="Start"', layer0_idx) < layer1_idx

    # Check that End is in layer 2
    assert layer2_idx < html.find('data-id="End"', layer2_idx)

def test_mono_flow_single_node(parser):
    markdown = """
@[flow]
Standalone Node
@[/flow]
"""
    html = parser.process(markdown)
    assert '<div class="flow-node" data-id="Standalone Node">Standalone Node</div>' in html

    # Edges should be empty
    json_start = html.find('<script type="application/json" class="flow-connections">')
    json_start += len('<script type="application/json" class="flow-connections">')
    json_end = html.find('</script>', json_start)
    edges_json = html[json_start:json_end]

    edges = json.loads(edges_json)
    assert len(edges) == 0

def test_mono_flow_cycle_handling(parser):
    # Tests that cycle does not cause infinite loop in layer calculation
    markdown = """
@[flow]
A -> B
B -> C
C -> A
@[/flow]
"""
    # Just processing should not hang
    html = parser.process(markdown)
    assert 'data-id="A"' in html
    assert 'data-id="B"' in html
    assert 'data-id="C"' in html

    json_start = html.find('<script type="application/json" class="flow-connections">')
    json_start += len('<script type="application/json" class="flow-connections">')
    json_end = html.find('</script>', json_start)
    edges = json.loads(html[json_start:json_end])
    assert len(edges) == 3
