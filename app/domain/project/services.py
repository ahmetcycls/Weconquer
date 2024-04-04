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

from app.infrastructure.database.neo4j.neo4j_connection import neo4j_conn

async def fetch_graph_data_for_vis_js(project_node_id: str, user_id: str):
    query = """
    MATCH (user:User {userId: $user_id})-[:HAS_PROJECT]->(project:Project {projectNodeId: $project_node_id})
    OPTIONAL MATCH (project)-[:HAS_TASK*0..]->(task:Task)
    OPTIONAL MATCH (task)-[:HAS_TASK]->(subtask:Task)
    RETURN project AS project, collect(DISTINCT task) AS tasks, collect(DISTINCT {parent: task, child: subtask}) AS relationships
    """
    parameters = {"user_id": user_id, "project_node_id": project_node_id}
    results = neo4j_conn.query(query, parameters)
    formatted_results_for_vis_js = format_graph_data(results)
    formatted_results_for_vis_js["projectNodeId"] = project_node_id
    return formatted_results_for_vis_js

async def fetch_project_hierarchy(project_node_id: str, user_id: str):
    print(user_id)
    # Adjusted query to start with the User node
    query = """
        MATCH (user:User {userId: $user_id})-[:HAS_PROJECT]->(project:Project {projectNodeId: $project_node_id})
        OPTIONAL MATCH (project)-[:HAS_TASK*0..]->(task:Task)
        OPTIONAL MATCH (task)-[:HAS_TASK]->(subtask:Task)
        RETURN project AS project, collect(DISTINCT task) AS tasks, collect(DISTINCT {parent: task, child: subtask}) AS relationships
        """


    results = neo4j_conn.query(query, parameters={"user_id": user_id, "project_node_id": project_node_id})
    if not results or not results[0]['project']:
        return {"nodeId": None, "title": "", "subtasks": []}

    project = results[0]['project']
    tasks = results[0]['tasks']
    relationships = results[0]['relationships']

    task_map = {}
    for task in tasks:
        if task:  # Ensure the task is not None
            task_info = {"nodeId": task['nodeId'], "title": task.get('title', ""), "description": task.get('description', "")}
            # Only add the 'subtasks' key if there are subtasks for this task
            task_info["subtasks"] = []
            task_map[task['nodeId']] = task_info

    # Determine parent-child relationships
    for relation in relationships:
        parent = relation['parent']
        child = relation['child']
        if parent and child:
            # Append child to parent's 'subtasks' if not already present
            if "subtasks" not in task_map[parent['nodeId']]:
                task_map[parent['nodeId']]["subtasks"] = []
            task_map[parent['nodeId']]["subtasks"].append(task_map[child['nodeId']])

    # Filter out tasks that are actually subtasks from the top level
    top_level_tasks = [task for task in task_map.values() if not any(child['child'] and child['child']['nodeId'] == task['nodeId'] for child in relationships)]

    # Remove the 'subtasks' key from tasks that don't have any subtasks
    for task in task_map.values():
        if not task["subtasks"]:
            task.pop("subtasks", None)

    project_structure = {
        "nodeId": project.get("projectNodeId"),
        "title": project.get("name"),
        "subtasks": top_level_tasks,
        "description": project.get("description")
    }

    # Remove 'subtasks' key from the project if there are no top-level tasks
    if not project_structure["subtasks"]:
        project_structure.pop("subtasks", None)
    project_text_representation =await format_project_to_text(project_structure)

    project_text_representation = "SYSTEM DYNAMIC GRAPH MESSAGE: The current project state is as follows:\n\n" + project_text_representation
    return project_text_representation


async def format_project_to_text(project, indent=0):
    # Base indentation for this level
    base_indent = "    " * indent
    # Start building the string representation
    project_str = f'{base_indent}nodeId: {project["nodeId"]},\n'
    project_str += f'{base_indent}title: {project["title"]},\n'
    project_str += f'{base_indent}description: {project["description"]},\n'

    # Check if there are subtasks to process
    if "subtasks" in project and project["subtasks"]:
        project_str += f'{base_indent}subtasks: \n'
        # Iterate through each subtask and recursively format it
        for subtask in project["subtasks"]:
            project_str += await format_project_to_text(subtask, indent + 2)  # Increase indentation for subtasks
    else:
        # If there are no subtasks, remove the trailing comma from the title line
        project_str = project_str.rstrip(",\n") + "\n"

    return project_str

def format_graph_data(results):
    nodes = []
    edges = []

    # Process each record in the results
    for record in results:
        # Process the project node
        project = record['project']
        project_node_id = project['projectNodeId']  # Store project node ID for later use
        nodes.append({
            'id': project_node_id,
            'label': project.get('name', 'Unnamed Project'),
            'title': project.get('description', ''),
            'group': 'project'
        })

        # Process each task node
        tasks = record['tasks']
        task_ids = []  # Keep track of task IDs to determine top-level tasks
        for task in tasks:
            task_id = task['nodeId']
            task_ids.append(task_id)
            nodes.append({
                'id': task_id,
                'label': task.get('title', 'Unnamed Task'),
                'title': task.get('description', ''),
                'group': 'task',
                'status': task.get('status', ''),
                'assigned_to': task.get('assigned_to', 'Unassigned')
            })

        # Process relationships and identify top-level tasks
        top_level_tasks = set(task_ids)  # Start with all tasks as potentially top-level
        relationships = record['relationships']
        for rel in relationships:
            if rel['child'] is not None:  # Ensure there's a child task
                child_id = rel['child']['nodeId']
                parent_id = rel['parent']['nodeId']
                edges.append({
                    'from': parent_id,
                    'to': child_id
                })
                if child_id in top_level_tasks:
                    top_level_tasks.remove(child_id)  # Remove from top-level tasks as it has a parent

        # Add edges from project to each top-level task
        for task_id in top_level_tasks:
            edges.append({
                'from': project_node_id,
                'to': task_id
            })

    graph_data = {'nodes': nodes, 'edges': edges}
    return graph_data


# Assuming `project_data` is your hierarchical project structure
