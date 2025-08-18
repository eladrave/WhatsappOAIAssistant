"""Minimal CLI to send a test message to the webhook."""

import argparse
import os
import sys
import hmac
import hashlib
import base64

import httpx


def compute_sig(url: str, params: dict, token: str) -> str:
    data = url + "".join(f"{k}{v}" for k, v in sorted(params.items()))
    digest = hmac.new(token.encode(), data.encode(), hashlib.sha1).digest()
    return base64.b64encode(digest).decode()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("text", help="Message body to send")
    parser.add_argument("--from-number", default="whatsapp:+15551234567")
    parser.add_argument("--url", default="http://localhost:8080/twilio/whatsapp/webhook")
    args = parser.parse_args()

    data = {
        "From": args.from_number,
        "Body": args.text,
        "NumMedia": "0",
        "MessageSid": "CLITEST",
    }
    token = os.environ.get("TWILIO_AUTH_TOKEN", "test")
    sig = compute_sig(args.url, data, token)
    headers = {"X-Twilio-Signature": sig}
    resp = httpx.post(args.url, data=data, headers=headers)
    print(resp.text)


if __name__ == "__main__":
    main()
