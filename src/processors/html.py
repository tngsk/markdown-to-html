"""
HTML Document Builder
=====================
Generates complete HTML documents from markdown with template support.
"""

import json
import html
import logging
import re
from pathlib import Path
from typing import List, Optional

from src.config import ConversionError
from src.constants import (
    DEFAULT_TEMPLATE_PATH,
    HIGHLIGHT_JS_CDN_CSS,
    HIGHLIGHT_JS_CDN_JS,
    HTML_TABLE_STYLE_PATTERN,
    MATERIAL_SYMBOLS_URL,
    TEMPLATES_DIR,
    COMPONENTS_DIR,
    MONO_VERSION,
)


class HTMLDocumentBuilder:
    """テンプレートベースのHTMLドキュメント生成クラス"""

    def __init__(self, logger: logging.Logger, template_path: Optional[Path] = None):
        self.logger = logger
        self.template_path = template_path or DEFAULT_TEMPLATE_PATH

    def build_document(
        self,
        html_body: str,
        title: str = "Document",
        excluded_tags: Optional[List[str]] = None,
        connect_src: str = "",
        asset_store: Optional[dict] = None,
        enable_export: bool = False,
    ) -> str:
        """
        テンプレートとHTML断片からドキュメントを生成

        Args:
            html_body: <body>に挿入するHTML
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

        # テーブルインラインスタイル削除
        html_body = self._remove_table_inline_styles(html_body)

        # 除外タグ削除
        html_body = self._remove_excluded_tags(html_body, excluded_tags)

        # プレースホルダーを置換
        safe_title = self._escape_html(title)

        # 最適化: HTMLボディからコンポーネントタグを1回のパスで抽出する
        found_mono_tags = set(re.findall(r"<(mono-[a-z0-9-]+)", html_body))

        # エクスポート機能の自動判定
        has_interactive_components = any(
            tag in found_mono_tags
            for tag in [
                "mono-poll",
                "mono-ab-test",
                "mono-notebook",
                "mono-textfield-input",
                "mono-reaction",
                "mono-session-join",
                "mono-group-assignment",
            ]
        )
        should_enable_export = enable_export or has_interactive_components

        if should_enable_export:
            html_body += "\n<mono-export></mono-export>"

        # 使用されているコンポーネントを特定
        used_component_dirs = self._get_used_component_dirs(found_mono_tags, should_enable_export)

        has_code_block = "<mono-code-block" in html_body
        highlight_js_css = self._build_highlight_js_link(html_body) if has_code_block else ""
        highlight_js = self._load_highlight_js_script() if has_code_block else ""

        mathjax = ""
        if 'class="mono-math' in html_body:
            mathjax = self._build_mathjax_script()

        mono_components_js = self._load_mono_components_script(used_component_dirs)
        component_templates = self._load_component_templates(used_component_dirs)

        connect_src_str = " ".join(filter(None, ["'self'", "https://cdn.jsdelivr.net", connect_src]))
        csp_meta = f"<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'self' 'unsafe-inline' data: https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://fonts.googleapis.com https://fonts.gstatic.com; img-src 'self' data: https://colab.research.google.com; connect-src {connect_src_str}; object-src 'none'; font-src 'self' data: https://fonts.gstatic.com; media-src 'self' data: https://actions.google.com;\">"

        meta_tags = []
        meta_tags.append(f'<meta name="mono-version" data-mono-version="{MONO_VERSION}">')
        if connect_src:
            meta_tags.append(f'<meta name="mono-api-url" content="{connect_src}">')

        meta_tags_html = "\n".join(meta_tags)
        if meta_tags_html:
            csp_meta += f"\n        {meta_tags_html}"

        # アイコンが使われている場合はGoogle Fontsのリンクを追加
        fonts_link = ""
        if "<mono-icon" in html_body:
            fonts_link = f'\n        <link rel="stylesheet" href="{MATERIAL_SYMBOLS_URL}" />'

        content_css = self._load_component_content_css(used_component_dirs)

        doc = template_content.replace("{TITLE}", safe_title)
        doc = doc.replace("{CSP_META}", csp_meta + fonts_link)
        doc = doc.replace("{HIGHLIGHT_JS_CSS}", highlight_js_css)
        doc = doc.replace("{HIGHLIGHT_JS}", highlight_js)
        doc = doc.replace("{MATHJAX}", mathjax)

        if content_css:
            content_css_tag = f"{{CSS_BLOCK}}\n<style id=\"mono-components-content-css\">\n{content_css}\n</style>"
            doc = doc.replace("{CSS_BLOCK}", content_css_tag)

        if asset_store:
            safe_json = json.dumps(asset_store).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
            asset_template = (
                f'<script type="application/json" id="mono-asset-store">{safe_json}</script>'
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

    def extract_title_from_html(self, html_content: str) -> str:
        """
        HTMLから最初の<h1>をタイトルとして抽出

        Args:
            html_content: HTML文字列

        Returns:
            抽出されたタイトル（デフォルト: "Document"）
        """
        match = re.search(r"<h1[^>]*>(.+?)</h1>", html_content)
        if match:
            # HTMLタグを削除
            title = re.sub(r"<[^>]+>", "", match.group(1))
            return title[:60]  # 最大60文字
        return "Document"

    @staticmethod
    def _escape_html(text: str) -> str:
        """HTML特殊文字をエスケープ"""
        # 最適化: C実装の高速な `html.escape` を使用
        # `&#x27;` と `&#39;` の違いはあるが、どちらも有効なアポストロフィのエスケープ
        return html.escape(text, quote=True).replace("&#x27;", "&#39;")

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

        # 最適化: すべての除外タグを1つの正規表現で処理する
        tags_pattern = "|".join(re.escape(tag) for tag in excluded_tags)

        # 自己終了タグ（<hr /> など）
        pattern_self_closing = re.compile(rf"<(?:{tags_pattern})[^>]*/?\s*>", re.IGNORECASE)
        html_content = pattern_self_closing.sub("", html_content)

        # 開閉タグ（<div>...</div> など）
        # 後方参照 (\1) を使って、開始タグと終了タグが一致するようにする
        pattern_paired = re.compile(
            rf"<({tags_pattern})[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL
        )
        html_content = pattern_paired.sub("", html_content)

        self.logger.debug(f"除外タグの一括削除処理を実行: {excluded_tags}")

        return html_content

    def _build_highlight_js_link(self, html_body: str) -> str:
        """Highlight.js のCSSスタイルタグを構築（オフライン・ビルド時）"""
        from src.constants import TEMPLATES_DIR
        import re
        # node_modules から highlight.js のスタイルを読み込む
        # constants.py doesn't have PROJECT_ROOT, but TEMPLATES_DIR is PROJECT_ROOT / "src" / "templates"
        project_root = TEMPLATES_DIR.parent.parent
        highlight_js_dir = project_root / "node_modules" / "highlight.js" / "styles"

        # すべてのテーマを抽出
        themes = set(["atom-one-dark"]) # デフォルトテーマ

        # html_bodyからtheme属性をすべて検索
        matches = re.finditer(r'<mono-code-block[^>]*theme="([^"]*)"', html_body)
        for match in matches:
            if match.group(1):
                themes.add(match.group(1))

        css_blocks = []
        for theme in themes:
            theme_css_file = highlight_js_dir / f"{theme}.css"

            if not theme_css_file.exists():
                # CSSファイルが存在しない場合はフォールバック
                self.logger.warning(f"Highlight.js theme '{theme}' not found. Falling back to default.")
                theme_css_file = highlight_js_dir / "atom-one-dark.css"

            try:
                css = theme_css_file.read_text(encoding="utf-8")

                # スコープを限定する。`.hljs` クラスを `mono-code-block[theme="..."] .hljs` などに置き換える
                # 先頭が `.hljs` で始まるセレクタを置き換える
                import re
                if theme == "atom-one-dark":
                    # デフォルトテーマのスコープ
                    css = re.sub(r'(?<![-a-zA-Z0-9])\.hljs', r'mono-code-block:not([theme]) .hljs, mono-code-block[theme="atom-one-dark"] .hljs', css)
                else:
                    css = re.sub(r'(?<![-a-zA-Z0-9])\.hljs', rf'mono-code-block[theme="{theme}"] .hljs', css)

                css_blocks.append(css)
            except Exception as e:
                self.logger.warning(f"Error loading Highlight.js theme '{theme}': {e}")

        if not css_blocks:
            return ""

        combined_css = "\n".join(css_blocks)
        return f'<style id="mono-highlightjs-css">\n{combined_css}\n</style>'

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

    def _load_highlight_js_script(self) -> str:
        """Highlight.js スクリプトタグは使用しないため空文字を返す"""
        return ""

    def _build_mathjax_script(self) -> str:
        """MathJax は事前レンダリングされるため空文字を返す"""
        return ""

    def _get_used_component_dirs(self, found_mono_tags: set, should_enable_export: bool) -> List[Path]:
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
            if name in found_mono_tags:
                used_dirs.append(component_dir)

        return used_dirs

    def _load_mono_components_script(self, used_component_dirs: List[Path]) -> str:
        """指定されたコンポーネントの script.js を読み込んで <script> タグで返す"""
        if not used_component_dirs:
            return ""

        js_contents = []

        # Base element script
        base_element_script_file = TEMPLATES_DIR / "core" / "mono-base-element.js"
        if base_element_script_file.exists():
            try:
                js_contents.append(base_element_script_file.read_text(encoding="utf-8"))
            except Exception as e:
                self.logger.warning(f"JS読み込みエラー ({base_element_script_file}): {e}")

        # Base interactive element script
        base_script_file = TEMPLATES_DIR / "core" / "mono-interactive-element.js"
        if base_script_file.exists():
            try:
                js_contents.append(base_script_file.read_text(encoding="utf-8"))
            except Exception as e:
                self.logger.warning(f"JS読み込みエラー ({base_script_file}): {e}")

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

    def _load_component_content_css(self, used_component_dirs: List[Path]) -> str:
        """指定されたコンポーネントの content.css を読み込み、結合して返す"""
        if not used_component_dirs:
            return ""

        css_contents = []
        for component_dir in used_component_dirs:
            css_file = component_dir / "content.css"
            if css_file.exists():
                try:
                    css_contents.append(css_file.read_text(encoding="utf-8"))
                except Exception as e:
                    self.logger.warning(
                        f"content.css読み込みエラー ({css_file}): {e}"
                    )

        if not css_contents:
            return ""

        combined_css = "\n\n".join(css_contents)
        return combined_css

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
