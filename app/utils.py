"""Miscellaneous helpers."""

from typing import Iterable, List
from xml.etree.ElementTree import Element, SubElement, tostring


def chunk_text(text: str, limit: int = 1500) -> List[str]:
    return [text[i : i + limit] for i in range(0, len(text), limit)] or [""]


def build_twiml(messages: Iterable[str], media_url: str | None = None) -> str:
    root = Element("Response")
    for m in messages:
        msg = SubElement(root, "Message")
        body = SubElement(msg, "Body")
        body.text = m
        if media_url:
            media = SubElement(msg, "Media")
            media.text = media_url
    return tostring(root, encoding="unicode")


def build_messages(system_prompt: str | None, user_text: str, media_parts: list) -> list:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if media_parts:
        parts = [{"type": "text", "text": user_text}] if user_text else []
        parts.extend(media_parts)
        messages.append({"role": "user", "content": parts})
    else:
        messages.append({"role": "user", "content": user_text})
    return messages
