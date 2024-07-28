
# whatsapp_handler.py
from twilio.rest import Client
import logging
from app.config import Config

logger = logging.getLogger(__name__)

class WhatsAppHandler:
    def __init__(self):
        self.client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        self.from_whatsapp_number = f"whatsapp:{Config.TWILIO_WHATSAPP_NUMBER}"

    def send_message(self, to, body):
        try:
            message = self.client.messages.create(
                body=body,
                from_=self.from_whatsapp_number,
                to=f"whatsapp:{to}"
            )
            return message.sid
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return None

    def receive_message(self, body, from_, to):
        logger.debug(f"Received message from {from_}: {body}")
        return body, from_, to
