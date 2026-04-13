"""
Media Embedder
==============
Converts media references (Images, Audio) to Base64-encoded data URIs in HTML.
"""

import base64
import io
import logging
import re
from pathlib import Path
from typing import Tuple

from PIL import Image

from config import FileProcessingError, ImageEmbeddingError
from constants import HTML_IMG_TAG_PATTERN
from handlers.file import FileHandler
from handlers.mime import MIMETypeRegistry


class MediaEmbedder:
    """メディアファイル（画像・音声）をBase64エンコードして扱うクラス"""

    def __init__(self, logger: logging.Logger, file_handler: FileHandler):
        self.logger = logger
        self.file_handler = file_handler
        self.mime_registry = MIMETypeRegistry()
        self._base64_cache = {}

    def encode_media_to_base64(self, media_path: Path) -> str:
        """メディアファイルをBase64エンコード"""
        if not media_path.exists():
            raise ImageEmbeddingError(f"メディアファイルが見つかりません: {media_path}")

        cache_key = str(media_path.resolve())
        if cache_key in self._base64_cache:
            return self._base64_cache[cache_key]

        try:
            media_data = self.file_handler.read_binary(media_path)

            ext = media_path.suffix.lower()
            if ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
                try:
                    img = Image.open(io.BytesIO(media_data))
                    buffer = io.BytesIO()
                    img.save(buffer, format="WEBP")
                    media_data = buffer.getvalue()
                except Exception as img_e:
                    self.logger.warning(
                        f"WebP変換失敗 ({media_path}): {img_e}. オリジナルを使用します。"
                    )

            encoded = base64.b64encode(media_data).decode("utf-8")
            self._base64_cache[cache_key] = encoded
            return encoded
        except FileProcessingError:
            raise
        except Exception as e:
            raise ImageEmbeddingError(
                f"Base64エンコード失敗 ({media_path}): {e}"
            ) from e

    def embed_media_in_html(
        self, html_content: str, markdown_dir: Path
    ) -> Tuple[str, int, dict]:
        """
        HTMLの<img>タグおよび<situ-ab-test>のメディアをBase64データに置換

        Args:
            html_content: 変換対象のHTML文字列
            markdown_dir: Markdownファイルが存在するディレクトリ

        Returns:
            (変換後のHTML, 埋め込みメディア数, asset_store)
        """
        media_count = 0
        asset_store = {}

        def resolve_and_encode(src_value: str) -> str:
            nonlocal media_count
            if src_value.startswith(("http://", "https://", "data:")):
                return src_value

            media_path = (markdown_dir / src_value).resolve()
            if not media_path.exists():
                self.logger.warning(f"メディアファイルが見つかりません: {src_value}")
                return src_value

            try:
                if media_path.suffix.lower() == ".svg":
                    svg_content = self.file_handler.read_text(media_path)
                    media_count += 1
                    self.logger.debug(
                        f"インライン埋め込み: {media_path.name} (image/svg+xml)"
                    )
                    return svg_content

                base64_data = self.encode_media_to_base64(media_path)
                mime_type = self.mime_registry.get_mime_type(media_path)
                ext = media_path.suffix.lower()
                if ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
                    mime_type = "image/webp"

                media_count += 1
                self.logger.debug(f"埋め込み: {media_path.name} ({mime_type})")

                asset_id = f"asset-{media_count}"
                asset_store[asset_id] = f"data:{mime_type};base64,{base64_data}"
                return asset_id
            except ImageEmbeddingError as e:
                self.logger.error(f"メディア埋め込み失敗: {e}")
                return src_value

        # 1. <img> タグの処理
        img_pattern = re.compile(HTML_IMG_TAG_PATTERN, re.IGNORECASE)

        def img_replacer(match: re.Match) -> str:
            before_src = match.group(1)
            src_value = match.group(2)
            after_src = match.group(3)

            new_src = resolve_and_encode(src_value)
            stripped_src = new_src.strip()
            if stripped_src.startswith("<svg") or stripped_src.startswith("<?xml"):
                return new_src

            if new_src.startswith("asset-"):
                # transparent 1x1 gif
                placeholder = (
                    "data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs="
                )
                return f'<img {before_src}src="{placeholder}" data-lazy-src="{new_src}"{after_src}>'

            return f'<img {before_src}src="{new_src}"{after_src}>'

        html_content = img_pattern.sub(img_replacer, html_content)

        # 2. <situ-ab-test> タグの処理
        # format: <situ-ab-test title="..." src-a="..." src-b="..."></situ-ab-test>
        ab_test_pattern = re.compile(
            r'(<situ-ab-test\s+[^>]*?src-a=")([^"]+)(".*?src-b=")([^"]+)("[^>]*></situ-ab-test>)',
            re.IGNORECASE,
        )

        def ab_test_replacer(match: re.Match) -> str:
            part1 = match.group(1)
            src_a = match.group(2)
            part3 = match.group(3)
            src_b = match.group(4)
            part5 = match.group(5)

            new_src_a = resolve_and_encode(src_a)
            new_src_b = resolve_and_encode(src_b)

            out_part1 = part1
            if new_src_a.startswith("asset-"):
                out_part1 = part1.replace(
                    'src-a="', 'data-lazy-src-a="' + new_src_a + '" src-a="'
                )

            out_part3 = part3
            if new_src_b.startswith("asset-"):
                out_part3 = part3.replace(
                    'src-b="', 'data-lazy-src-b="' + new_src_b + '" src-b="'
                )

            return f"{out_part1}{new_src_a if not new_src_a.startswith('asset-') else ''}{out_part3}{new_src_b if not new_src_b.startswith('asset-') else ''}{part5}"

        html_content = ab_test_pattern.sub(ab_test_replacer, html_content)

        return html_content, media_count, asset_store
