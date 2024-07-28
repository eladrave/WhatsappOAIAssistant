class Tool:
    async def execute(self, *args, **kwargs):
        raise NotImplementedError("Subclasses should implement this method.")

    def __str__(self) -> str:
        return "tool name"
    
__all__ = ['Tool']
