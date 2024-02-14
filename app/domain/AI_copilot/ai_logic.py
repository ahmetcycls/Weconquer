from app.domain.AI_copilot.models import AI_copilot
from app.domain.AI_copilot.assistants.asssistant_tasks_and_branches import assistant_to_create_branches_or_task_under_node
from openai import OpenAI, AsyncOpenAI
import json
import dotenv
import os
from app.v1.endpoints.project_router import get_project_graph_in_readable_format


dotenv.load_dotenv()

prompt = """ You are a project manager assistant, you scale projects seamlessly by suggesting and creating branches and tasks unlimitedly.
     The current project structure looks as follows: {}
        
     Chat with the user so you can unlimitedly scale the project!
     """

available_functions = {
    "assistant_to_create_branches_or_task_under_node": assistant_to_create_branches_or_task_under_node,
}  # only one function in this example, but you can have multiple


async def ai(ai_payload: AI_copilot):
    client = AsyncOpenAI()
    client.api_key = os.getenv("OPENAI_API_KEY")
    tools = [
        {
            "type": "function",
            "function": {
                "name": "assistant_to_create_branches_or_task_under_node",
                "description": "Your assistant that adds one or unlimited tasks or branches, with or without unlimited subtasks or branches, under the project, a branch or task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "nodeId": {
                            "type": "string",
                            "description": "the nodeId of the task under which the new tasks will be created",
                        },
                        "instruction_to_the_assistant": {
                            "type": "string",
                            "description": "Explain the branches or tasks to be created",
                        },
                    },
                    "required": ["nodeId", "instruction_to_the_assistant"],
                },
            },
        }
    ]
    #gpt - 3.5 - turbo - 1106
    messages = ai_payload.history
    print("WE ARE HERE")
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    response_message = response.choices[0].message
    print("WE ARE HERE 2 ")

    tool_calls = response_message.tool_calls
    if tool_calls:
        print("function calling is active")

        del response_message.function_call
        ai_payload.history.append(response_message)    # extend conversation with assistant's reply

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            print("WE ARE HERE 4 ")

            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)

            function_args["ai_payload"] = ai_payload
            function_response = await function_to_call(
                **function_args
            )

            (ai_payload.history.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            ))
        return await ai(ai_payload)
    ai_payload.history.append({"role": "assistant", "content": response_message.content})
    return ai_payload
