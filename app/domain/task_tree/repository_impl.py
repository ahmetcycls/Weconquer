from typing import List, Dict, Optional
import shortuuid
from ...infrastructure.database.neo4j.neo4j_connection import Neo4jConnection

# Assuming neo4j_conn is globally accessible in this module or passed appropriately

neo4j_conn = Neo4jConnection(uri="bolt://localhost:7687", user="neo4j", password="Qgqus4uq")

# Make sure neo4j_conn is correctly initialized
def generate_unique_short_id() -> str:
    return shortuuid.ShortUUID().random(length=10)


def create_task_under_node(user_id: str, project_node_id: str, tasks: List[Dict],
                           parent_node_id: Optional[str] = None) -> List[str]:
    results = []

    for task in tasks:
        node_id = generate_unique_short_id()
        # Filter out 'subtasks' from the task properties
        task_properties = {k: v for k, v in task.items() if k != 'subtasks'}

        # Dynamically build the SET part of the query based on provided task properties
        set_clauses = ", ".join(f"task.{k} = ${k}" for k in task_properties.keys())

        if parent_node_id:
            parent_match_query = "MATCH (parent:Task {nodeId: $parentNodeId})"
        else:
            parent_match_query = "MATCH (parent:Project {projectNodeId: $projectNodeId})"

        query = f"""
        {parent_match_query}
        CREATE (parent)-[:HAS_TASK]->(task:Task {{nodeId: $nodeId}})
        SET {set_clauses}
        RETURN task.nodeId AS nodeId
        """

        parameters = {"nodeId": node_id, **task_properties}
        if parent_node_id:
            parameters["parentNodeId"] = parent_node_id
        else:
            parameters["projectNodeId"] = project_node_id

        result = neo4j_conn.query(query, parameters=parameters)
        print(result)
        if result and result[0]:
            new_task_node_id = result[0]["nodeId"]
            results.append(new_task_node_id)

            # Handle subtasks recursively, if any
            subtasks = task.get('subtasks', [])
            if subtasks:
                subtask_results = create_task_under_node(user_id, project_node_id, subtasks, new_task_node_id)
                results.extend(subtask_results)

    return results

def create_task_under_node_manual(user_id: str, project_node_id: str, tasks: List[Dict],
                           parent_node_id: Optional[str] = None, sio=None, sid=None):
    results = []
    is_project_node = False
    if project_node_id == parent_node_id:
        is_project_node = True
        parent_node_id = None

    for task in tasks:
        node_id = generate_unique_short_id()
        # Filter out 'subtasks' from the task properties
        task_properties = {k: v for k, v in task.items() if k != 'subtasks'}

        # Dynamically build the SET part of the query based on provided task properties
        set_clauses = ", ".join(f"task.{k} = ${k}" for k in task_properties.keys())

        if parent_node_id:
            parent_match_query = "MATCH (parent:Task {nodeId: $parentNodeId})"
        else:
            parent_match_query = "MATCH (parent:Project {projectNodeId: $projectNodeId})"

        query = f"""
        
        {parent_match_query}
        CREATE (parent)-[:HAS_TASK]->(task:Task {{nodeId: $nodeId}})
        SET {set_clauses}
        RETURN task.nodeId AS nodeId
        """

        parameters = {"nodeId": node_id, **task_properties}
        if parent_node_id:
            parameters["parentNodeId"] = parent_node_id
        else:
            parameters["projectNodeId"] = project_node_id

        result = neo4j_conn.query(query, parameters=parameters)
        print(result)
        if result and result[0]:
            new_task_node_id = result[0]["nodeId"]
            results.append(new_task_node_id)

            # Handle subtasks recursively, if any
            subtasks = task.get('subtasks', [])
            if subtasks:
                subtask_results = create_task_under_node_manual(user_id, project_node_id, subtasks, new_task_node_id)
                results.extend(subtask_results)
    the_task = tasks[0]
    node_id_to_format = results[0]

    the_task["nodeId"] = node_id_to_format
    if is_project_node:
        the_task["edge"] = {"from": project_node_id, "to": node_id_to_format}
    else:
        the_task["edge"] = {"from": parent_node_id, "to": node_id_to_format}
    print(the_task)
    return the_task


def update_task_by_node_id(node_id: str, update_details: dict):
    set_clauses = ", ".join([f"n.{key} = ${key}" for key in update_details.keys()])
    query = f"""
    MATCH (n:Task) WHERE n.nodeId = $node_id
    SET {set_clauses}
    RETURN n
    """
    parameters = {"node_short_id": node_id, **update_details}
    result = neo4j_conn.query(query, parameters)
    return result

