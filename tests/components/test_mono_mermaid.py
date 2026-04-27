import pytest
from unittest.mock import patch, MagicMock
import importlib.util
import re
from pathlib import Path

# mono-mermaidのパーサーを動的にロード
spec = importlib.util.spec_from_file_location("mono_mermaid_parser", "src/components/mono-mermaid/parser.py")
mono_mermaid_parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mono_mermaid_parser)

@pytest.fixture
def parser():
    return mono_mermaid_parser.Parser()

def test_mermaid_basic_parsing(parser):
    """基本的なMermaid構文が正しく処理されるかテスト"""
    markdown_content = """
@[mermaid]
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
@[/mermaid]
"""
    # mock _generate_svg to return a dummy svg
    with patch.object(parser, '_generate_svg', return_value="<svg><g></g></svg>"):
        html_output = parser.process(markdown_content)

        assert "<mono-mermaid" in html_output
        assert "<svg><g></g></svg>" in html_output
        assert "</mono-mermaid>" in html_output

def test_mermaid_with_title(parser):
    """タイトル付きのMermaid構文が正しく処理されるかテスト"""
    markdown_content = """
@[mermaid: "Sample Graph"]
graph TD;
    A-->B;
@[/mermaid]
"""
    with patch.object(parser, '_generate_svg', return_value="<svg></svg>"):
        html_output = parser.process(markdown_content)

        assert 'title="Sample Graph"' in html_output

def test_mermaid_generation_failure(parser):
    """SVG生成に失敗した場合のフォールバックが正しく機能するかテスト"""
    markdown_content = """
@[mermaid]
invalid syntax
@[/mermaid]
"""
    with patch.object(parser, '_generate_svg', return_value=""):
        html_output = parser.process(markdown_content)

        assert '<div class="mermaid-error">' in html_output
        assert "invalid syntax" in html_output
        assert "<mono-mermaid" not in html_output

@patch.object(mono_mermaid_parser.subprocess, 'run')
def test_mermaid_subprocess_call(mock_run, parser):
    """subprocess.runが正しい引数で呼ばれるかテスト"""
    mock_run.return_value = MagicMock(returncode=0)

    # create a fake input/output scenario
    mermaid_code = "graph TD;\n A-->B;"

    with patch.object(mono_mermaid_parser.Path, 'exists', return_value=True), \
         patch.object(mono_mermaid_parser.Path, 'read_text', return_value="<svg>mock</svg>"):

        result = parser._generate_svg(mermaid_code)

        assert result == "<svg>mock</svg>"
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "npx"
        assert args[1] == "mmdc"
        assert "-i" in args
        assert "-o" in args

@patch.object(mono_mermaid_parser.subprocess, 'run')
def test_mermaid_subprocess_error(mock_run, parser):
    """subprocess.runがエラーを投げた場合のハンドリング"""
    import subprocess
    mock_run.side_effect = subprocess.CalledProcessError(1, 'cmd')

    result = parser._generate_svg("graph TD;")
    assert result == ""
