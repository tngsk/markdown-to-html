import re
import urllib.request
import base64
import logging
from src.processors.base_parser import BaseComponentParser

logger = logging.getLogger(__name__)

class Parser(BaseComponentParser):
    # OPTIONS: url: "url", style: "full|small|card"
    PATTERN = r"@\[link(?:(?:\:\s*)?([^\]]*))\](?:\(((?:[^()]*|\([^()]*\))*)\))?(?:\{([^}]*)\})?"
    FAST_PATH_MARKERS = ("@[link",)

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

    def fetch_og_data(self, url: str) -> dict:
        """Fetch OpenGraph metadata and image from URL"""
        data = {
            "title": "",
            "desc": "",
            "image": ""
        }

        if not url.startswith("http://") and not url.startswith("https://"):
            return data

        try:
            safe_url = self.safe_encode_url(url)
            req = urllib.request.Request(safe_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
            html = urllib.request.urlopen(req, timeout=5).read().decode('utf-8', errors='ignore')

            # Extract og:image
            image_match = re.search(r'<meta\s+property=[\"\'\s]?og:image[\"\'\s]?\s+content=[\"\'\s]?([^\"\'>\s]+)', html, re.IGNORECASE)
            # Extract og:title
            title_match = re.search(r'<meta\s+property=[\"\'\s]?og:title[\"\'\s]?\s+content=[\"\'\s]?([^\"\'>]+)', html, re.IGNORECASE)
            if not title_match:
                title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
            # Extract og:description
            desc_match = re.search(r'<meta\s+property=[\"\'\s]?og:description[\"\'\s]?\s+content=[\"\'\s]?([^\"\'>]+)', html, re.IGNORECASE)

            if title_match:
                data["title"] = title_match.group(1).strip()
            if desc_match:
                # Remove newlines to prevent markdown from splitting the tag
                data["desc"] = desc_match.group(1).replace('\n', ' ').strip()

            if image_match:
                img_url = image_match.group(1).strip()
                # Ensure img_url is absolute
                from urllib.parse import urljoin
                img_url = urljoin(url, img_url)

                # Fetch image and convert to base64
                img_req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
                img_response = urllib.request.urlopen(img_req, timeout=5)
                img_data = img_response.read()
                content_type = img_response.headers.get('Content-Type', 'image/jpeg')
                b64 = base64.b64encode(img_data).decode('utf-8')
                data["image"] = f"data:{content_type};base64,{b64}"

        except Exception as e:
            logger.warning(f"Failed to fetch OpenGraph data for {url}: {e}")

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
