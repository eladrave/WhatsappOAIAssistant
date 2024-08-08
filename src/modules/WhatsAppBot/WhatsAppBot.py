from fastapi import FastAPI, Form, HTTPException, Request, status
import logging
import os
import openai

from ..WhatsAppHandler import WhatsAppHandler
from ..OpenAIHandler import OpenAIHandler
from ..DBClient import DBClient

from ..AudioTranscriber import AudioTranscriber


class WhatsAppBot:
    def __init__(self, db_client, whatsapp_handler, openai_handler, audio_transcriber, logger):
        self.db_client = db_client
        self.whatsapp_handler = whatsapp_handler
        self.openai_handler = openai_handler
        self.audio_transcriber = audio_transcriber
        self.logger = logger



    # For cloud
    async def heartbeat(self):
        return {'success': True}

    async def handle_message(self, request: Request):
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

            # Is the user is not registered, we should not respond
            if not self.db_client.check_user_exists(From):
                return {"success": True}


            user = self.db_client.get_user(From) # Get user by phone number
            
            NumMedia = form_data.get('NumMedia')
            for i in range(int(NumMedia)):
                media_url = form_data.get(f'MediaUrl{i}')
                media_content_type = form_data.get(f'MediaContentType{i}')
                
                if media_content_type.startswith('audio/ogg'):
                    self.audio_transcriber.download_audio_file(media_url, 'audio.ogg')
                    transcribed_text = self.audio_transcriber.transcribe_audio(user['openai_api_key'], 'audio.ogg')
                    Body += f"\n\nTranscribed Text: {transcribed_text} \n\n"



            # Empty message, we shoudl check for media
            if Body is None or Body == "":
                return {"success": True}
            
            res = await self.openai_handler.query(Body, user['assistant_id'], user['openai_api_key'])

            self.whatsapp_handler.send_message(From, To, res[0])
            return {"success": True}

        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    


__all__ = ['WhatsAppBot']
