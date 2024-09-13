import os
from dotenv import load_dotenv
import logging
import uvicorn
from fastapi import FastAPI,  Request
from twilio.rest import Client as TwilioClient

import requests

from .modules.WhatsAppHandler import WhatsAppHandler
from .modules.WhatsAppHandler.WhatsappRequest import WhatsappRequest



logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


# Load environment variables from .env file
load_dotenv()




def initialize_whatsapp_handler():
    

    # Load environment variables
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

    # Initialize Twilio client
    twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    whatsapp_handler = WhatsAppHandler(twilio_client)


    return whatsapp_handler

if __name__ == '__main__':
    whatsapp_hdndler = initialize_whatsapp_handler()

    app = FastAPI()

    # add bot heartbeat route to FastAPI
    @app.get("/")
    async def heartbeat():
        return {"success": True}

    # add bot message handling route to FastAPI
    @app.post("/handleMessage")
    async def handle_message(request: WhatsappRequest):
        print("Request:", request)
        
        data = {
            "prompt": request.Body,
            "phone_number": request.From
        }

        url = "http://localhost:8080/handleMessage"
        response = requests.post(url, json=data)

        if response.status_code != 200:
            return {"success": False}
        else:
            print("Response:", response.json())


        return {"success": True}

    host = os.getenv('HOST', '0.0.0.0')
    port = 8081

    uvicorn.run(app, host=host, port=port)


