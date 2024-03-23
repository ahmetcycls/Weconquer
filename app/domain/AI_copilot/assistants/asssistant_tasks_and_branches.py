
from app.domain.AI_copilot.models import AI_copilot
from openai import OpenAI, AsyncOpenAI
import json
import dotenv
import os

from app.v1.endpoints.project_router import get_project_graph_in_readable_format, ProjectReadRequest
from app.v1.endpoints.task_router import TaskDetail, TaskCreatePayload, create_task_endpoint, register_socketio_events
from pydantic import parse_obj_as
from app.domain.project.services import fetch_project_hierarchy

dotenv.load_dotenv()
async def chatGPT(prompt):

    client = AsyncOpenAI()
    client.api_key = os.getenv("OPENAI_API_KEY")

    messages = [{"role": "user", "content": prompt}]
    #gpt-3.5-turbo-1106
    # gpt - 4 - 0125 - preview
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        response_format={ "type": "json_object"}
    )
    response_message = response.choices[0].message.content
    return response_message

async def assistant_to_create_branches_or_task_under_node(nodeId, ai_payload: AI_copilot, sio, sid):
    print("assistant_to_create_branches_or_task_under_node")
    project_graph = ai_payload.history[1]["content"]
    history_json = ai_payload.history[2:]
    #convert the history to a readable format for the prompt like user: assistant: user: assistant:
    history = "\n".join([f"{message['role']}: {message['content']}" for message in history_json])
    prompt = f"""
    json
    Understand the following conversation keeping in mind the last thing the user wants: '{history}'. 
    
    And also, understand the current project structure which is the graph, and keep in mind the nodes and right under it the titles: '{project_graph}'.
    
    Your task is to understand what the user wants and structure a JSON with things that will be attached to the following node '{nodeId}'.
    
    You only have to make sure the JSON is correctly spitted out, and the last users request is fulfilled.
    This is an example response, you can go create as you like:
    {{
      "task_details": [
          {{
            "title": "title"
            "description": "description.",
            "subtasks": [  // This array can include further nested tasks or branches, following the same format.
                  {{
                      "title": "Example Subtask or Sub-Branch Title",
                        "description": "description."
                        "subtasks": [  // This array can include further nested tasks or branches, following the same format.
                      
                    }}
              ]
            }},
            {{
            "title": "Title",
            "description": "description." etc etc
            }},
            {{
            "title": "title",
            "description": "description." etc etc
            }}
      ]
    }}
    
    As you see, you can go unlimitedly. You can create as many subtasks or branches as you want. Fully understand the users request and provide the tasks or branches accordingly. Try to create more then 2 nested tasks.
    """
    try:


        response = await chatGPT(prompt)
        response = json.loads(response)

        with open('response_gpt.json', 'w') as file:
            json.dump(response, file, indent=4)
        print("\n\n\n\n")
        response["user_id"] = ai_payload.user_id
        response['project_node_id'] = ai_payload.project_node_id
        response['parent_node_id'] = nodeId
        payload = parse_obj_as(TaskCreatePayload, response)
        create_task_response = await create_task_endpoint(payload, sio, sid)
        print(create_task_response, "printing the create_task_response")

        graph_readable = await fetch_project_hierarchy(ai_payload.project_node_id,ai_payload.user_id)

        #TODO instead of sending the nodes here, send it within the repository_impl.py file
        # await sio.emit('added_node', {'data': create_task_response}, room=sid)

        # Save the JSON string to a file

        return graph_readable
    except Exception as e:
        print(e)

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