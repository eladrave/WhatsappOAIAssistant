import os
import openai
from fastapi import FastAPI, Form, HTTPException
from pydantic import BaseModel
from twilio.rest import Client
from dotenv import load_dotenv
import logging
from openai import OpenAI

from src.modules.WhatsAppHandler import WhatsAppHandler
from src.modules.OpenAIHandler import OpenAIHandler

# Load environment variables from .env file
load_dotenv()

class WhatsAppBot:
    def __init__(self):
        # Load environment variables
        self.OPENAI_KEY = os.getenv('OpenAIKey')
        self.OPENAI_BASE_URL = os.getenv('OpenAIBaseURL')
        self.OPENAI_MODEL = os.getenv('OpenAIModel')
        self.TWILIO_ACCOUNT_SID = os.getenv('TwilioAccountSID')
        self.TWILIO_AUTH_TOKEN = os.getenv('TwilioAuthToken')

        # Set OpenAI configuration
        openai.api_key = self.OPENAI_KEY
        openai.api_base = self.OPENAI_BASE_URL

        assistant_id = os.getenv('OpenAIAssistantId')
        openai_client = OpenAI(api_key=os.environ["OpenAIKey"])

        # Initialize Twilio client
        twilio_client = Client(self.TWILIO_ACCOUNT_SID, self.TWILIO_AUTH_TOKEN)



        # Initialize WhatsAppHanlder
        self.whatsapp_handler = WhatsAppHandler(twilio_client)

        # initialize OpenAIHandler
        self.openai_handler = OpenAIHandler(openai_client, assistant_id)

        # Initialize FastAPI
        self.app = FastAPI()

        # Set up logging
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

        # Define routes
        self.app.post("/handleMessage")(self.handle_message)

    async def handle_message(self, Body: str = Form(), From: str = Form(), To: str = Form()):
        res = await self.openai_handler.query(Body)

        self.whatsapp_handler.send_message(From, To, res[0])
        return {"success": True}

    def run(self, host="0.0.0.0", port=8000):
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)

if __name__ == "__main__":
    bot = WhatsAppBot()
    bot.run()
