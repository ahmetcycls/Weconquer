# app/api/v1/endpoints/project_endpoint.py
from fastapi import APIRouter, HTTPException
from app.domain.project.services import check_project_exists_for_user
from app.infrastructure.database.neo4j.repository_impl import create_projects_node_if_not_exists


router = APIRouter()

@router.post("/projects/")
async def create_project(user_id: int, project_data: dict):
    # Check if any project exists for the user in PostgreSQL
    if not await check_project_exists_for_user(user_id):
        raise HTTPException(status_code=404, detail="User not found or no projects exist for this user.")

    # Ensure the "Projects" node exists for this user in Neo4j
    create_projects_node_if_not_exists(user_id)

    # Proceed to create the new project in Neo4j and link it under the "Projects" node
    # This part would inv