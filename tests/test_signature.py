from tests.conftest import make_signature


def test_invalid_signature(client):
    data = {
        "From": "whatsapp:+15551234567",
        "Body": "hi",
        "NumMedia": "0",
        "MessageSid": "1",
    }
    headers = {"X-Twilio-Signature": "bad"}
    resp = client.post("/twilio/whatsapp/webhook", data=data, headers=headers)
    assert resp.status_code == 403


def test_valid_signature(client):
    data = {
        "From": "whatsapp:+15551234567",
        "Body": "hi",
        "NumMedia": "0",
        "MessageSid": "1",
    }
    url = "http://testserver/twilio/whatsapp/webhook"
    headers = {"X-Twilio-Signature": make_signature(url, data)}
    resp = client.post("/twilio/whatsapp/webhook", data=data, headers=headers)
    assert resp.status_code == 200
