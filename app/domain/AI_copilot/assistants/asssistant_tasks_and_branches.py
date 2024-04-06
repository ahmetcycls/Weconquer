
from app.domain.AI_copilot.models import AI_copilot
from openai import OpenAI, AsyncOpenAI
import json
import dotenv
import os
from app.domain.task_tree.repository_impl import get_node_title
from app.v1.endpoints.project_router import get_project_graph_in_readable_format, ProjectReadRequest
from app.v1.endpoints.task_router import TaskDetail, TaskCreatePayload, create_task_endpoint, register_socketio_events
from pydantic import parse_obj_as
from app.domain.project.services import fetch_project_hierarchy

dotenv.load_dotenv()
async def chatGPT(messages):

    client = AsyncOpenAI()
    client.api_key = os.getenv("OPENAI_API_KEY")

    # messages = [{"role": "user", "content": prompt}]
    #gpt-3.5-turbo-1106
    # gpt - 4 - 0125 - preview
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        response_format={ "type": "json_object"},
        temperature=0.2

    )
    response_message = response.choices[0].message.content
    return response_message

async def assistant_to_create_branches_or_task_under_node(nodeId, ai_payload: AI_copilot, sio, sid):
    print("assistant_to_create_branches_or_task_under_node")
    project_graph = ai_payload.history[1]["content"]
    history_json = ai_payload.history[2:]
    # print(history_json)

    node_title = await get_node_title(ai_payload.user_id, ai_payload.project_node_id, nodeId)
    print(node_title, "node title is getting printed")
    #convert the history to a readable format for the prompt like user: assistant: user: assistant:
    # history = "\n".join([f"{message['role']}: {message['content']}" for message in history_json])
    prompt = f"""
    json
    Understand the current project structure which is the "Project Graph": '{project_graph}'.
    
    Structure a JSON with things that will be attached to the Node ID of the title the user wants it to be attached to.
    So figure out from the conversation under which node the user wants something to be added to.
    
    This is an example response, make sure whatever you will add will come under the RIGHT nodeID, BE creative as possible about the things that will come under what the user wants.
    {{
      "parent_node_id": "nodeid under which the subnodes will be placed at",
      "subnodes": [
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
            "description": "description." 
            }},
            {{
            "title": "title",
            "description": "description." 
            }}
      ]
    }}
    
    As you see, you can go unlimitedly. You can create as many subtasks or branches as you want. 
    
    Remember, whatever you will produce under the subnodes array, imagine it will come right under {node_title}. So do not include {node_title} in the subnodes array, just pretend whatever you're producing in subnodes array that it will come right under {node_title}.
    AND make sure you're not generating the same things that already exist under {node_title}, see "Project Graph" above the example json response.
    """
    allowed_roles = {"user", "system", "assistant"}
    filtered_history_json = [entry for entry in history_json if entry.get("content") is not None and entry.get("role") in allowed_roles]
    filtered_history_json.insert(0, {"role": "system", "content": prompt})

    # add_system_prompt = {"role": "system", "content": prompt}
    # filtered_history_json.append(history_json)
    print(filtered_history_json)
    try:


        response = await chatGPT(filtered_history_json)
        response = json.loads(response)

        with open('response_gpt.json', 'w') as file:
            json.dump(response, file, indent=4)
        response["user_id"] = ai_payload.user_id
        response['project_node_id'] = ai_payload.project_node_id
        # response['parent_node_id'] = nodeId
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