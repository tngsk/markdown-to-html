import pytest
from pathlib import Path
from src.main import create_argument_parser

def test_parser_basic():
    """基本的な引数（入力ファイルのみ）が正しくパースされることをテスト"""
    parser = create_argument_parser()
    args = parser.parse_args(["test.md"])

    assert args.input_file == Path("test.md")
    assert args.output is None
    assert args.css is None
    assert args.verbose is False
    assert args.template is None
    assert args.excluded_tags is None
    assert args.force is False
    assert args.export is False
    assert args.pdf is None

def test_parser_all_options():
    """全てのオプションを指定した場合に正しくパースされることをテスト"""
    parser = create_argument_parser()
    args = parser.parse_args([
        "doc.md",
        "-o", "out.html",
        "-c", "style1.css", "style2.css",
        "-v",
        "-t", "custom.html",
        "-e", "hr", "div",
        "--force",
        "--export"
    ])

    assert args.input_file == Path("doc.md")
    assert args.output == Path("out.html")
    assert args.css == [Path("style1.css"), Path("style2.css")]
    assert args.verbose is True
    assert args.template == Path("custom.html")
    assert args.excluded_tags == ["hr", "div"]
    assert args.force is True
    assert args.export is True

def test_parser_pdf_option():
    """--pdfオプションの動作をテスト"""
    parser = create_argument_parser()

    # 引数なしの--pdf（constが適用される）
    args_no_val = parser.parse_args(["doc.md", "--pdf"])
    assert args_no_val.pdf is True

    # 引数ありの--pdf
    args_with_val = parser.parse_args(["doc.md", "--pdf", "custom.pdf"])
    assert args_with_val.pdf == Path("custom.pdf")

def test_parser_missing_input():
    """必須引数（入力ファイル）が欠落している場合のエラーをテスト"""
    parser = create_argument_parser()

    # parse_argsはエラー時にSystemExitを発生させる
    with pytest.raises(SystemExit):
        parser.parse_args([])

def test_parser_invalid_option():
    """存在しないオプションを指定した場合のエラーをテスト"""
    parser = create_argument_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(["doc.md", "--unknown-option"])
