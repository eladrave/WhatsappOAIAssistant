import time

from ..SessionBuilder import SessionBuilder
from ..Session import Session
from ..User import User

from openai import OpenAI
from mem0 import MemoryClient

class SessionFactory:
    def __init__(self, session_builder: SessionBuilder):
        self.session_builder = session_builder

    def create_standard_session(self, user: User) -> Session:
        openai_client = OpenAI(api_key=user.api_keys['openai_api_key'])
        memory_client = MemoryClient(user.api_keys['mem0_api_key'])

        session_id = f"{user.phone_number}-{int(time.time())}"
        user_id = user.phone_number

        session = self.session_builder\
            .set_openai_client(openai_client)\
            .set_assistant_id(user.assistant_id)\
            .set_memory_client(memory_client)\
            .set_session_id(session_id)\
            .set_user_id(user_id)\
            .build()
        
        return session

