from fastapi import FastAPI, Form, HTTPException, Request, status
import logging



class WhatsAppHandler:
    def __init__(self, twilio_client):
        self.client = twilio_client

    async def process_request(self, request: Request):
        try:
            # Access form data
            form_data = await request.form()
            message_data = form_data.multi_items()

            # Log all information from the request
            print("Received Message Data:")
            for key, value in message_data:
                print(f"{key}: {value}")

            Body = form_data.get('Body')
            From = form_data.get('From')
            To = form_data.get('To')

            return From, To, Body, form_data
        except Exception as e:
            logging.getLogger().error(f"Error processing WhatsApp request: {e}")
            return None, None, None

    def send_message(self, to, from_, body):
        try:
            texts = [body[i:i+1500] for i in range(0, len(body), 1500)]
            messages_ids = []

            for text in texts:
                message = self.client.messages.create(
                    body=text,
                    from_=from_,  # Twilio's sandbox number for WhatsApp
                    to=to
                )
                messages_ids.append(message.sid)
            return messages_ids
        except Exception as e:
            logging.getLogger().error(f"Error sending WhatsApp message: {e}")
            return None



