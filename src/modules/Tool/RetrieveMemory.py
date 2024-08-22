
from .Tool import Tool

from ..Session import Session

class RetrieveMemory(Tool):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        

    async def execute(self, query: str, session: Session, **kwargs) -> str:
        memory = session.memory_client.search(query, user_id=session.user_id)
        return memory

    def __str__(self) -> str:
        return "retrive_memory"

