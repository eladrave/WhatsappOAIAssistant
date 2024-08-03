from openai import OpenAI
import logging
import requests

class AudioTranscriber:
    def __init__(self, model: str = "whisper-1"):
        """
        Initialize the AudioTranscriber with a default Whisper model.
        
        :param model: The Whisper model to use for transcription.
        """
        self.model = model
        self.logger = logging.getLogger(__name__)

    def transcribe_audio(self, api_key: str, file_path: str) -> str:
        """
        Transcribe the given audio file to text using OpenAI's Whisper API.
        
        :param api_key: The OpenAI API key.
        :param file_path: The path to the audio file.
        :return: Transcribed text from the audio file.
        """
        try:
            # Initialize the OpenAI client with the provided API key
            client = OpenAI(api_key=api_key)

            # Load the audio file
            audio_file = self._load_audio_file(file_path)
            
            # Transcribe the audio using the Whisper API
            transcript = client.audio.transcriptions.create(
                model=self.model,
                file=audio_file
            )
            
            return transcript.text
        except Exception as e:
            self.logger.error(f"Error during transcription: {e}")
            return "An error occurred during transcription."

    def _load_audio_file(self, file_path: str):
        """
        Load the audio file for transcription.
        
        :param file_path: The path to the audio file.
        :return: The audio file opened in binary read mode.
        """
        try:
            return open(file_path, "rb")
        except FileNotFoundError:
            self.logger.error(f"File not found: {file_path}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading audio file: {e}")
            raise

    def download_audio_file(self, url, local_filename):
        """
        Download the audio file from the provided URL and save it locally.
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Check for request errors

            with open(local_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            print(f"Downloaded file saved as {local_filename}")

        except Exception as e:
            print(f"Error downloading the file: {e}")
            return None


