from fastapi import APIRouter, Depends, Request, Response

from .deps import get_openai_client, get_settings
from .emoji_filter import is_emoji_only
from .media import fetch_media
from .openai_client import OpenAIClient
from .twilio_verify import verify_twilio_signature
from .utils import build_messages, build_twiml, chunk_text

router = APIRouter()


@router.post("/twilio/whatsapp/webhook", dependencies=[Depends(verify_twilio_signature)])
async def whatsapp_webhook(
    request: Request,
    settings=Depends(get_settings),
    openai: OpenAIClient = Depends(get_openai_client),
) -> Response:
    form = await request.form()
    from_number = str(form.get("From", ""))
    body = str(form.get("Body", ""))
    num_media = int(form.get("NumMedia", "0"))

    from_number = from_number.replace("whatsapp:", "")
    if settings.allowed_senders and from_number not in settings.allowed_senders:
        return Response(content=build_twiml([]), media_type="application/xml")

    if num_media == 0 and is_emoji_only(body):
        return Response(content=build_twiml([]), media_type="application/xml")

    media_parts = []
    transcript = ""
    for i in range(num_media):
        url = str(form.get(f"MediaUrl{i}"))
        ctype = str(form.get(f"MediaContentType{i}"))
        item = await fetch_media(request.app.state.http_client, url, ctype, settings)
        if item.is_voice:
            try:
                transcript = await openai.transcribe(item.path)
            except Exception:
                transcript = ""
        elif ctype.startswith("image/"):
            media_parts.append({"type": "image_url", "image_url": {"url": url}})
        else:
            media_parts.append({"type": "text", "text": f"Attached file: {url}"})

    text = body.strip()
    if transcript:
        text += f"\n\n[Voice note transcript]: {transcript}"

    messages = build_messages(settings.system_prompt, text, media_parts)

    try:
        result = await openai.chat(messages)
        reply = result["choices"][0]["message"]["content"]
    except Exception:
        reply = "Sorry, there was a temporary problem. Please try again."

    twiml = build_twiml(chunk_text(reply))
    return Response(content=twiml, media_type="application/xml")
