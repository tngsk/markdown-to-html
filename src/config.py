"""
Configuration and Exception Classes
===================================
Centralized definitions for conversion configuration and error handling.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union

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


class ConfigurationError(ConversionError):
    """設定エラー"""

    pass


# ============================================================================
# Data Classes & Configuration
# ============================================================================


@dataclass
class ConversionConfig:
    """変換処理の設定を保持するデータクラス"""

    input_file: Path
    output_file: Optional[Path] = None
    css_files: Optional[List[Path]] = None
    template_path: Optional[Path] = None
    verbose: bool = False
    excluded_tags: Optional[List[str]] = None
    force: bool = False
    enable_export: bool = False
    pdf_output: Union[Path, bool, None] = None
    theme: Optional[str] = None
    connect_src: str = ""
    csp_additions: dict[str, List[str]] = None
    profile: Optional[str] = None
    profile_components: Optional[List[str]] = None

    def __post_init__(self):
        self.csp_additions = {}
        self.profile_components = []
        config_paths = [
            Path.cwd() / "config.toml",
            Path(__file__).resolve().parent.parent / "config.toml",
        ]
        config_path = next((p for p in config_paths if p.is_file()), None)
        if config_path:
            try:
                with open(config_path, "rb") as f:
                    config_data = tomllib.load(f)
                    security = config_data.get("security", {})
                    self.connect_src = security.get("connect-src", "")
                    self.csp_additions = security.get("csp-additions", {})
                    
                    # Profiles resolving
                    profiles = config_data.get("profiles", {})
                    if self.profile:
                        if self.profile == "static":
                            active_profile_name = "minimal"
                        elif self.profile in profiles:
                            active_profile_name = self.profile
                        else:
                            raise ConfigurationError(f"未定義のプロファイルが指定されました: {self.profile}")
                    else:
                        active_profile_name = profiles.get("default", "standard")

                    if active_profile_name in profiles and isinstance(profiles[active_profile_name], dict):
                        self.profile_components = profiles[active_profile_name].get("components", [])
            except ConfigurationError:
                raise
            except Exception:
                pass

    def resolve_output_file(self) -> Path:
        """出力ファイルパスを決定する（未指定時は入力ファイル名から生成）"""
        if self.output_file:
            return self.output_file

        dist_dir = self.input_file.parent / "dist"
        if dist_dir.is_dir():
            return dist_dir / self.input_file.with_suffix(".html").name

        return self.input_file.with_suffix(".html")

    def resolve_pdf_output_file(self) -> Optional[Path]:
        """PDF出力ファイルパスを決定する"""
        if self.pdf_output is None or self.pdf_output is False:
            return None
        pdf_file: Path
        if isinstance(self.pdf_output, bool) and self.pdf_output:
            dist_dir = self.input_file.parent / "dist"
            if dist_dir.is_dir():
                pdf_file = dist_dir / self.input_file.with_suffix(".pdf").name
            else:
                pdf_file = self.input_file.with_suffix(".pdf")
        else:
            pdf_file = Path(self.pdf_output)

        # HTML出力先との衝突を検証
        html_file = self.resolve_output_file()
        try:
            if html_file.resolve() == pdf_file.resolve():
                raise ConfigurationError(
                    f"HTML出力先とPDF出力先に同一のファイルパスが指定されています: {html_file}"
                )
        except ValueError:
            pass

        return pdf_file


@dataclass
class ConversionStats:
    """変換結果の統計情報"""

    images_embedded: int = 0
    css_files_embedded: int = 0
    output_file_size: int = 0
    markdown_file: Optional[str] = None
    output_file: Optional[str] = None
