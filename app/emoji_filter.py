"""Utility for filtering messages that contain only emoji characters."""

import re
from typing import Pattern

# Quick ASCII guard to skip regex when clear text is present
ASCII_RE: Pattern[str] = re.compile(r"[A-Za-z0-9]")

# Simplistic emoji only regex covering the basic emoticon ranges.
EMOJI_ONLY_RE: Pattern[str] = re.compile(
    r"^[\u2600-\u26FF\u2700-\u27BF\U0001F300-\U0001FAFF]+$"
)


def is_emoji_only(text: str) -> bool:
    """Return ``True`` if ``text`` consists solely of emoji characters."""
    if not text:
        return False
    if ASCII_RE.search(text):
        return False
    stripped = text.strip()
    if not stripped:
        return False
    return bool(EMOJI_ONLY_RE.fullmatch(stripped))
