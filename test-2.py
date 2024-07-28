import os
import openai
import httpx
from dotenv import load_dotenv
import logging
import asyncio

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
OPENAI_KEY = os.getenv('OpenAIKey')
OPENAI_BASE_URL = os.getenv('OpenAIBaseURL')
OPENAI_MODEL = os.getenv('OpenAIModel')

# Set OpenAI configuration
openai.api_key = OPENAI_KEY
openai.api_base = OPENAI_BASE_URL

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
        self.api_key = OPENAI_KEY
        self.api_base = OPENAI_BASE_URL
        self.tool_manager = tool_manager

    async def get_response(self, prompt):
        try:
            response = openai.Completion.create(
                model=OPENAI_MODEL,
                prompt=prompt,
                max_tokens=150
            )
            return response.choices[0].text.strip()
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
