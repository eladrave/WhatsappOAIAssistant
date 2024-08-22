from fastapi import FastAPI, Form, HTTPException, Request, status
import logging
import os


from ..SessionFactory import SessionFactory
from ..SessionManager import SessionManager
from ..WhatsAppHandler import WhatsAppHandler
from ..DBClient import DBClient
from ..OpenAIHandler import OpenAIHandler
from ..AudioTranscriber import AudioTranscriber


class WhatsAppBot:
    def __init__(self,
                  db_client: DBClient, 
                  whatsapp_handler: WhatsAppHandler, 
                  openai_handler: OpenAIHandler, 
                  audio_transcriber: AudioTranscriber, 
                  session_manager: SessionManager, 
                  session_factory: SessionFactory,
                  logger):
        self.db_client = db_client
        self.whatsapp_handler = whatsapp_handler
        self.openai_handler = openai_handler
        self.audio_transcriber = audio_transcriber
        self.session_manager = session_manager
        self.session_factory = session_factory
        self.logger = logger



    # For cloud
    async def heartbeat(self):
        self.session_manager.update_sessions()
        return {'success': True}

    async def handle_message(self, request: Request):
        try:
            From, To, Body, form_data = await self.whatsapp_handler.process_request(request)

            # Is the user is not registered, we should not respond
            if not self.db_client.check_user_exists(From):
                return {"success": True}

            user = self.db_client.get_user(From) # Get user by phone number
            
            logging.info(f"User: {user}")

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

            outdated_sessions = self.session_manager.update_sessions()
            for session_id in outdated_sessions:
                self.session_manager.delete_session(session_id)


            # Empty message, we shoudl check for media
            if Body is None or Body == "":
                return {"success": True}
            
            conv = session.memory_client.get_all(session_id=session.session_id, user_id=user.phone_number)

            prompt = f"{conv}\nUser: {Body}\nAssistant:"


            res = await self.openai_handler.query(prompt, session)

            session.memory_client.add(prompt+res[0], session_id=session.session_id, user_id=user.phone_number)

            self.whatsapp_handler.send_message(From, To, res[0])
            return {"success": True}

        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    


__all__ = ['WhatsAppBot']
