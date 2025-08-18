# WhatsApp OpenAI Handler

A FastAPI service that receives inbound WhatsApp messages from Twilio and
forwards them to an OpenAI compatible Chat Completions API. The model response
is returned to the user via Twilio using TwiML.

## Features

* Validates Twilio signatures and allowed senders
* Filters out emoji reactions
* Downloads media and transcribes voice notes
* Forwards text and media to any OpenAI compatible endpoint
* Responds with TwiML messages

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env  # edit with your keys
uvicorn app.main:app --reload
```

Send a test message:

```bash
python cli.py "Hello" --from-number whatsapp:+15551234567
```

## Docker

```bash
docker build -t whatsapp-openai-handler .
docker compose up
```

## Environment

Configuration is via environment variables; see `.env.example` for options. An
optional `CONFIG_FILE` may point at a YAML file for per-sender overrides
(similar to `config.example.yaml`).

## Testing

```bash
pytest
```

## Twilio configuration

1. Configure a WhatsApp sender in Twilio and connect it to a Messaging Service.
2. Set the inbound webhook URL to `https://your-host/twilio/whatsapp/webhook`.
3. Set `TWILIO_AUTH_TOKEN` and `ALLOWED_SENDERS` in the environment.
4. Send a WhatsApp message to test.
