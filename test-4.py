import openai
import os
import time
import httpx
import json
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set OpenAI configuration
openai.api_key = os.getenv('OpenAIKey')
assistant_id = os.getenv('OpenAIAssistantId')

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
        self.client = openai

    def wait_on_run(self, run, thread):
        while run['status'] in ["queued", "in_progress"]:
            run = self.client.AssistantRun.retrieve(
                thread_id=thread['id'],
                run_id=run['id'],
            )
            time.sleep(0.5)
        return run

    async def query_assistant(self, prompt):
        try:
            # Create a new thread
            thread = self.client.Thread.create()
            thread_id = thread['id']

            # Add a message to the thread
            self.client.ThreadMessage.create(
                thread_id=thread_id,
                role="user",
                content=prompt
            )

            # Run the Assistant
            run = self.client.AssistantRun.create(
                thread_id=thread_id,
                assistant_id=assistant_id
            )
            run = self.wait_on_run(run, thread)

            # Handle tool call if required
            if run['status'] == 'requires_action':
                await self.handle_tool_call(thread, run)

            # Retrieve the response
            messages = self.client.ThreadMessage.list(thread_id=thread_id)
            assistant_response = messages['data'][-1]['content']
            print("Assistant Response:", assistant_response)
        except Exception as e:
            print(f"Error querying assistant: {e}")

    async def handle_tool_call(self, thread, run):
        tool_call = run['required_action']['submit_tool_outputs']['tool_calls'][0]
        tool_name = tool_call['function']['name']
        arguments = json.loads(tool_call['function']['arguments'])

        try:
            result = await self.tool_manager.execute_tool(tool_name, **arguments)
            self.client.AssistantRun.submit_tool_outputs(
                thread_id=thread['id'],
                run_id=run['id'],
                tool_outputs=[{
                    "tool_call_id": tool_call['id'],
                    "output": json.dumps(result),
                }]
            )

            # Wait for the run to complete after tool output is submitted
            run = self.wait_on_run(run, thread)
            return run
        except Exception as e:
            print(f"Error executing tool {tool_name}: {e}")

if __name__ == "__main__":
    tool_manager = ToolManager()
    web_search_tool = WebSearchTool()
    tool_manager.register_tool(web_search_tool)

    assistant = OpenAIAssistant(tool_manager)
    asyncio.run(assistant.query_assistant("Hello, how are you?"))

    # Example of using a tool with the assistant
    asyncio.run(assistant.query_assistant("Search for the latest news on AI advancements."))
