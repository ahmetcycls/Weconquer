# app/api/v1/endpoints/project_endpoint.py
from fastapi import APIRouter, HTTPException, FastAPI, Request
from app.domain.project.services import check_project_exists_for_user, get_project_with_tasks
from app.domain.user.repository_impl import create_project_for_user
from app.infrastructure.database.neo4j.neo4j_connection import neo4j_conn
from pydantic import BaseModel


router = APIRouter()


# Assuming the necessary imports and neo4j_conn initialization

@router.get("/{project_node_id}/readable_format")
def get_project_graph_in_readable_format(project_node_id: str):
    print(project_node_id)
    project_data = get_project_with_tasks(project_node_id)
    if not project_data:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_data

@router.get("/")
def get_projects():
    query = "MATCH (projects:Project) RETURN projects"
    try:
        projects = neo4j_conn.query(query)
        print(projects)
        projects = [dict(project['projects']) for project in projects]  # Adjust based on your data structure
        return {"projects": projects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ProjectCreateRequest(BaseModel):
    user_id: str
    description: str
    name: str

@router.post("/create/")
def create_project(payload: ProjectCreateRequest):
    try:
        result = create_project_for_user(payload.user_id ,payload.description, payload.name)
        return {"message": "Project created successfully", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Proceed to create the new project in Neo4j and link it under the "Projects" node
    # This part would inv
