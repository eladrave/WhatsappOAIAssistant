import os
import time
import json
from openai import OpenAI

from ..ToolManager.ToolManager import ToolManager

from ..Session import Session


class OpenAIHandler:
    def __init__(self, tool_manager: ToolManager, sleep_period=0.5) -> None:
        self.tool_manager = tool_manager
        self.sleep_period = sleep_period
        self.client = None


    async def query(self, query: str, session: Session, **kwargs):
        openai_client = session.openai_client
        assistant_id = session.assistant_id

        thread = openai_client.beta.threads.create()

        openai_client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=query,
        )

        run = openai_client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,
        )

        run = await self._wait_on_run(thread, run, openai_client, session)

        messages = openai_client.beta.threads.messages.list(thread_id=thread.id)
        return [msg.content[0].text.value for msg in messages.data]

    async def _wait_on_run(self, thread, run, openai_client: OpenAI, session: Session):
        while run.status != "completed":
            print(run.status)  
            run = openai_client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id,
            )
            
            if run.required_action:
                tool_call_reqs = await self._handle_tool_calls(run, session=session)

                # Submit the tool output
                run = openai_client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_call_reqs,
                )

            time.sleep(self.sleep_period)
        
        return run

    async def _handle_tool_calls(self, run, **kwargs):
        tool_call_reqs = []
        for tool_call in run.required_action.submit_tool_outputs.tool_calls:
            print("Call ", tool_call.function)

            # Execute the tool
            tool_params = json.loads(tool_call.function.arguments)
            tool_result = await self.tool_manager.use_tool(tool_call.function.name, **tool_params, **kwargs)

            tool_call_dict = {
                "tool_call_id": tool_call.id,
                "output": json.dumps({"result": tool_result})
            }
            tool_call_reqs.append(tool_call_dict)
        return tool_call_reqs
    

__all__ = ['OpenAiHandler']
