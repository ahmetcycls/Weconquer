from app.domain.user.models import User
from app.infrastructure.database.relational_db import db

async def get_user_data(user_id: str):
    query = f"users?auth_provider_id=eq.{user_id}"

    db_response = await db(path = query, method = "get")
    print(db_response.json())
    return User(**db_response.json()[0])


import shortuuid
from ...infrastructure.database.neo4j.neo4j_connection import Neo4jConnection
neo4j_conn = Neo4jConnection(uri="bolt://localhost:7687", user="neo4j", password="Qgqus4uq")


def create_project_for_user(user_id: str, description: str, name: str):
    user_node_id = shortuuid.ShortUUID().random(length=10)
    project_node_id = shortuuid.ShortUUID().random(length=10)

    # This query ensures a User node exists for the given user_id, then creates a new Project node each time.
    query = f"""
    MERGE (user:User {{userId: '{user_id}'}})
    ON CREATE SET user.nodeId = '{user_node_id}'
    WITH user
    CREATE (user)-[:HAS_PROJECT]->(project:Project {{projectNodeId: '{project_node_id}', description: '{description}', name: '{name}'}})
    RETURN project.projectNodeId AS projectNodeId, project.description AS description, project.name AS name
    """

    result = neo4j_conn.query(query)
    return result  # Return the shortIds of the user and the newly created project.