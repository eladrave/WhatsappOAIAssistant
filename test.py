from fastapi import FastAPI, Form, HTTPException
from pydantic import BaseModel
import os
import openai
from twilio.rest import Client
from dotenv import load_dotenv
import logging

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

class WhatsAppHandler:
    def __init__(self):
        self.client = twilio_client

    def send_message(self, to, body):
        try:
            message = self.client.messages.create(
                body=body,
                from_='whatsapp:+14155238886',  # Twilio's sandbox number for WhatsApp
                to=to
            )
            return message.sid
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return None

class OpenAIAssistant:
    def __init__(self):
        self.api_key = OPENAI_KEY
        self.api_base = OPENAI_BASE_URL

    def get_response(self, prompt):
        try:
            response = openai.Completion.create(
                model=OPENAI_MODEL,
                prompt=prompt,
                max_tokens=150
            )
            return response.choices[0].text.strip()
        except Exception as e:
            logger.error(f"Error getting response from OpenAI: {e}")
            return "Sorry, something went wrong with the assistant."

class WhatsAppBot:
    def __init__(self):
        self.whatsapp_handler = WhatsAppHandler()
        self.assistant = OpenAIAssistant()

    def handle_message(self, body, from_, to):
        logger.debug(f"Received message from {from_}: {body}")

        try:
            # Get assistant response
            response = self.assistant.get_response(body)

            # Send the response back via WhatsApp using Twilio
            self.whatsapp_handler.send_message(from_, response)

            return {"status": "success"}
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            raise HTTPException(status_code=500, detail=str(e))

app = FastAPI()
bot = WhatsAppBot()

@app.post("/handleMessage")
async def handle_message(Body: str = Form(), From: str = Form(), To: str = Form()):
    return bot.handle_message(Body, From, To)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
