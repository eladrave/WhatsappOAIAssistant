"""Media downloading and classification utilities."""

from dataclasses import dataclass
import mimetypes
import os
import tempfile
from typing import Optional

import httpx

from .config import Settings


VOICE_TYPES = {"audio/ogg", "audio/amr", "audio/mpeg", "audio/mp4"}


@dataclass
class MediaItem:
    url: str
    content_type: str
    path: str
    is_voice: bool


async def fetch_media(
    client: httpx.AsyncClient, url: str, content_type: str, settings: Settings
) -> MediaItem:
    """Download media to a temporary file and classify it."""
    resp = await client.get(url, timeout=settings.media_download_timeout_sec)
    resp.raise_for_status()
    size = int(resp.headers.get("content-length", 0))
    if size and size > settings.media_max_bytes:
        raise ValueError("media too large")
    suffix = mimetypes.guess_extension(content_type) or ""
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "wb") as f:
        f.write(resp.content)
    is_voice = content_type in VOICE_TYPES
    return MediaItem(url=url, content_type=content_type, path=path, is_voice=is_voice)
