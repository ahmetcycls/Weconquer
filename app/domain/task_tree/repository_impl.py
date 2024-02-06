# app/domain/task_tree/repository_impl.py
import shortuuid
from ...infrastructure.database.neo4j.neo4j_connection import Neo4jConnection

neo4j_conn = Neo4jConnection(uri="bolt://localhost:7687", user="neo4j", password="Qgqus4uq")


def generate_unique_short_id():
    return shortuuid.ShortUUID().random(length=10)


def create_task_under_node(parent_short_id: str, task_details: dict):
    short_id = generate_unique_short_id()
    # Prepare the properties for the new task, excluding 'subtasks' if present
    task_properties = {k: v for k, v in task_details.items() if k != 'subtasks'}
    properties_str = ', '.join(f"{k}: '{v}'" if isinstance(v, str) else f"{k}: {v}" for k, v in task_properties.items())

    # The Cypher query to create a new task node linked to the specified parent node by its shortId
    query = f"""
    MATCH (parent)
    WHERE parent.shortId = '{parent_short_id}'
    CREATE (parent)-[:HAS_TASK]->(newTask:Task {{shortId: '{short_id}', {properties_str}}})
    RETURN newTask.shortId AS shortId
    """
    parameters = {"parent_short_id": parent_short_id, **task_properties}
    result = neo4j_conn.query(query, parameters)
    new_task_short_id = result[0]['shortId']

    # If there are nested subtasks, recursively create them under the new task
    for subtask in task_details.get('subtasks', []):
        create_task_under_node(new_task_short_id, subtask)

    return new_task_short_id
def update_task_by_short_id(short_id: str, update_details: dict):
    set_clauses = ", ".join([f"n.{key} = ${key}" for key in update_details.keys()])
    query = f"""
    MATCH (n:Task) WHERE n.shortId = $short_id
    SET {set_clauses}
    RETURN n
    """
    parameters = {"short_id": short_id, **update_details}
    result = neo4j_conn.query(query, parameters)
    return result
