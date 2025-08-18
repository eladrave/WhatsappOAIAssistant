from functools import lru_cache

from fastapi import Depends, Request
import httpx

from .config import Settings, load_settings
from .openai_client import OpenAIClient


def get_settings() -> Settings:
    return load_settings()


def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client


def get_openai_client(
    settings: Settings = Depends(get_settings),
    client: httpx.AsyncClient = Depends(get_http_client),
) -> OpenAIClient:
    return OpenAIClient(client, settings)
