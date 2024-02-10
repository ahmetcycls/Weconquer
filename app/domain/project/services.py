# app/domain/project/services.py
from app.infrastructure.database.neo4j.neo4j_connection import neo4j_conn
from typing import Optional
from app.infrastructure.database.relational_db.db import db
from typing import Dict

async def check_project_exists_for_user(user_id: int) -> bool:
    # Assuming you have a function in `db` to query PostgreSQL
    # Adjust `path` and `method` according to your API design
    response = await db(path=f"projects?user_id=eq.{user_id}", method="get")
    return len(response) > 0


def get_project_with_tasks(project_node_id: str) -> dict:
    query = """
    MATCH (p:Project {projectNodeId: $project_node_id})
    OPTIONAL MATCH (p)-[:HAS_TASK*]->(t:Task)
    WITH p, collect(t) AS tasks
    RETURN p AS project, tasks
    """
    results = neo4j_conn.query(query, parameters={"project_node_id": project_node_id})

    if not results or not results[0]['project']:
        return {"nodeId": None, "title": "", "subtasks": []}

    # Initialize project structure with basic details
    project_node = results[0]['project']
    project_structure = {
        "nodeId": project_node["projectNodeId"],
        "title": project_node.get("name", ""),  # Assuming 'name' holds the project title
        "subtasks": []
    }

    tasks = results[0]['tasks']
    task_dict = {task['nodeId']: {"nodeId": task['nodeId'], "title": task.get('title', ""), "subtasks": []} for task in
                 tasks if task}

    # Assuming all tasks are direct children of the project (simplification)
    for task in tasks:
        if task:  # Ensure task is not None
            # Here, you would need logic to determine a task's parent if it's not the project
            # For simplicity, adding all tasks directly under the project
            project_structure["subtasks"].append(task_dict[task['nodeId']])

    return project_structure

