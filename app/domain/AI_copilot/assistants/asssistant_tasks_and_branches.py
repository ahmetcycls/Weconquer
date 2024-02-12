
from app.domain.AI_copilot.models import AI_copilot
from openai import OpenAI
import json
import dotenv
import os
from app.v1.endpoints.task_router import TaskDetail, TaskCreatePayload, create_task_endpoint

dotenv.load_dotenv()
async def chatGPT(prompt):

    client = OpenAI()
    client.api_key = os.getenv("OPENAI_API_KEY")

    messages = [{"role": "user", "content": prompt}]


    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=messages,
        response_format={ "type": "json_object"}
    )
    response_message = response.choices[0].message.content
    return response_message


async def assistant_to_create_branches_or_task_under_node(nodeId: str, instruction_to_the_assistant: str):
    print(instruction_to_the_assistant)
    prompt = f"""
    Create a JSON structure from the provided instructions: '{instruction_to_the_assistant}'. The JSON should organize branches or tasks under the project, with only 'title' as a mandatory field; all other fields are optional. Branches or tasks can have nested subtasks or further branches to any depth, potentially including 'description', 'assigned_to', 'status', 'skills', and further 'subtasks'. Structure the JSON as follows, adapting content dynamically as per instructions:

    {{
      "task_details": [
          {{
              "title": "Example Task or Branch Title",
              "description": "Optional. Example description.",
              "subtasks": [  // This array can include further nested tasks or branches, following the same format.
                  {{
                      "title": "Example Subtask or Sub-Branch Title",
                      "subtasks": [  // Additional nesting levels can be included here, demonstrating the structure's flexibility.
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
        payload = TaskCreatePayload(
            user_id = "12",
            task_details = response,
            parent_node_id = nodeId
        )
        response = create_task_endpoint(payload)

        #TODO Return the current graph of the project in readable nodes format for the AI

        #Update the front-end graph with websockets

        return response
    except Exception as e:
        print(e)

