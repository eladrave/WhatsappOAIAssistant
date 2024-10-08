
from .Tool import Tool

from ..Session import Session

class SaveMemory(Tool):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        

    async def execute(self, query: str, session: Session, **kwargs) -> str:
        session.memory_client.add(query, user_id=session.user_id)
        return "Memory saved successfully."

    def __str__(self) -> str:
        return "save_memory"

