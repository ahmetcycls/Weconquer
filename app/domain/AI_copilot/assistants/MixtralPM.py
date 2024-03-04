from app.domain.AI_copilot.models import AI_copilot
from app.domain.AI_copilot.assistants.asssistant_tasks_and_branches import assistant_to_create_branches_or_task_under_node
from openai import OpenAI, AsyncOpenAI
import json
import dotenv
import os
from app.v1.endpoints.project_router import get_project_graph_in_readable_format


dotenv.load_dotenv()

prompt = """ You are a project manager assistant, whenever you think that the user wants to create a branch or a task under a node, just type 'ASSIGN' and I will take care of the rest.
     """

available_functions = {
    "assistant_to_create_branches_or_task_under_node": assistant_to_create_branches_or_task_under_node,
}  # only one function in this example, but you can have multiple


async def ai(ai_payload: AI_copilot, sio, sid):
    client = AsyncOpenAI()
    client.api_key = os.getenv("OPENAI_API_KEY")

    #gpt - 3.5 - turbo - 1106
    messages = ai_payload.history
    print("WE ARE HERE")
    response = await client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=messages,
    )

    response_message = response.choices[0].message
    print("WE ARE HERE 2 ")
    if response_message.content == "ASSIGN":

        response_node_creation = await assistant_to_create_branches_or_task_under_node(ai_payload.nodeId, ai_payload.instruction_to_the_assistant, ai_payload, sio, sid)
        return await ai(ai_payload, sio, sid)
    ai_payload.history.append({"role": "assistant", "content": response_message.content})
    return ai_payload
