from app.domain.AI_copilot.models import AI_copilot
from app.domain.AI_copilot.assistants.asssistant_tasks_and_branches import assistant_to_create_branches_or_task_under_node
from openai import OpenAI
import json
import dotenv
import os
from app.v1.endpoints.project_router import get_project_graph_in_readable_format
dotenv.load_dotenv()

prompt = """ You are a project manager assistant, you scale projects seamlessly by suggesting and creating branches and tasks unlimitedly.
     The current project structure looks as follows: {}
        
     Chat with the user so you can unlimitedly scale the project!
     """


async def ai(ai_payload):

    client = OpenAI()
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

    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=ai_payload.history,
        tools=tools,
        tool_choice="auto",  #
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    if tool_calls:

        available_functions = {
            "assistant_to_create_branches_or_task_under_node": assistant_to_create_branches_or_task_under_node,
        }  # only one function in this example, but you can have multiple
        ai_payload.history.append(response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            print("function calling is active")
            function_name = tool_call.function.name
            print(function_name, "function name")

            function_to_call = available_functions[function_name]
            print(function_to_call, "function to call")
            function_args = json.loads(tool_call.function.arguments)
            function_response = await function_to_call(
                **function_args
            )
            print(function_response)
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
    return ai_payload.history
