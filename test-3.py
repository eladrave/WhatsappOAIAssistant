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

client = OpenAI(api_key=os.environ["OpenAIKey"])



thread = client.beta.threads.create()

message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="What is the latest news in Israel?",
)


run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant_id,
)


import time

def wait_on_run(run, thread):
    while run.status != "completed":
        print(run.status)  
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        
        if run.required_action:
            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                print("Call ", tool_call.function)
            
            run = client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=[
                    {
                        "tool_call_id": tool_call.id,
                        "output": json.dumps(responses),
                    }
                ],
            )

                
    return run

run = wait_on_run(run, thread)
print(run)


