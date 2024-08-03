from fastapi import FastAPI, Form, HTTPException, Request, status
import logging
import os
from twilio.rest import Client
import openai

from ..WhatsAppHandler import WhatsAppHandler
from ..OpenAIHandler import OpenAIHandler
from ..DBClient import DBClient

from ..AudioTranscriber import AudioTranscriber


class WhatsAppBot:
    def __init__(self):
        self._load_database_client()
        self._load_environment_variables()
        self._initialize_clients()
        self._initialize_handlers()
        self._setup_logging()
        self._initialize_app()
        self._define_routes()

    def _load_database_client(self):
        self.db_client = DBClient(
            os.getenv('DBName'),
            os.getenv('DBUser'),
            os.getenv('DBPassword'),
            os.getenv('DBHost'),
            os.getenv('DBPort', '5432')
        )

    def _load_environment_variables(self):
        config = self.db_client.read_config()

        self.OPENAI_BASE_URL = config['OpenAIBaseURL']
        self.OPENAI_MODEL = config['OpenAIModel']
        self.TWILIO_ACCOUNT_SID = config['TwilioAccountSID']
        self.TWILIO_AUTH_TOKEN = config['TwilioAuthToken']

    def _initialize_clients(self):
        self.twilio_client = Client(self.TWILIO_ACCOUNT_SID, self.TWILIO_AUTH_TOKEN)

    def _initialize_handlers(self):
        openai.api_base = self.OPENAI_BASE_URL

        self.whatsapp_handler = WhatsAppHandler(self.twilio_client)
        self.openai_handler = OpenAIHandler()
        self.audio_transcriber = AudioTranscriber()

    def _setup_logging(self):
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

    def _initialize_app(self):
        self.app = FastAPI()

    def _define_routes(self):
        self.app.post("/handleMessage")(self.handle_message)
        self.app.get("/")(self.heartbeat)

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

    def run(self, host="0.0.0.0", port=8080):
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)


__all__ = ['WhatsAppBot']
