"""Simple environment-based configuration loader."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Settings:
    app_env: str = os.getenv("APP_ENV", "dev")
    port: int = int(os.getenv("PORT", "8080"))

    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    openai_org_id: Optional[str] = os.getenv("OPENAI_ORG_ID")
    openai_project_id: Optional[str] = os.getenv("OPENAI_PROJECT_ID")
    openai_default_options_json: dict = field(
        default_factory=lambda: json.loads(os.getenv("OPENAI_DEFAULT_OPTIONS_JSON", "{}"))
    )
    openai_transcribe_model: str = os.getenv("OPENAI_TRANSCRIBE_MODEL", "whisper-1")

    twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    allowed_senders: List[str] = field(
        default_factory=lambda: [s.strip() for s in os.getenv("ALLOWED_SENDERS", "").split(",") if s.strip()]
    )

    system_prompt: Optional[str] = os.getenv("SYSTEM_PROMPT")
    media_download_timeout_sec: int = int(os.getenv("MEDIA_DOWNLOAD_TIMEOUT_SEC", "10"))
    media_max_bytes: int = int(os.getenv("MEDIA_MAX_BYTES", "15000000"))
    reply_with_media: bool = os.getenv("REPLY_WITH_MEDIA", "false").lower() == "true"
    config_file: Optional[str] = os.getenv("CONFIG_FILE")


def load_settings() -> Settings:
    return Settings()
