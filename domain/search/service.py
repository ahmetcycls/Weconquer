from db import db
from fastapi import  HTTPException, APIRouter, Request


async def find_person(request: Request):
    request = await request.json()

    #TODO create searchID for a specific project

    #Selec
    request = {
    "user_id": 1,
    "project_id": 1,
    "search_id": 1,
    "traits": [
        {
        "1": "Advanced Cognitive Abilities",
        "weight": 70
        },
        {
        "2": "Speed and Efficiency",
        "weight": 30
        }
    ],
    "skills": ["UI", "UX", "Sales", "Marketing"]
    }

    if request.get("skills") is not None:
        pass
    elif request.get("personality") is not None:
        pass

async def find_by_skills(skills: list[str]):
    vector = "vector"
    embedding_data = {"limit_input": 8,"threshold_input": 0.7, "vector_input": str(vector)}

    #TODO Create the funcion in supabase
    top_matches = await db(path=f"/rpc/find_person_with_skills", data=embedding_data, method="post")

