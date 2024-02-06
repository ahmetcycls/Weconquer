# app/api/v1/endpoints/project_endpoint.py
from fastapi import APIRouter, HTTPException, FastAPI, Request
from app.domain.project.services import check_project_exists_for_user
from app.infrastructure.database.neo4j.repository_impl import create_projects_node_if_not_exists
from app.infrastructure.database.neo4j.neo4j_connection import neo4j_conn


router = APIRouter()
@router.get("/test-neo4j")
def get_projects():
    query = "MATCH (projects:Project) RETURN projects"
    try:
        projects = neo4j_conn.query(query)
        print(projects)
        projects = [dict(project['projects']) for project in projects]  # Adjust based on your data structure
        return {"projects": projects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # [ < Record
    # projects = < Node
    # element_id = '4:9ea1d287-3096-4709-a488-b3602ec4e124:0'
    # labels = frozenset({'Project'})
    # properties = {'name': 'First Project', 'description': 'This is a sample project.', 'projectId': 'project1'} >>]
@router.post("/projects/")
async def create_project(user_id: int, project_data: dict):
    # Check if any project exists for the user in PostgreSQL
    if not await check_project_exists_for_user(user_id):
        raise HTTPException(status_code=404, detail="User not found or no projects exist for this user.")

    # Ensure the "Projects" node exists for this user in Neo4j
    create_projects_node_if_not_exists(user_id)

    # Proceed to create the new project in Neo4j and link it under the "Projects" node
    # This part would inv