class ToolManager:
    def __init__(self):
        self.tools = {}

    def register_tool(self, tool):
        """Register a tool with a given name."""
        self.tools[str(tool)] = tool

    async def use_tool(self, tool_name: str, *args, **kwargs):
        """Execute a tool by name with the provided arguments."""
        if tool_name in self.tools:
            return await self.tools[tool_name].execute(*args, **kwargs)
        else:
            raise ValueError(f"Tool '{tool_name}' not found.")

__all__ = ['ToolManager']
