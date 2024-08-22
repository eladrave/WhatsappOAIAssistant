import os
from dotenv import load_dotenv
import openai
import logging
import uvicorn
from fastapi import FastAPI, Form, HTTPException, Request, status
from twilio.rest import Client as TwilioClient

from mem0 import Memory


from .modules.WhatsAppBot import WhatsAppBot
from .modules.DBClient import DBClient
from .modules.WhatsAppHandler import WhatsAppHandler
from .modules.OpenAIHandler import OpenAIHandler
from .modules.AudioTranscriber import AudioTranscriber
from .modules.SessionManager import SessionManager
from .modules.SessionBuilder import SessionBuilder
from .modules.SessionFactory import SessionFactory

from .modules.ToolManager import ToolManager
from .modules.Tool.RetrieveMemory import RetrieveMemory
from .modules.Tool.SaveMemory import SaveMemory
from .modules.Tool.WebSearch import WebSearch




logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


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

    tool_manager = ToolManager()

    tool_manager.register_tool(RetrieveMemory())
    tool_manager.register_tool(SaveMemory())
    tool_manager.register_tool(WebSearch())

    whatsapp_handler = WhatsAppHandler(twilio_client)
    openai_handler = OpenAIHandler(tool_manager)
    audio_transcriber = AudioTranscriber()
    session_manager = SessionManager()
    session_factory = SessionFactory(SessionBuilder())

    logger = logging.getLogger(__name__)

    bot = WhatsAppBot(db_client, 
                      whatsapp_handler, 
                      openai_handler, 
                      audio_transcriber, 
                      session_manager, 
                      session_factory, 
                      logger)
    return bot



if __name__ == '__main__':
    bot = initialize_bot()

    app = FastAPI()

    # add bot heartbeat route to FastAPI
    @app.get("/")
    async def heartbeat():
        return await bot.heartbeat()

    # add bot message handling route to FastAPI
    @app.post("/handleMessage")
    async def handle_message(request: Request):
        return await bot.handle_message(request)

    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '8080'))

    uvicorn.run(app, host=host, port=port)


