import logging




class WhatsAppHandler:
    def __init__(self, twilio_client):
        self.client = twilio_client

    def send_message(self, to,from_, body):
        try:
            message = self.client.messages.create(
                body=body,
                from_=from_,  # Twilio's sandbox number for WhatsApp
                to=to
            )
            return message.sid
        except Exception as e:
            logging.getLogger().error(f"Error sending WhatsApp message: {e}")
            return None
        

    