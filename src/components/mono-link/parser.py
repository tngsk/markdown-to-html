import re
import urllib.request
import urllib.parse
import base64
import hashlib
import json
import logging
from html.parser import HTMLParser
from pathlib import Path
from src.processors.base_parser import BaseComponentParser

logger = logging.getLogger(__name__)

class MetadataParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.values = {}
        self.title = ""
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "meta":
            key = attrs_dict.get("property", attrs_dict.get("name", "")).lower().strip()
            if key and "content" in attrs_dict:
                self.values.setdefault(key, attrs_dict["content"])
        elif tag == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, value):
        if self.in_title:
            self.title += value

class Parser(BaseComponentParser):
    # OPTIONS: url: "url", style: "full|small|card"
    PATTERN = r"@\[link(?:(?:\:\s*)?([^\]]*))\](?:\(((?:[^()]*|\([^()]*\))*)\))?(?:\{([^}]*)\})?"
    FAST_PATH_MARKERS = ("@[link",)
    _memory_cache = {}

    @property
    def block_level_tags(self) -> list[str]:
        return []

    def safe_encode_url(self, url: str) -> str:
        """Encode URL properly handling non-ASCII characters without double encoding"""
        try:
            url.encode('ascii')
            return url
        except UnicodeEncodeError:
            from urllib.parse import urlsplit, urlunsplit, quote, unquote
            scheme, netloc, path, query, fragment = urlsplit(url)
            path = quote(unquote(path))
            query = quote(unquote(query), safe='=&')
            fragment = quote(unquote(fragment))
            return urlunsplit((scheme, netloc, path, query, fragment))

    def _get_cache_dir(self) -> Path:
        cache_dir = Path.cwd() / ".mono-cache"
        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        return cache_dir

    def download_resource(self, url: str, limit: int, timeout: int = 8) -> tuple[bytes, str, str, str]:
        parts = urllib.parse.urlsplit(url)
        if parts.scheme not in ("http", "https") or not parts.hostname or any(ord(c) < 33 for c in url):
            raise ValueError(f"不正なURL形式です: {url}")

        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MonoDoc/1.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            final_url = response.url
            data = response.read(limit + 1)
            if len(data) > limit:
                raise ValueError("プレビュー取得サイズが上限を超過しました")
            content_type = response.headers.get_content_type()
            charset = response.headers.get_content_charset() or "utf-8"
            return data, content_type, charset, final_url

    def fetch_og_data(self, url: str) -> dict:
        """Fetch OpenGraph metadata and image from URL with caching and size limits"""
        data = {
            "title": "",
            "desc": "",
            "image": ""
        }

        if not url.startswith("http://") and not url.startswith("https://"):
            return data

        if url in self._memory_cache:
            return self._memory_cache[url]

        cache_dir = self._get_cache_dir()
        url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()
        cache_file = cache_dir / f"{url_hash}.json"

        if cache_file.is_file():
            try:
                cached_data = json.loads(cache_file.read_text(encoding="utf-8"))
                self._memory_cache[url] = cached_data
                return cached_data
            except (OSError, ValueError):
                pass

        try:
            safe_url = self.safe_encode_url(url)
            raw_html, content_type, charset, final_url = self.download_resource(safe_url, limit=2_000_000)
            if content_type not in ("text/html", "application/xhtml+xml"):
                return data

            html_text = raw_html.decode(charset, errors="replace")
            meta_parser = MetadataParser()
            meta_parser.feed(html_text)

            title = meta_parser.values.get("og:title") or meta_parser.title.strip()
            desc = meta_parser.values.get("og:description") or meta_parser.values.get("description", "")
            data["title"] = title.strip()
            data["desc"] = desc.replace("\n", " ").strip()

            img_url = meta_parser.values.get("og:image")
            if img_url:
                absolute_img_url = urllib.parse.urljoin(final_url, img_url.strip())
                try:
                    img_data, img_mime, _, _ = self.download_resource(absolute_img_url, limit=8_000_000)
                    if img_mime in ("image/png", "image/jpeg", "image/webp", "image/gif", "image/svg+xml"):
                        b64 = base64.b64encode(img_data).decode("utf-8")
                        data["image"] = f"data:{img_mime};base64,{b64}"
                except Exception as img_err:
                    logger.debug(f"OGP画像の取得をスキップしました ({absolute_img_url}): {img_err}")

            if cache_dir.exists():
                try:
                    cache_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
                except OSError:
                    pass

        except Exception as e:
            logger.warning(f"Failed to fetch OpenGraph data for {url}: {e}")

        self._memory_cache[url] = data
        return data

    def process(self, markdown_content: str) -> str:
        if "@[link" not in markdown_content:
            return markdown_content

        pattern = re.compile(self.PATTERN)

        def replacer(match: re.Match) -> str:
            bracket_content = match.group(1) or ""
            args_str = match.group(2) or ""
            trailing_str = match.group(3) or ""

            label, specific_args = self.parse_bracket_content(bracket_content)
            common_args = self.parse_key_value_args(args_str)
            args = {**specific_args, **common_args}
            args = self.merge_trailing_attrs(args, trailing_str)

            # Support both `@[link: "url"]` and `@[link](url="url")`
            url, text_label = self.resolve_url_and_label(label, args, ['url'], 'text')
            url = url.strip('\'"')
            # Default style is full
            style = args.get('style', 'full')

            # Fetch metadata
            og_data = self.fetch_og_data(url)

            # Determine title: explicit label/text > title arg > OGP title > url
            title = text_label or args.get('title') or og_data['title'] or url

            # We must escape HTML safely
            safe_url = self.escape_html(url)
            safe_title = self.escape_html(title)
            safe_desc = self.escape_html(og_data['desc'])

            # The base64 data shouldn't strictly need escaping but it's safe to do so
            safe_img = self.escape_html(og_data['image'])
            safe_style = self.escape_html(style)

            common_attrs = self.get_common_attributes(args)

            return (f'<mono-link url="{safe_url}" title="{safe_title}" desc="{safe_desc}" '
                    f'image="{safe_img}" card-style="{safe_style}"{common_attrs}></mono-link>')

        return pattern.sub(replacer, markdown_content)
