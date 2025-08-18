"""OpenAI API client wrappers."""

from __future__ import annotations

from typing import Any, Dict, List

import httpx

from .config import Settings


class OpenAIClient:
    def __init__(self, client: httpx.AsyncClient, settings: Settings) -> None:
        self.client = client
        self.settings = settings

    def _headers(self) -> Dict[str, str]:
        headers = {"Authorization": f"Bearer {self.settings.openai_api_key}"}
        if self.settings.openai_org_id:
            headers["OpenAI-Organization"] = self.settings.openai_org_id
        if self.settings.openai_project_id:
            headers["OpenAI-Project"] = self.settings.openai_project_id
        return headers

    async def chat(self, messages: List[Dict[str, Any]], **options: Any) -> Dict[str, Any]:
        url = f"{self.settings.openai_base_url}/chat/completions"
        payload: Dict[str, Any] = {
            "model": self.settings.openai_model,
            "messages": messages,
        }
        payload.update(self.settings.openai_default_options_json)
        payload.update(options)
        resp = await self.client.post(url, json=payload, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    async def transcribe(self, file_path: str) -> str:
        url = f"{self.settings.openai_base_url}/audio/transcriptions"
        with open(file_path, "rb") as f:
            files = {"file": (file_path, f, "application/octet-stream"), "model": (None, self.settings.openai_transcribe_model)}
            resp = await self.client.post(url, files=files, headers=self._headers())
        resp.raise_for_status()
        data = resp.json()
        return data.get("text", "")
