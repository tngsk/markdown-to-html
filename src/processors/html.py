"""
HTML Document Builder
=====================
Generates complete HTML documents from markdown with template support.
"""

import json
import logging
import re
from pathlib import Path
from typing import List, Optional

from src.config import ConversionError
from src.constants import (
    BASE_CSS_FILE,
    COLAB_BADGE_URL,
    COLAB_GITHUB_BASE_URL,
    DEFAULT_TEMPLATE_PATH,
    GITHUB_BASE_URL,
    HIGHLIGHT_JS_CDN_CSS,
    HIGHLIGHT_JS_CDN_JS,
    HTML_COLAB_BADGE_IMG,
    HTML_COLAB_LINK_TEMPLATE,
    HTML_IPYNB_LINK_PATTERN,
    HTML_TABLE_STYLE_PATTERN,
    MATERIAL_SYMBOLS_URL,
    TEMPLATES_DIR,
    COMPONENTS_DIR,
)


class HTMLDocumentBuilder:
    """テンプレートベースのHTMLドキュメント生成クラス"""

    def __init__(self, logger: logging.Logger, template_path: Optional[Path] = None):
        self.logger = logger
        self.template_path = template_path or DEFAULT_TEMPLATE_PATH

    def build_document(
        self,
        html_body: str,
        css_content: Optional[str] = None,
        title: str = "Document",
        excluded_tags: Optional[List[str]] = None,
        connect_src: str = "",
        ws_src: str = "",
        asset_store: Optional[dict] = None,
        enable_export: bool = False,
    ) -> str:
        """
        テンプレートとHTML断片からドキュメントを生成

        Args:
            html_body: <body>に挿入するHTML
            css_content: <head>に挿入するCSS（オプション）
            title: ドキュメントのタイトル

        Returns:
            完全なHTMLドキュメント
        """
        try:
            # テンプレートを読み込む
            template_content = self.template_path.read_text(encoding="utf-8")
            self.logger.debug(f"テンプレート読み込み: {self.template_path}")
        except FileNotFoundError as e:
            raise ConversionError(
                f"テンプレートファイルが見つかりません: {self.template_path}"
            ) from e
        except Exception as e:
            raise ConversionError(f"テンプレート読み込みエラー: {e}") from e

        # コードブロック拡張（コピーボタン、シンタックスハイライト準備）
        html_body = self._enhance_code_blocks(html_body)

        # テーブルインラインスタイル削除
        html_body = self._remove_table_inline_styles(html_body)

        # 除外タグ削除
        html_body = self._remove_excluded_tags(html_body, excluded_tags)

        # カスタム記法処理（{{...}} → <span class="nowrap">...</span>）
        html_body = self._replace_custom_nowrap(html_body)

        # Colabリンクの変換処理 (.ipynb)
        html_body = self._enhance_colab_links(html_body)

        # プレースホルダーを置換
        safe_title = self._escape_html(title)
        css_block = self._build_css_block(css_content)

        # エクスポート機能の自動判定
        has_interactive_components = any(
            tag in html_body
            for tag in [
                "<mono-poll",
                "<mono-ab-test",
                "<mono-notebook",
                "<mono-textfield-input",
                "<mono-reaction",
                "<mono-session-join",
                "<mono-group-assignment",
            ]
        )
        should_enable_export = enable_export or has_interactive_components

        if should_enable_export:
            html_body += "\n<mono-export></mono-export>"

        # 使用されているコンポーネントを特定
        used_component_dirs = self._get_used_component_dirs(html_body, should_enable_export)

        # コードブロック用リソース（CSS/JS）を読み込む
        base_css = self._load_base_css()

        has_code_block = "<mono-code-block" in html_body
        highlight_js_css = self._build_highlight_js_link() if has_code_block else ""
        highlight_js = self._load_highlight_js_script() if has_code_block else ""

        mono_components_js = self._load_mono_components_script(used_component_dirs)
        component_templates = self._load_component_templates(used_component_dirs)

        connect_src_str = " ".join(filter(None, ["'self'", connect_src, ws_src]))
        csp_meta = f"<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'self' 'unsafe-inline' data: https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://fonts.googleapis.com https://fonts.gstatic.com; img-src 'self' data: https://colab.research.google.com; connect-src {connect_src_str}; object-src 'none'; font-src 'self' data: https://fonts.gstatic.com;\">"

        meta_tags = []
        if connect_src:
            meta_tags.append(f'<meta name="mono-api-url" content="{connect_src}">')
        if ws_src:
            meta_tags.append(f'<meta name="mono-ws-url" content="{ws_src}">')

        meta_tags_html = "\n".join(meta_tags)
        if meta_tags_html:
            csp_meta += f"\n        {meta_tags_html}"

        # アイコンが使われている場合はGoogle Fontsのリンクを追加
        fonts_link = ""
        if "<mono-icon" in html_body:
            fonts_link = f'\n        <link rel="stylesheet" href="{MATERIAL_SYMBOLS_URL}" />'

        doc = template_content.replace("{TITLE}", safe_title)
        doc = doc.replace("{CSP_META}", csp_meta + fonts_link)
        doc = doc.replace("{CSS_BLOCK}", css_block)
        doc = doc.replace("{HIGHLIGHT_JS_CSS}", highlight_js_css)
        doc = doc.replace("{CODE_BLOCK_CSS}", base_css)
        doc = doc.replace("{HIGHLIGHT_JS}", highlight_js)

        if asset_store:
            asset_template = (
                f'<template id="mono-asset-store">{json.dumps(asset_store)}</template>'
            )
            lazy_load_js = self._load_lazy_load_script()
            lazy_load_script = (
                f"\n<script>\n{lazy_load_js}\n</script>\n" if lazy_load_js else ""
            )
            html_body += f"\n{asset_template}\n{lazy_load_script}"

        # 既存の {COPY_BUTTON_JS} プレースホルダーにまとめて追記する
        combined_js = f"{component_templates}\n{mono_components_js}"
        doc = doc.replace("{COPY_BUTTON_JS}", combined_js)
        doc = doc.replace(
            "{BODY}", html_body
        )  # Ensure BODY is replaced after appending asset store

        return doc

    def _build_css_block(self, css_content: Optional[str]) -> str:
        """CSSブロックを構築（ない場合は空文字列）"""
        if not css_content:
            return ""
        return f"    <style>\n{css_content}\n    </style>\n"

    def extract_title_from_html(self, html_content: str) -> str:
        """
        HTMLから最初の<h1>をタイトルとして抽出

        Args:
            html_content: HTML文字列

        Returns:
            抽出されたタイトル（デフォルト: "Document"）
        """
        match = re.search(r"<h1>(.+?)</h1>", html_content)
        if match:
            # HTMLタグを削除
            title = re.sub(r"<[^>]+>", "", match.group(1))
            return title[:60]  # 最大60文字
        return "Document"

    @staticmethod
    def _escape_html(text: str) -> str:
        """HTML特殊文字をエスケープ"""
        replacements = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;",
        }
        for char, escaped in replacements.items():
            text = text.replace(char, escaped)
        return text

    def _enhance_code_blocks(self, html_content: str) -> str:
        """
        コードブロックを拡張（コピーボタン、シンタックスハイライト対応）
        """
        # <pre><code ...>...</code></pre> パターンを検索
        pattern = re.compile(
            r'(<pre><code(?:\s+class="([^"]*)")?>.*?</code></pre>)', re.DOTALL
        )

        def replacer(match: re.Match) -> str:
            original_block = match.group(1)
            lang_class = match.group(2) or ""

            # 言語クラスから言語名を抽出（"language-python" → "python"）
            language = ""
            if lang_class:
                lang_match = re.search(r"language-(\w+)", lang_class)
                if lang_match:
                    language = lang_match.group(1)

            # コードブロックの新しい構造を構築
            enhanced = f'<mono-code-block language="{language}">\n{original_block}\n</mono-code-block>'
            return enhanced

        result = pattern.sub(replacer, html_content)
        return result

    def _remove_table_inline_styles(self, html_content: str) -> str:
        """
        テーブルタグから不要なインラインスタイルを削除

        Markdownライブラリが付与する text-align: left; などを除去
        """
        # <td style="..."> → <td>
        # <th style="..."> → <th>
        pattern = re.compile(HTML_TABLE_STYLE_PATTERN, re.IGNORECASE)
        result = pattern.sub(r"<\1", html_content)
        return result

    def _remove_excluded_tags(
        self, html_content: str, excluded_tags: Optional[List[str]]
    ) -> str:
        """
        指定されたタグをHTMLから削除（タグとその中身も一緒に削除）

        Args:
            html_content: HTML文字列
            excluded_tags: 削除対象のタグ名リスト（例：["hr", "div"]）

        Returns:
            タグ削除後のHTML
        """
        if not excluded_tags:
            return html_content

        for tag in excluded_tags:
            # 自己終了タグ（<hr /> など）
            pattern_self_closing = re.compile(rf"<{tag}[^>]*/?\s*>", re.IGNORECASE)
            html_content = pattern_self_closing.sub("", html_content)

            # 開閉タグ（<div>...</div> など）
            pattern_paired = re.compile(
                rf"<{tag}[^>]*>.*?</{tag}>", re.IGNORECASE | re.DOTALL
            )
            html_content = pattern_paired.sub("", html_content)

            self.logger.debug(f"タグ削除完了: {tag}")

        return html_content

    def _enhance_colab_links(self, html_content: str) -> str:
        """
        URLに .ipynb が含まれるリンクを検知し、Google Colabリンクに変換する。
        """
        pattern = re.compile(HTML_IPYNB_LINK_PATTERN, re.IGNORECASE)

        def replacer(match: re.Match) -> str:
            before_href = match.group(1)
            url = match.group(2)
            after_href = match.group(3)
            link_text = match.group(4)

            # GitHubのURLであれば、Colab用のURLに変換
            colab_url = url
            if url.startswith(GITHUB_BASE_URL):
                colab_url = url.replace(GITHUB_BASE_URL, COLAB_GITHUB_BASE_URL)

            badge_img = HTML_COLAB_BADGE_IMG.format(badge_url=COLAB_BADGE_URL)

            return HTML_COLAB_LINK_TEMPLATE.format(
                before_href=before_href,
                colab_url=colab_url,
                after_href=after_href,
                badge_img=badge_img,
                link_text=link_text,
            )

        result = pattern.sub(replacer, html_content)
        self.logger.debug("Colabリンク処理完了: .ipynbリンクをColabバッジに変換")
        return result

    def _replace_custom_nowrap(self, html_content: str) -> str:
        """
        カスタム記法 {{...}} をno改行しないテキストに変換

        {{連結テキスト}} → <span class="nowrap">連結テキスト</span>

        Args:
            html_content: HTML文字列

        Returns:
            記法処理後のHTML
        """
        pattern = re.compile(r"\{\{(.*?)\}\}")
        result = pattern.sub(r'<span class="nowrap">\1</span>', html_content)
        self.logger.debug(
            'カスタム記法処理完了: {{...}} → <span class="nowrap">...</span>'
        )
        return result

    def _build_highlight_js_link(self) -> str:
        """Highlight.js CSSリンクタグを構築"""
        return f'<link rel="stylesheet" href="{HIGHLIGHT_JS_CDN_CSS}">'

    def _load_lazy_load_script(self) -> str:
        """lazy_load.js ファイルを読み込んで返す"""
        js_file = TEMPLATES_DIR / "core" / "lazy_load.js"
        try:
            return js_file.read_text(encoding="utf-8")
        except FileNotFoundError:
            self.logger.warning(f"lazy_load.js が見つかりません: {js_file}")
            return ""
        except Exception as e:
            self.logger.warning(f"lazy_load.js の読み込みエラー: {e}")
            return ""

    def _load_base_css(self) -> str:
        """base.css ファイルを読み込んで <style> タグで返す"""
        css_file = TEMPLATES_DIR / "core" / BASE_CSS_FILE
        try:
            css_content = css_file.read_text(encoding="utf-8")
            return f"<style>\n{css_content}\n</style>"
        except FileNotFoundError:
            self.logger.warning(f"base.css が見つかりません: {css_file}")
            return ""
        except Exception as e:
            self.logger.warning(f"base.css の読み込みエラー: {e}")
            return ""

    def _load_highlight_js_script(self) -> str:
        """Highlight.js スクリプトタグを構築"""
        return f'<script src="{HIGHLIGHT_JS_CDN_JS}"></script>'

    def _get_used_component_dirs(self, html_body: str, should_enable_export: bool) -> List[Path]:
        """使用されているコンポーネントのディレクトリ一覧を取得する"""
        components_dir = COMPONENTS_DIR
        if not components_dir.exists() or not components_dir.is_dir():
            return []

        used_dirs = []
        for component_dir in sorted(components_dir.iterdir()):
            if not component_dir.is_dir():
                continue

            name = component_dir.name

            # 常に含めるコンポーネント
            if name in ["mono-sync", "mono-brush"]:
                used_dirs.append(component_dir)
                continue

            # エクスポートコンポーネント
            if name == "mono-export":
                if should_enable_export:
                    used_dirs.append(component_dir)
                continue

            # HTML内で使用されているかチェック
            if f"<{name}" in html_body:
                used_dirs.append(component_dir)

        return used_dirs

    def _load_mono_components_script(self, used_component_dirs: List[Path]) -> str:
        """指定されたコンポーネントの script.js を読み込んで <script> タグで返す"""
        if not used_component_dirs:
            return ""

        js_contents = []
        for component_dir in used_component_dirs:
            js_file = component_dir / "script.js"
            if js_file.exists():
                try:
                    js_contents.append(js_file.read_text(encoding="utf-8"))
                except Exception as e:
                    self.logger.warning(f"JS読み込みエラー ({js_file}): {e}")

        if not js_contents:
            return ""

        combined_js = "\n\n".join(js_contents)
        return f"<script>\n{combined_js}\n</script>"

    def _load_component_templates(self, used_component_dirs: List[Path]) -> str:
        """指定されたコンポーネントの template.html を読み込み、対応する style.css を注入して結合する"""
        if not used_component_dirs:
            return ""

        templates_html = []
        for component_dir in used_component_dirs:
            template_file = component_dir / "template.html"
            css_file = component_dir / "style.css"

            if template_file.exists():
                try:
                    template_content = template_file.read_text(encoding="utf-8")
                    css_content = ""
                    if css_file.exists():
                        try:
                            css_content = css_file.read_text(encoding="utf-8")
                        except Exception as e:
                            self.logger.warning(
                                f"CSS読み込みエラー ({css_file}): {e}"
                            )

                    template_content = template_content.replace(
                        "{COMPONENTS_CSS}", css_content
                    )
                    templates_html.append(template_content)
                except Exception as e:
                    self.logger.warning(
                        f"テンプレート読み込みエラー ({template_file}): {e}"
                    )

        return "\n\n".join(templates_html)
