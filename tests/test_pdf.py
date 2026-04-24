import pytest
from pathlib import Path
import logging
from src.processors.pdf import PDFProcessor
from src.config import ConversionConfig

def test_pdf_processor_export_html_to_pdf_no_playwright(tmp_path, monkeypatch):
    logger = logging.getLogger("test")
    processor = PDFProcessor(logger)

    # playwright モジュールが存在しないかのようにモックする
    import sys
    monkeypatch.setitem(sys.modules, "playwright", None)
    monkeypatch.setitem(sys.modules, "playwright.sync_api", None)

    html_file = tmp_path / "test.html"
    html_file.write_text("<html><body><h1>Test PDF</h1></body></html>")

    pdf_file = tmp_path / "test.pdf"

    # 実行
    result = processor.export_html_to_pdf(html_file, pdf_file)

    # アサーション（ImportErrorをキャッチしてFalseを返すはず）
    assert result is False

def test_config_resolve_pdf_output_file():
    config = ConversionConfig(
        input_file=Path("test.md"),
        output_file=None,
        css_files=None,
        pdf_output=True
    )
    assert config.resolve_pdf_output_file() == Path("test.pdf")

    config2 = ConversionConfig(
        input_file=Path("test.md"),
        output_file=None,
        css_files=None,
        pdf_output=Path("custom.pdf")
    )
    assert config2.resolve_pdf_output_file() == Path("custom.pdf")

    config3 = ConversionConfig(
        input_file=Path("test.md"),
        output_file=None,
        css_files=None,
        pdf_output=None
    )
    assert config3.resolve_pdf_output_file() is None
