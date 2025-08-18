from tests.conftest import make_signature
from app.openai_client import OpenAIClient


async def fake_chat(self, messages, **options):
    return {"choices": [{"message": {"content": "pong"}}]}


def test_text_message(monkeypatch, client):
    monkeypatch.setattr(OpenAIClient, "chat", fake_chat)
    data = {
        "From": "whatsapp:+15551234567",
        "Body": "ping",
        "NumMedia": "0",
        "MessageSid": "1",
    }
    headers = {
        "X-Twilio-Signature": make_signature(
            "http://testserver/twilio/whatsapp/webhook", data
        )
    }
    resp = client.post("/twilio/whatsapp/webhook", data=data, headers=headers)
    assert resp.status_code == 200
    assert "pong" in resp.text
