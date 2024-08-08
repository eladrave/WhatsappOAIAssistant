import os
from dotenv import load_dotenv
import openai
import logging
import uvicorn


from .modules.WhatsAppBot import WhatsAppBot
from .modules.DBClient import DBClient
from .modules.WhatsAppHandler import WhatsAppHandler
from .modules.OpenAIHandler import OpenAIHandler
from .modules.AudioTranscriber import AudioTranscriber

from twilio.rest import Client as TwilioClient

from fastapi import FastAPI, Form, HTTPException, Request, status


logging.basicConfig(level=logging.DEBUG)

# Load environment variables from .env file
load_dotenv()


def initialize_bot():
    db_client = DBClient(
        os.getenv('DBName'),
        os.getenv('DBUser'),
        os.getenv('DBPassword'),
        os.getenv('DBHost'),
        os.getenv('DBPort', '5432')
    )

    # Get config from DB
    config = db_client.read_config()
    TWILIO_ACCOUNT_SID = config['TwilioAccountSID']
    TWILIO_AUTH_TOKEN = config['TwilioAuthToken']

    # Initialize Twilio client
    twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    openai.api_base = config['OpenAIBaseURL']

    whatsapp_handler = WhatsAppHandler(twilio_client)
    openai_handler = OpenAIHandler()
    audio_transcriber = AudioTranscriber()

    logger = logging.getLogger(__name__)

    bot = WhatsAppBot(db_client, whatsapp_handler, openai_handler, audio_transcriber, logger)
    return bot



if __name__ == '__main__':
    bot = initialize_bot()

    app = FastAPI()

    # add bot heartbeat route to FastAPI
    @app.get("/heartbeat")
    async def heartbeat():
        return await bot.heartbeat()

    # add bot message handling route to FastAPI
    @app.post("/handleMessage")
    async def handle_message(request: Request):
        return await bot.handle_message(request)

    host = os.getenv('HOST', '0.0.0.0')
    port = os.getenv('PORT', 8080)

    uvicorn.run(app, host=host, port=port)


