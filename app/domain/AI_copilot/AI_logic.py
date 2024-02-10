from app.domain.AI_copilot.models import AI_copilot
from app.domain.AI_copilot.assistants.asssistant_tasks_and_branches import assistant_to_create_branches_or_task_under_node
from openai import OpenAI
import json
import dotenv
import os

dotenv.load_dotenv()

async def AI(user):
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
        model="gpt-3.5-turbo-0613",
        messages=user.history,
        tools=tools,
        tool_choice="auto",  #
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    if tool_calls:

        available_functions = {
            "assistant_to_create_tasks_under_node": assistant_to_create_branches_or_task_under_node,
        }  # only one function in this example, but you can have multiple
        user.history.append(response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                **function_args
            )
            user.history.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )
        return await AI(user)
    user.history.append(response_message)
    return user.history
