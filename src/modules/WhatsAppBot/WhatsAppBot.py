import os
import logging
from fastapi import FastAPI, Form, HTTPException
from twilio.rest import Client
import openai
from openai import OpenAI



from ..WhatsAppHandler import WhatsAppHandler
from ..OpenAIHandler import OpenAIHandler


class WhatsAppBot:
    def __init__(self):
        self._load_environment_variables()
        self._configure_openai()
        self._initialize_clients()
        self._initialize_handlers()
        self._setup_logging()
        self._initialize_app()
        self._define_routes()

    def _load_environment_variables(self):
        self.OPENAI_KEY = os.getenv('OpenAIKey')
        self.OPENAI_BASE_URL = os.getenv('OpenAIBaseURL')
        self.OPENAI_MODEL = os.getenv('OpenAIModel')
        self.TWILIO_ACCOUNT_SID = os.getenv('TwilioAccountSID')
        self.TWILIO_AUTH_TOKEN = os.getenv('TwilioAuthToken')
        self.assistant_id = os.getenv('OpenAIAssistantId')

    def _configure_openai(self):
        openai.api_key = self.OPENAI_KEY
        openai.api_base = self.OPENAI_BASE_URL
        self.openai_client = OpenAI(api_key=self.OPENAI_KEY)

    def _initialize_clients(self):
        self.twilio_client = Client(self.TWILIO_ACCOUNT_SID, self.TWILIO_AUTH_TOKEN)

    def _initialize_handlers(self):
        self.whatsapp_handler = WhatsAppHandler(self.twilio_client)
        self.openai_handler = OpenAIHandler(self.openai_client, self.assistant_id)

    def _setup_logging(self):
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

    def _initialize_app(self):
        self.app = FastAPI()

    def _define_routes(self):
        self.app.post("/handleMessage")(self.handle_message)

    async def handle_message(self, Body: str = Form(), From: str = Form(), To: str = Form()):
        try:
            res = await self.openai_handler.query(Body)
            self.whatsapp_handler.send_message(From, To, res[0])
            return {"success": True}
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def run(self, host="0.0.0.0", port=8000):
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)


__all__ = ['WhatsAppBot']
