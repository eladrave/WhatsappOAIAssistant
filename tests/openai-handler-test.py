import openai
import os
import time
import json
from dotenv import load_dotenv
from openai import OpenAI
import asyncio
import httpx

from src.modules.OpenAIHandler.OpenAIHandler import OpenAIHandler

# Load environment variables from .env file
load_dotenv()



# Set OpenAI configuration
openai.api_key = os.getenv('OpenAIKey')
assistant_id = os.getenv('OpenAIAssistantId')

client = OpenAI(api_key=os.environ["OpenAIKey"])



async def main():
    handler = OpenAIHandler(client, assistant_id)
    res = await handler.query("What is the latest news in Israel?")
    print(res)

if __name__ == "__main__":
    asyncio.run(main())
