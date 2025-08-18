"""Twilio request signature verification."""

import base64
import hashlib
import hmac
from typing import Dict

from fastapi import Depends, HTTPException, Request

from .deps import get_settings
from .config import Settings


def _compute_signature(token: str, url: str, params: Dict[str, str]) -> str:
    data = url + "".join(f"{k}{v}" for k, v in sorted(params.items()))
    digest = hmac.new(token.encode(), data.encode(), hashlib.sha1).digest()
    return base64.b64encode(digest).decode()


async def verify_twilio_signature(
    request: Request, settings: Settings = Depends(get_settings)
) -> None:
    signature = request.headers.get("X-Twilio-Signature", "")
    form = dict(await request.form())
    url = str(request.url)
    expected = _compute_signature(settings.twilio_auth_token, url, form)
    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")
