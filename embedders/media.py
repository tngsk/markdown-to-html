"""
Media Embedder
==============
Converts media references (Images, Audio) to Base64-encoded data URIs in HTML.
"""

import base64
import logging
import re
from pathlib import Path
from typing import Tuple

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

    def encode_media_to_base64(self, media_path: Path) -> str:
        """メディアファイルをBase64エンコード"""
        if not media_path.exists():
            raise ImageEmbeddingError(f"メディアファイルが見つかりません: {media_path}")

        try:
            media_data = self.file_handler.read_binary(media_path)
            return base64.b64encode(media_data).decode("utf-8")
        except FileProcessingError:
            raise
        except Exception as e:
            raise ImageEmbeddingError(
                f"Base64エンコード失敗 ({media_path}): {e}"
            ) from e

    def embed_media_in_html(
        self, html_content: str, markdown_dir: Path
    ) -> Tuple[str, int]:
        """
        HTMLの<img>タグをBase64埋め込みデータに置換

        Args:
            html_content: 変換対象のHTML文字列
            markdown_dir: Markdownファイルが存在するディレクトリ

        Returns:
            (変換後のHTML, 埋め込み画像数)
        """
        # パターン: <img ...src="..." ... > 形式の画像タグを検索
        pattern = re.compile(HTML_IMG_TAG_PATTERN, re.IGNORECASE)

        image_count = 0

        def replacer(match: re.Match) -> str:
            nonlocal image_count
            before_src = match.group(1)
            src_value = match.group(2)
            after_src = match.group(3)

            # 相対パスを絶対パスに解決
            image_path = (markdown_dir / src_value).resolve()

            if not image_path.exists():
                self.logger.warning(f"画像ファイルが見つかりません: {src_value}")
                return match.group(0)

            try:
                base64_data = self.encode_media_to_base64(image_path)
                mime_type = self.mime_registry.get_mime_type(image_path)
                image_count += 1
                self.logger.debug(f"埋め込み: {image_path.name} ({mime_type})")
                return f'<img {before_src}src="data:{mime_type};base64,{base64_data}"{after_src}>'
            except ImageEmbeddingError as e:
                self.logger.error(f"画像埋め込み失敗: {e}")
                return match.group(0)

        result = pattern.sub(replacer, html_content)
        return result, image_count
