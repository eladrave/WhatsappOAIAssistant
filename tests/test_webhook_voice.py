import os
tempfile = __import__('tempfile')

from app.media import MediaItem
from app.openai_client import OpenAIClient
from tests.conftest import make_signature


async def fake_fetch_media(client, url, ctype, settings):
    fd, path = tempfile.mkstemp()
    os.close(fd)
    return MediaItem(url=url, content_type=ctype, path=path, is_voice=True)


async def fake_transcribe(self, path):
    return "transcribed"


async def fake_chat(self, messages, **options):
    assert "transcribed" in messages[-1]["content"]
    return {"choices": [{"message": {"content": "ok"}}]}


def test_voice_note(monkeypatch, client):
    monkeypatch.setattr("app.router_webhook.fetch_media", fake_fetch_media)
    monkeypatch.setattr(OpenAIClient, "transcribe", fake_transcribe)
    monkeypatch.setattr(OpenAIClient, "chat", fake_chat)
    data = {
        "From": "whatsapp:+15551234567",
        "Body": "here",
        "NumMedia": "1",
        "MediaUrl0": "http://example.com/voice.ogg",
        "MediaContentType0": "audio/ogg",
        "MessageSid": "1",
    }
    headers = {"X-Twilio-Signature": make_signature("http://testserver/twilio/whatsapp/webhook", data)}
    resp = client.post("/twilio/whatsapp/webhook", data=data, headers=headers)
    assert resp.status_code == 200
    assert "ok" in resp.text
