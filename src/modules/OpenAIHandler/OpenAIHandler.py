import openai
import os
import time
import json
from dotenv import load_dotenv
from openai import OpenAI
import asyncio


from ..ToolManager.ToolManager import ToolManager
from ..Tool.WebSearch import WebSearch




class OpenAIHandler:
    def __init__(self, sleep_period=0.5) -> None:
        self.tool_manager = ToolManager()
        self._register_tools()
        self.sleep_period = sleep_period
        self.client = OpenAI()


    def _register_tools(self):
        """Register all available tools."""
        self.tool_manager.register_tool(WebSearch())

    async def query(self, query: str, assistant_id: str, openai_api_key: str):
        openai.api_key = openai_api_key

        thread = self.client.beta.threads.create()

        self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=query,
        )

        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,
        )

        run = await self._wait_on_run(thread, run)

        messages = self.client.beta.threads.messages.list(thread_id=thread.id)
        return [msg.content[0].text.value for msg in messages.data]

    async def _wait_on_run(self, thread, run):
        while run.status != "completed":
            print(run.status)  
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id,
            )
            
            if run.required_action:
                tool_call_reqs = await self._handle_tool_calls(run)

                # Submit the tool output
                run = self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_call_reqs,
                )

            time.sleep(self.sleep_period)
        
        return run

    async def _handle_tool_calls(self, run):
        tool_call_reqs = []
        for tool_call in run.required_action.submit_tool_outputs.tool_calls:
            print("Call ", tool_call.function)

            # Execute the tool
            tool_params = json.loads(tool_call.function.arguments)
            tool_result = await self.tool_manager.use_tool(tool_call.function.name, **tool_params)

            tool_call_dict = {
                "tool_call_id": tool_call.id,
                "output": json.dumps({"result": tool_result})
            }
            tool_call_reqs.append(tool_call_dict)
        return tool_call_reqs
    

__all__ = ['OpenAiHandler']
