"""Lightweight data models used across the application."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ChatMessage:
    role: str
    content: str | list


@dataclass
class ChatRequest:
    model: str
    messages: List[ChatMessage]
    options: dict
