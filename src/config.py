"""
Configuration and Exception Classes
===================================
Centralized definitions for conversion configuration and error handling.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

# ============================================================================
# Custom Exceptions
# ============================================================================


class ConversionError(Exception):
    """変換処理中に発生する汎用エラー"""

    pass


class FileProcessingError(ConversionError):
    """ファイル処理エラー"""

    pass


class ImageEmbeddingError(ConversionError):
    """画像埋め込みエラー"""

    pass


class CSSEmbeddingError(ConversionError):
    """CSS埋め込みエラー"""

    pass


# ============================================================================
# Data Classes & Configuration
# ============================================================================


from typing import Union

@dataclass
class ConversionConfig:
    """変換処理の設定を保持するデータクラス"""

    input_file: Path
    output_file: Optional[Path]
    css_files: Optional[List[Path]]
    template_path: Optional[Path] = None
    verbose: bool = False
    excluded_tags: Optional[List[str]] = None
    force: bool = False
    connect_src: str = ""
    ws_src: str = ""
    enable_export: bool = False
    pdf_output: Union[Path, bool, None] = None

    def __post_init__(self):
        try:
            with open("config.toml", "rb") as f:
                config_data = tomllib.load(f)
                self.connect_src = config_data.get("security", {}).get("connect-src", "")
                self.ws_src = config_data.get("security", {}).get("ws-src", "")
        except Exception:
            pass

    def resolve_output_file(self) -> Path:
        """出力ファイルパスを決定する（未指定時は入力ファイル名から生成）"""
        if self.output_file:
            return self.output_file
        return self.input_file.with_suffix(".html")

    def resolve_pdf_output_file(self) -> Optional[Path]:
        """PDF出力ファイルパスを決定する"""
        if self.pdf_output is None:
            return None
        if isinstance(self.pdf_output, bool) and self.pdf_output:
            return self.input_file.with_suffix(".pdf")
        return self.pdf_output


@dataclass
class ConversionStats:
    """変換結果の統計情報"""

    images_embedded: int = 0
    css_files_embedded: int = 0
    output_file_size: int = 0
    markdown_file: Optional[str] = None
    output_file: Optional[str] = None
