from mem0 import Memory

class MemoryClient:
    def __init__(self, memory: Memory):
        self.memory = memory

    def search_memories(self, query, user_id, session_id=None):
        if not session_id:
            memories = self.memory.search(query, user_id)
            return [m['memory'] for m in memories]
        else:
            memories = self.memory.search(query, user_id)
            session_memories = [m['memory'] for m in memories if m['metadata'].get('session_id') == session_id]
            return session_memories
        
    def delete_session(self, session_id):
        """
        Delete all memories associated with a session.
        """
        session_memories = self.memory.get_all(user_id=self.user_id)
        for mem in session_memories:
            if mem['metadata'].get('session_id') == session_id:
                self.memory.delete(mem['id'])
