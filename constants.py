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
    ".wav": "audio/wav",
    ".mp3": "audio/mpeg",
    ".ogg": "audio/ogg",
    ".flac": "audio/flac",
    ".aac": "audio/aac",
    ".m4a": "audio/mp4",
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
HTML_AB_TEST_COMPONENT_TEMPLATE = (
    '<situ-ab-test title="{title}" src-a="{src_a}" src-b="{src_b}"></situ-ab-test>'
)

# 外部サービス URL
GITHUB_BASE_URL = "https://github.com/"
COLAB_GITHUB_BASE_URL = "https://colab.research.google.com/github/"
COLAB_BADGE_URL = "https://colab.research.google.com/assets/colab-badge.svg"

# Colabリンク変換用テンプレート
HTML_COLAB_BADGE_IMG = '<img src="{badge_url}" alt="Open In Colab" class="colab-badge">'
HTML_COLAB_LINK_TEMPLATE = '<a {before_href}href="{colab_url}"{after_href} target="_blank" rel="noopener noreferrer" class="colab-link">{badge_img}{link_text}</a>'

# 正規表現フラグ
REGEX_FLAG_IGNORECASE = "IGNORECASE"

# ============================================================================
# Markdown Processing
# ============================================================================

# Markdownの拡張機能リスト
MARKDOWN_EXTENSIONS = ["fenced_code", "tables", "nl2br", "toc"]

# 投票コンポーネント（Live Polling）の正規表現パターン
MARKDOWN_POLL_PATTERN = r"@\[poll:\s*(.+?)\]\((.+?)\)"

# A/Bテストコンポーネントの正規表現パターン
MARKDOWN_AB_TEST_PATTERN = r"@\[ab-test:\s*(.+?)\]\((.+?),\s*(.+?)\)"

# ノートブック入力コンポーネントの正規表現パターン
MARKDOWN_NOTEBOOK_PATTERN = r"@\[notebook-input\]\((.+?)\)"
HTML_NOTEBOOK_COMPONENT_TEMPLATE = (
    '<situ-notebook-input id="{id}"></situ-notebook-input>'
)

# テキストフィールド入力コンポーネントの正規表現パターン
MARKDOWN_TEXTFIELD_PATTERN = r"@\[(?:textfield|textfiled):\s*(.+?)\]"
HTML_TEXTFIELD_COMPONENT_TEMPLATE = (
    '<situ-textfield-input placeholder="{placeholder}"></situ-textfield-input>'
)

# リアクションコンポーネントの正規表現パターン
MARKDOWN_REACTION_PATTERN = r"@\[reaction:\s*\"?(.*?)\"?\]"
HTML_REACTION_COMPONENT_TEMPLATE = '<situ-reaction options="{options}"></situ-reaction>'

# セッション参加コンポーネントの正規表現パターン
MARKDOWN_SESSION_JOIN_PATTERN = r"@\[session-join:\s*\"?(.*?)\"?\]"
HTML_SESSION_JOIN_COMPONENT_TEMPLATE = (
    '<situ-session-join title="{title}"></situ-session-join>'
)

# グループ分けコンポーネントの正規表現パターン
MARKDOWN_GROUP_ASSIGNMENT_PATTERN = r"@\[group-assignment:\s*\"?(.*?)\"?\]"
HTML_GROUP_ASSIGNMENT_COMPONENT_TEMPLATE = (
    '<situ-group-assignment title="{title}"></situ-group-assignment>'
)


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
