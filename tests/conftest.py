import base64
import hmac
import hashlib
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

os.environ.setdefault("OPENAI_API_KEY", "test")
os.environ.setdefault("TWILIO_AUTH_TOKEN", "token")
os.environ.setdefault("ALLOWED_SENDERS", "+15551234567")

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def make_signature(url: str, params: dict, token: str = "token") -> str:
    data = url + "".join(f"{k}{v}" for k, v in sorted(params.items()))
    digest = hmac.new(token.encode(), data.encode(), hashlib.sha1).digest()
    return base64.b64encode(digest).decode()