# def delete_node_and_subnodes(user_id: str, node_id: str, project_node_id: str):
#     query = """
#     MATCH (user:User {userId: $userId})-[:HAS_PROJECT]->(project {projectNodeId: $projectNodeId})
#     MATCH (project)-[:HAS_TASK*0..]->(parent)-[:HAS_TASK*0..]->(task:Task {nodeId: $nodeId})
#     WITH parent, task, COUNT(task) AS tasksToDelete
#     DETACH DELETE task
#     WITH parent, SUM(tasksToDelete) AS totalTasksToDelete
#     WHERE NOT EXISTS ((parent)-[:HAS_TASK]->())
#     DETACH DELETE parent
#     RETURN totalTasksToDelete > 0 AS deletionOccurred
#     """
#     parameters = {"userId": user_id, "nodeId": node_id, "projectNodeId": project_node_id}
#     result = neo4j_conn.query(query, parameters)
#     return result

def delete_node_and_subnodes(user_id: str, node_id: str, project_node_id: str):
    query = """
    MATCH (user:User {userId: $userId})-[:HAS_PROJECT]->(project {projectNodeId: $projectNodeId})
    OPTIONAL MATCH (project)-[:HAS_TASK*]->(task:Task {nodeId: $nodeId})
    WITH project, COLLECT(task) AS tasksToDelete
    CALL {
        WITH tasksToDelete
        UNWIND tasksToDelete AS taskToDelete
        DETACH DELETE taskToDelete
    }
    OPTIONAL MATCH (project)-[:HAS_TASK]->(remainingTask)
    WITH project, SIZE(tasksToDelete) > 0 AS deletionOccurred, COUNT(remainingTask) AS remainingTasks
    RETURN deletionOccurred, remainingTasks > 0 AS projectRetained
    """
    parameters = {"userId": user_id, "nodeId": node_id, "projectNodeId": project_node_id}
    result = neo4j_conn.query(query, parameters)
    return result
def delete_subnodes_and_their_relationships(user_id: str, project_node_id: str, node_id: str):
    print(project_node_id, node_id, "delete_subnodes_and_their_relationships")
    # Check if node_id is the same as project_node_id, indicating deletion beneath the project node
    if project_node_id == node_id:
        query = """
        MATCH (user:User {userId: $userId})-[:HAS_PROJECT]->(project {projectNodeId: $projectNodeId})
        OPTIONAL MATCH (project)-[:HAS_TASK*]->(subNode)
        WHERE subNode.nodeId <> $projectNodeId
        OPTIONAL MATCH (subNode)-[r]-()
        DETACH DELETE subNode
        RETURN COUNT(DISTINCT subNode) AS deletedSubNodes, COUNT(DISTINCT r) AS deletedRelationships
        """
    else:
        query = """
        MATCH (user:User {userId: $userId})-[:HAS_PROJECT]->(project {projectNodeId: $projectNodeId})
        MATCH (project)-[:HAS_TASK*0..]->(rootNode {nodeId: $nodeId})-[:HAS_TASK*]->(subNode)
        OPTIONAL MATCH (subNode)-[r]-()
        DETACH DELETE subNode
        RETURN COUNT(DISTINCT subNode) AS deletedSubNodes, COUNT(DISTINCT r) AS deletedRelationships
        """
    parameters = {"userId": user_id, "projectNodeId": project_node_id, "nodeId": node_id}
    result = neo4j_conn.query(query, parameters)
    return result
    #In the future for dynamic graph update after update instead of refreshing the whole graph
    # def delete_node_and_subnodes(user_id: str, node_id: str, project_node_id: str):
    #     query = """
    #     MATCH (user:User {userId: $userId})-[:HAS_PROJECT]->(project {projectNodeId: $projectNodeId})
    #     MATCH (project)-[:HAS_TASK*0..]->(parent)-[:HAS_TASK*0..]->(task:Task {nodeId: $nodeId})
    #     OPTIONAL MATCH (task)-[r]-()
    #     WITH task, COLLECT(r) AS relsToDelete, COLLECT(task) AS tasksToDelete, parent
    #     DETACH DELETE task
    #     WITH DISTINCT parent, tasksToDelete, relsToDelete
    #     WHERE NOT (parent)-[:HAS_TASK]->()
    #     DETACH DELETE parent
    #     RETURN project.projectNodeId as projectId, COUNT(DISTINCT tasksToDelete) AS deletedTasks, COUNT(DISTINCT relsToDelete) AS deletedRelationships
    #     """
    #     parameters = {"userId": user_id, "nodeId": node_id, "projectNodeId": project_node_id}
    #     result = neo4j_conn.query(query, parameters)
    #     return result
