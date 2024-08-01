from fastapi import FastAPI, Form, HTTPException
from pydantic import BaseModel
import os
import openai
from twilio.rest import Client
from dotenv import load_dotenv
import logging

from src.modules.WhatsAppHandler.WhatsAppHandler import WhatsAppHandler


# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
OPENAI_KEY = os.getenv('OpenAIKey')
OPENAI_BASE_URL = os.getenv('OpenAIBaseURL')
OPENAI_MODEL = os.getenv('OpenAIModel')
TWILIO_ACCOUNT_SID = os.getenv('TwilioAccountSID')
TWILIO_AUTH_TOKEN = os.getenv('TwilioAuthToken')

# Set OpenAI configuration
openai.api_key = OPENAI_KEY
openai.api_base = OPENAI_BASE_URL

# Initialize Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)





app = FastAPI()



@app.post("/handleMessage")
async def handle_message(Body: str = Form(), From: str = Form(), To: str = Form()):
    whatsapp_handler = WhatsAppHandler(twilio_client)    
    whatsapp_handler.send_message(From, To, Body)
    return {"success": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
