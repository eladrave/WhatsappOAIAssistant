from fastapi import FastAPI, Form, HTTPException
from pydantic import BaseModel
import os
import openai
import httpx
from twilio.rest import Client
from dotenv import load_dotenv
import asyncio
import logging

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
OPENAI_KEY = os.getenv('OpenAIKey')
OPENAI_BASE_URL = os.getenv('OpenAIBaseURL')
OPENAI_MODEL = os.getenv('OpenAIModel')
OPENAI_ASSISTANT_ID = os.getenv('OpenAIAssistantId')
TWILIO_ACCOUNT_SID = os.getenv('TwilioAccountSID')
TWILIO_AUTH_TOKEN = os.getenv('TwilioAuthToken')

openai.api_key = OPENAI_KEY
openai.api_base = OPENAI_BASE_URL

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

class TwilioMessage(BaseModel):
    Body: str
    From: str
    To: str

@app.post("/handleMessage")
async def handle_message(Body: str = Form(), From: str = Form(), To: str = Form()):
    logger.debug(f"Received message from {From}: {Body}")

    try:
        # Retrieve the assistant
        client = openai.Client(api_key=OPENAI_KEY)
        my_assistant = client.beta.assistants.retrieve(OPENAI_ASSISTANT_ID)

        # Create a thread
        my_thread = client.beta.threads.create()
        logger.debug(f"Created thread: {my_thread}")

        # Add a message to the thread
        my_thread_message = client.beta.threads.messages.create(
            thread_id=my_thread.id,
            role="user",
            content=Body
        )
        logger.debug(f"Added message to thread: {my_thread_message}")

        # Run the assistant
        my_run = client.beta.threads.runs.create(
            thread_id=my_thread.id,
            assistant_id=my_assistant.id,
        )
        logger.debug(f"Started assistant run: {my_run}")

        # Retrieve the run status and result
        while True:
            retrieve_run = client.beta.threads.runs.retrieve(
                thread_id=my_thread.id,
                run_id=my_run.id
            )
            logger.debug(f"Run status: {retrieve_run.status}")

            if retrieve_run.status == "completed":
                break
            elif retrieve_run.status in ["queued", "in_progress"]:
                await asyncio.sleep(1)
            else:
                raise Exception(f"Run failed with status: {retrieve_run.status}")

        # Retrieve the assistant's response
        all_messages = client.beta.threads.messages.list(thread_id=my_thread.id)
        #allMessages.data[0].content[0].text.value
        assistant_response = all_messages.data[0].content[0].text.value
        logger.debug(f"Assistant response: {assistant_response}")

        # Send the response back via WhatsApp using Twilio
        send_whatsapp_message(To, From, assistant_response)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def send_whatsapp_message(From: str, to: str, body: str):
    print(f"Sending message from {From} to {to}: {body}")
    from_whatsapp_number = f'{From}'
    to_whatsapp_number = f'{to}'

    message = twilio_client.messages.create(
        body=body,
        from_=from_whatsapp_number,
        to=to_whatsapp_number
    )
    return message.sid

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)