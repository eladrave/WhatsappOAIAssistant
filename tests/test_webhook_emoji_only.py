from tests.conftest import make_signature
from app.openai_client import OpenAIClient


async def fail_chat(self, messages, **options):
    raise AssertionError("should not be called")


def test_emoji_only(monkeypatch, client):
    monkeypatch.setattr(OpenAIClient, "chat", fail_chat)
    data = {
        "From": "whatsapp:+15551234567",
        "Body": "👍",
        "NumMedia": "0",
        "MessageSid": "1",
    }
    headers = {"X-Twilio-Signature": make_signature("http://testserver/twilio/whatsapp/webhook", data)}
    resp = client.post("/twilio/whatsapp/webhook", data=data, headers=headers)
    assert resp.status_code == 200
    assert "Body" not in resp.text
