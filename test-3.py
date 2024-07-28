import openai
import os
import time
from dotenv import load_dotenv
from openai import OpenAI


# Load environment variables from .env file
load_dotenv()

# Set OpenAI configuration
openai.api_key = os.getenv('OpenAIKey')
assistant_id = os.getenv('OpenAIAssistantId')

client = OpenAI(api_key=os.environ.get("OpenAIKey", "<your OpenAI API key if not set as env var>"))



thread = client.beta.threads.create()

message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Can you help me?",
)


run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant_id,
)


import time

def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

run = wait_on_run(run, thread)
print(run)
