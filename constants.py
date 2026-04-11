"""
Constants for Markdown to HTML Converter
========================================
Centralized configuration and constant definitions for the converter.
"""

from pathlib import Path
from typing import Dict

# ============================================================================
# File Paths & Directories
# ============================================================================

# テンプレートディレクトリ
TEMPLATES_DIR = Path(__file__).parent / "templates"

# デフォルトテンプレートパス
DEFAULT_TEMPLATE_PATH = TEMPLATES_DIR / "default.html"

# テンプレートファイル名
BASE_CSS_FILE = "base.css"

# ============================================================================
# Highlight.js Configuration
# ============================================================================

# Highlight.js CDN バージョン
HIGHLIGHT_JS_VERSION = "11.9.0"

# Highlight.js CDN URLs
HIGHLIGHT_JS_CDN_BASE = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js"
HIGHLIGHT_JS_CDN_CSS = (
    f"{HIGHLIGHT_JS_CDN_BASE}/{HIGHLIGHT_JS_VERSION}/styles/atom-one-dark.min.css"
)
HIGHLIGHT_JS_CDN_JS = f"{HIGHLIGHT_JS_CDN_BASE}/{HIGHLIGHT_JS_VERSION}/highlight.min.js"

# ============================================================================
# MIME Type Registry
# ============================================================================

# ファイル拡張子とMIMEタイプのマッピング
MIME_TYPE_REGISTRY: Dict[str, str] = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
    ".bmp": "image/bmp",
    ".tiff": "image/tiff",
}

# デフォルトMIMEタイプ
DEFAULT_MIME_TYPE = "application/octet-stream"

# ============================================================================
# File I/O Encoding
# ============================================================================

# テキストファイルのデフォルトエンコーディング
DEFAULT_TEXT_ENCODING = "utf-8"

# ============================================================================
# HTML Processing
# ============================================================================

# HTMLロギングのフォーマット文字列
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 正規表現パターン
HTML_IMG_TAG_PATTERN = r'<img\s+([^>]*?)src="([^"]+)"([^>]*)/?>'
HTML_SCRIPT_TAG_PATTERN = r'<script\s+([^>]*?)src="([^"]+)"([^>]*)></script>'
HTML_TABLE_STYLE_PATTERN = r'<(td|th)\s+style="[^"]*?"'
HTML_HEAD_CLOSING_TAG = "</head>"
HTML_OPENING_TAG = r"<html[^>]*>"
HTML_TAG_REMOVAL_PATTERN_TEMPLATE = r"<{tag}[^>]*>.*?</{tag}>"
HTML_IPYNB_LINK_PATTERN = r'<a\s+([^>]*?)href="([^"]+\.ipynb)"([^>]*)>(.*?)</a>'
HTML_POLL_COMPONENT_TEMPLATE = (
    '<situ-poll title="{title}" options="{options}"></situ-poll>'
)

# 外部サービス URL
GITHUB_BASE_URL = "https://github.com/"
COLAB_GITHUB_BASE_URL = "https://colab.research.google.com/github/"
COLAB_BADGE_URL = "https://colab.research.google.com/assets/colab-badge.svg"

# Colabリンク変換用テンプレート
HTML_COLAB_BADGE_IMG = '<img src="{badge_url}" alt="Open In Colab" style="vertical-align: middle; margin-right: 6px; height: 20px; width: auto; border-radius: 0;">'
HTML_COLAB_LINK_TEMPLATE = '<a {before_href}href="{colab_url}"{after_href} target="_blank" rel="noopener noreferrer" class="colab-link" style="text-decoration: none;">{badge_img}{link_text}</a>'

# 正規表現フラグ
REGEX_FLAG_IGNORECASE = "IGNORECASE"

# ============================================================================
# Markdown Processing
# ============================================================================

# Markdownの拡張機能リスト
MARKDOWN_EXTENSIONS = ["fenced_code", "tables", "nl2br"]

# 投票コンポーネント（Live Polling）の正規表現パターン
MARKDOWN_POLL_PATTERN = r"@\[poll:\s*(.+?)\]\((.+?)\)"

# ============================================================================
# Size Formatting
# ============================================================================

# バイトサイズのフォーマット単位
SIZE_UNITS = ("B", "KB", "MB", "GB", "TB")
SIZE_UNIT_THRESHOLD = 1024

# ============================================================================
# CLI & Output
# ============================================================================

# CLIのヘッダー表示
HEADER_TEXT = """
╔═══════════════════════════════════════════════════════════════╗
║         Markdown to Single-File HTML Converter                ║
║                    Version 0.1.0                              ║
╚═══════════════════════════════════════════════════════════════╝
"""
