from fastapi import FastAPI, Form, HTTPException, Request, status
import logging
import os


from ..SessionFactory import SessionFactory
from ..SessionManager import SessionManager
from ..WhatsAppHandler import WhatsAppHandler
from ..DBClient import DBClient
from ..OpenAIHandler import OpenAIHandler
from ..AudioTranscriber import AudioTranscriber

from ..Command.CommandHandler import CommandHandler

class WhatsAppBot:
    def __init__(self,
                  db_client: DBClient, 
                  whatsapp_handler: WhatsAppHandler, 
                  openai_handler: OpenAIHandler, 
                  audio_transcriber: AudioTranscriber, 
                  session_manager: SessionManager, 
                  session_factory: SessionFactory,
                  command_handler: CommandHandler,
                  logger):
        self.db_client = db_client
        self.whatsapp_handler = whatsapp_handler
        self.openai_handler = openai_handler
        self.audio_transcriber = audio_transcriber
        self.session_manager = session_manager
        self.session_factory = session_factory
        self.command_handler = command_handler
        self.logger = logger



    # For cloud
    async def heartbeat(self):
        self.session_manager.update_sessions()
        return {'success': True}

    async def handle_message(self, request: Request):
        From, To = None, None
        try:
            From, To, Body, form_data = await self.whatsapp_handler.process_request(request)

            self.logger.info(f"From: {From}, To: {To}, Body: {Body}, form_data: {form_data}")

            # Is the user is not registered, we should not respond
            if not self.db_client.check_user_exists(From):
                return {"success": True}

            
            user = self.db_client.get_user(From) # Get user by phone number

            # Format the phone number
            user.phone_number = user.phone_number.replace("whatsapp:+", "")

            logging.info(f"User: {user}")

            self.session_manager.update_sessions()
            

            if not self.session_manager.is_session_active(user.phone_number):
                session = self.session_factory.create_standard_session(user)
                self.session_manager.create_session(session)
            else:
                session = self.session_manager.get_session(user.phone_number)
                


            NumMedia = form_data.get('NumMedia')
            for i in range(int(NumMedia)):
                media_url = form_data.get(f'MediaUrl{i}')
                media_content_type = form_data.get(f'MediaContentType{i}')
                
                if media_content_type.startswith('audio/ogg'):
                    self.audio_transcriber.download_audio_file(media_url, 'temp/audio.ogg')
                    transcribed_text = self.audio_transcriber.transcribe_audio(session, 'temp/audio.ogg')
                    Body += f"\n\nTranscribed Text: {transcribed_text} \n\n"


            self.session_manager.refresh_session(user.phone_number)

            

            self.logger.info(f"Session: {session}")

            # Empty message, we shoudl check for media
            if Body is None or Body == "":
                return {"success": True}
            

            command = self.command_handler.extract_command(Body)
            if command:
                self.command_handler.execute_command(command, self, user)
                return {"success": True}

            
            conv = session.memory_client.get_all(run_id=session.session_id, user_id=user.phone_number)

            prompt = f"{conv}\nUser: {Body}\nAssistant:"


            res = await self.openai_handler.query(prompt, session)

            session.memory_client.add(prompt+res[0], run_id=session.session_id, user_id=user.phone_number, metadata=['Short Term'])


            self.whatsapp_handler.send_message(From, To, res[0])

            return {"success": True}

        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            if From:
                self.whatsapp_handler.send_message(From, To, str(e))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    


__all__ = ['WhatsAppBot']
