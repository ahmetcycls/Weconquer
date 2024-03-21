from app.domain.AI_copilot.models import AI_copilot
from app.domain.AI_copilot.assistants.asssistant_tasks_and_branches import assistant_to_create_branches_or_task_under_node
from openai import OpenAI, AsyncOpenAI
import json
import dotenv
import os
from app.v1.endpoints.project_router import get_project_graph_in_readable_format


dotenv.load_dotenv()

prompt = """ You and your assistant will help the user to build and expand projects in the fastest and nicest ways
It's really important to correctly pass the right nodeId understand under what node the user wants something to be added to..
  
        
     Chat, brainstorm, help, ask questions to the user to fully understand what they're trying to build and make use of your assistant that will read the whole conversation and add tasks and nodes to the project!
     """

available_functions = {
    "assistant_to_create_branches_or_task_under_node": assistant_to_create_branches_or_task_under_node,
}  # only one function in this example, but you can have multiple


async def ai(ai_payload: AI_copilot, sio, sid):
    client = AsyncOpenAI()
    client.api_key = os.getenv("OPENAI_API_KEY")
    tools = [
        {
            "type": "function",
            "function": {
                "name": "assistant_to_create_branches_or_task_under_node",
                "description": "supply the nodeId under which operations will be done, assistant will read the conversation and create the tasks or branches under the provided nodeId.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "nodeId": {
                            "type": "string",
                            "description": "the nodeId of the task under which the new tasks will be created",
                        },
                    },
                    "required": ["nodeId"],
                },
            },
        }
    ]
    #gpt - 3.5 - turbo - 1106
    #"gpt-4-0125-preview"
    messages = ai_payload.history
    print(
    "were in messages"
    )
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    response_message = response.choices[0].message

    tool_calls = response_message.tool_calls
    if tool_calls:
        print("function calling is active")

        del response_message.function_call
        print(response_message.dict(), "response message")
        response_message.content = "function calling is active"
        ai_payload.history.append(response_message.dict())    # extend conversation with assistant's reply

        for tool_call in tool_calls:
            function_name = tool_call.function.name

            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)

            function_args["ai_payload"] = ai_payload
            function_args["sio"] = sio
            function_args["sid"] = sid
            print("lijn 73 ai_logic.py")

            function_response = await function_to_call(
                **function_args
            )
            print("lijn 75 ai_logic.py")
            #TODO FIND OUT WHY THE FUNCTION RESPONSE IS NONE
            print("printing function response", function_response)
            ai_payload.history[1]["content"] = function_response
            print("lijn 77 ai_logic.py")
            ai_payload.history.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": "The graph is updated, the user (in the graph) and you (above the chat) can see it. Ask the user how it looks like without calling function.",
                }
            )
            print(ai_payload.history)
            print("lijn 87 ai_logic.py")
        return await ai(ai_payload, sio, sid)
    ai_payload.history.append({"role": "assistant", "content": response_message.content})
    return ai_payload
