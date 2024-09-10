from .Session import Session
from openai import OpenAI

from mem0 import MemoryClient

# Follow builder pattern to create a session
class SessionBuilder:
    def __init__(self):
        self.openai_client = None
        self.assistant_id = None
        self.user_id = None
        self.memory_client = None
        self.session_id = None


    def set_openai_client(self, openai_client: OpenAI):
        self.openai_client = openai_client
        return self
    
    def set_assistant_id(self, assistant_id: str):
        self.assistant_id = assistant_id
        return self
    
    def set_memory_client(self, memory_client: MemoryClient):
        self.memory_client = memory_client
        return self
    
    def set_session_id(self, session_id: str):
        self.session_id = session_id
        return self
    
    def set_user_id(self, user_id: str):
        self.user_id = user_id
        return self


    def build(self):
        return Session(session_id=self.session_id, 
                        openai_client=self.openai_client,
                        assistant_id=self.assistant_id,
                        user_id=self.user_id, 
                        memory_client=self.memory_client)    

    


    
