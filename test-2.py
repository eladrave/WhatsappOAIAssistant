import os
import openai
import httpx
from dotenv import load_dotenv
import logging
import asyncio
import json

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
OPENAI_KEY = os.getenv('OpenAIKey')
OPENAI_ASSISTANT_ID = os.getenv('OpenAIAssistantId')

# Set OpenAI configuration
openai.api_key = OPENAI_KEY

class Tool:
    def __init__(self, name):
        self.name = name

    async def execute(self, *args, **kwargs):
        pass

class WebSearchTool(Tool):
    def __init__(self):
        super().__init__('web_search')

    async def execute(self, query):
        async with httpx.AsyncClient() as client:
            response = await client.get(f'https://api.example.com/search?q={query}')
            return response.json()

class ToolManager:
    def __init__(self):
        self.tools = {}

    def register_tool(self, tool):
        self.tools[tool.name] = tool

    async def execute_tool(self, tool_name, *args, **kwargs):
        if tool_name in self.tools:
            return await self.tools[tool_name].execute(*args, **kwargs)
        else:
            raise ValueError(f"Tool {tool_name} not found")

class OpenAIAssistant:
    def __init__(self, tool_manager):
        self.tool_manager = tool_manager

    async def get_response(self, prompt):
        try:
            # Create a new thread
            thread = await openai.Thread.create()
            logger.debug(f"Created thread: {thread}")

            # Add a user message to the thread
            user_message = await openai.Message.create(
                thread_id=thread.id,
                role="user",
                content=prompt
            )
            logger.debug(f"Added message to thread: {user_message}")

            # Run the assistant
            run = await openai.Run.create(
                thread_id=thread.id,
                assistant_id=OPENAI_ASSISTANT_ID
            )
            logger.debug(f"Started assistant run: {run}")

            # Wait for the run to complete
            run = await self.wait_on_run(run, thread)

            # Retrieve the assistant's response
            messages = await openai.Message.list(thread_id=thread.id)
            assistant_response = messages[-1].content
            logger.debug(f"Assistant response: {assistant_response}")

            return assistant_response
        except Exception as e:
            logger.error(f"Error getting response from OpenAI: {e}")
            return "Sorry, something went wrong with the assistant."

    async def handle_tool(self, tool_name, *args, **kwargs):
        try:
            result = await self.tool_manager.execute_tool(tool_name, *args, **kwargs)
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return "Sorry, something went wrong with the tool."

    async def wait_on_run(self, run, thread):
        while run.status in ["queued", "in_progress"]:
            await asyncio.sleep(1)
            run = await openai.Run.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
        return run

async def sanity_check():
    tool_manager = ToolManager()
    assistant = OpenAIAssistant(tool_manager)

    # Register tools
    tool_manager.register_tool(WebSearchTool())

    # Test OpenAI response
    openai_response = await assistant.get_response("Hello, how are you?")
    logger.info(f"OpenAI Response: {openai_response}")

    # Test Tool execution
    try:
        tool_response = await assistant.handle_tool('web_search', 'OpenAI')
        logger.info(f"Tool Response: {tool_response}")
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")

if __name__ == "__main__":
    asyncio.run(sanity_check())
