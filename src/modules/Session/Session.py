
from openai import OpenAI
from mem0 import Memory

from mem0 import MemoryClient

class Session:
    def __init__(self, session_id: str, user_id: str, openai_client: OpenAI, assistant_id: str, memory_client: MemoryClient) -> None:
        self.session_id = session_id
        self.user_id = user_id
        self.openai_client = openai_client
        self.assistant_id = assistant_id
        self.memory_client = memory_client

    def __del__(self):
        self.memory_client.delete_all(session_id=self.session_id, user_id=self.user_id)
        

    
