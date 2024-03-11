
from app.domain.AI_copilot.models import AI_copilot
from openai import OpenAI, AsyncOpenAI
import json
import dotenv
import os

from app.v1.endpoints.project_router import get_project_graph_in_readable_format, ProjectReadRequest
from app.v1.endpoints.task_router import TaskDetail, TaskCreatePayload, create_task_endpoint
from pydantic import parse_obj_as
dotenv.load_dotenv()
async def chatGPT(prompt):

    client = AsyncOpenAI()
    client.api_key = os.getenv("OPENAI_API_KEY")

    messages = [{"role": "user", "content": prompt}]
    #gpt-3.5-turbo-1106
    # gpt - 4 - 0125 - preview
    response = await client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=messages,
        response_format={ "type": "json_object"}
    )
    response_message = response.choices[0].message.content
    return response_message


async def assistant_to_create_branches_or_task_under_node(nodeId, instruction_to_the_assistant: str, ai_payload: AI_copilot, sio, sid):
    print(instruction_to_the_assistant)
    prompt = f"""
    Create a JSON structure from the provided instructions: '{instruction_to_the_assistant}'. The JSON should organize branches or tasks under the project, with only 'title' as a mandatory field; all other fields are optional. Branches or tasks can have nested subtasks or further branches to any depth, potentially including 'description', 'assigned_to', 'status', 'skills' (list of strings), and further 'subtasks'. Structure the JSON as follows, adapting content dynamically as per instructions:
    Subtasks always have to be a list, even if there is only one subtask or no at all..
    {{
      "task_details": [
          {{
              "title": "Task or Branch Title",
              "description": "description.",
              "subtasks": [  // This array can include further nested tasks or branches, following the same format.
                  {{
                      "title": "Example Subtask or Sub-Branch Title",
                        
                          {{
                              "title": "Example Sub-Subtask or Sub-Sub-Branch Title"
                              // Further details are optional, highlighting the mandatory title field only.
                          }}
                      ]
                  }}
              ]
          }}
      ]
    }}
    """
    try:
        response = await chatGPT(prompt)

        print(response)
        response = json.loads(response)
        print(response)

        #TODO Check why this error is happening
        response["user_id"] = ai_payload.user_id
        response['project_node_id'] = ai_payload.project_node_id
        payload = parse_obj_as(TaskCreatePayload, response)
        response = create_task_endpoint(payload)
        print(response)
        #TODO Return the current graph of the project in readable nodes format for the AI

        #Update the front-end graph with websockets
        projectReadRequest = ProjectReadRequest(project_node_id=ai_payload.project_node_id, user_id=ai_payload.user_id)
        response_graph_readable = await get_project_graph_in_readable_format(projectReadRequest)
        response_graph_readable = "Users graph is updated, ask the user if it looks good, you don't have to explain just ask them. : " + response_graph_readable
        await sio.emit('graph_update', {'data': 'updated graph'}, room=sid)
        return response_graph_readable
    except Exception as e:
        print(e)

