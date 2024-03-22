
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
    Understand the following conversation keeping in mind the last thing the user said : '{history}'. 
    
    And also, understand the current project structure: '{project_graph}'.
    
    Your task is to fulfill the users request.
    
    Every task details you will provide will come under the node with the nodeId: '{nodeId}', automatically. You don't have to do anything about that.
    Now please provide the task details in the following format, kindly all in one go :
    {{
      "task_details": [
          {{
              "title": "Task or Branch Title",
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
            "title": "Task or Branch Title",
            "description": "description." etc etc
        }}
      ]
    }}
    """
    try:
        response = await chatGPT(prompt)
        response = json.loads(response)

        response["user_id"] = ai_payload.user_id
        response['project_node_id'] = ai_payload.project_node_id
        response['parent_node_id'] = nodeId
        payload = parse_obj_as(TaskCreatePayload, response)
        create_task_response = await create_task_endpoint(payload, sio, sid)

        graph_readable = await fetch_project_hierarchy(ai_payload.project_node_id,ai_payload.user_id)


        await sio.emit('added_node', {'data': create_task_response}, room=sid)

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