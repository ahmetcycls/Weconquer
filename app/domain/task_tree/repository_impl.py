from typing import List, Dict, Optional
import shortuuid
from ...infrastructure.database.neo4j.neo4j_connection import Neo4jConnection

# Assuming neo4j_conn is globally accessible in this module or passed appropriately

neo4j_conn = Neo4jConnection(uri="bolt://localhost:7687", user="neo4j", password="Qgqus4uq")

# Make sure neo4j_conn is correctly initialized
def generate_unique_short_id() -> str:
    return shortuuid.ShortUUID().random(length=10)


def create_task_under_node(user_id: str, project_node_id: str, tasks: List[Dict], parent_node_id: Optional[str] = None) -> List[str]:
    results = []

    for task in tasks:
        node_id = generate_unique_short_id()
        task_properties = {k: v for k, v in task.items() if k != 'subtasks'}
        properties_str = ", ".join(f"{k}: '{v}'" if isinstance(v, str) else f"{k}: {v}" for k, v in task_properties.items())

        if parent_node_id:
            # Linking task to another task
            parent_match_query = f"MATCH (parent:Task {{nodeId: '{parent_node_id}'}})"
        else:
            # Linking task directly to a project
            parent_match_query = f"MATCH (parent:Project {{projectNodeId: '{project_node_id}'}})"

        query = f"""
        {parent_match_query}
        CREATE (parent)-[:HAS_TASK]->(task:Task {{nodeId: '{node_id}', {properties_str}}})
        RETURN task.nodeId AS nodeId
        """
        parameters = {"nodeId": node_id, **task_properties}
        result = neo4j_conn.query(query, parameters)

        if result:
            new_task_node_id = result[0]["nodeId"]
            results.append(new_task_node_id)

            # Handling subtasks recursively
            subtasks = task.get('subtasks', [])
            if subtasks:
                subtask_results = create_task_under_node(user_id, project_node_id, subtasks, new_task_node_id)
                results.extend(subtask_results)

    return results




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