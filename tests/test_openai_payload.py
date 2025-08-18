import asyncio
import httpx

from app.config import Settings
from app.openai_client import OpenAIClient
from app.utils import build_messages


def test_build_messages_text():
    msgs = build_messages("sys", "hi", [])
    assert msgs[0]["role"] == "system"
    assert msgs[1]["content"] == "hi"


def test_build_messages_image():
    msgs = build_messages(None, "hi", [{"type": "image_url", "image_url": {"url": "u"}}])
    assert isinstance(msgs[0]["content"], list)
def test_openai_options_merge(monkeypatch):
    async def run():
        settings = Settings(
            openai_api_key="k",
            twilio_auth_token="t",
            allowed_senders=["+1"],
            openai_default_options_json={"temperature": 0.2},
        )
        async with httpx.AsyncClient() as client:
            api = OpenAIClient(client, settings)

            class DummyResp:
                def raise_for_status(self):
                    pass

                def json(self):
                    return {"choices": [{"message": {"content": "ok"}}]}

            async def fake_post(url, json, headers):
                assert json["temperature"] == 0.2
                return DummyResp()

            monkeypatch.setattr(client, "post", fake_post)
            resp = await api.chat([{"role": "user", "content": "hi"}])
            assert resp["choices"][0]["message"]["content"] == "ok"

    asyncio.run(run())
