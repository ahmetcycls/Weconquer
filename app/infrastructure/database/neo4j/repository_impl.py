# app/infrastructure/database/neo4j/repository_impl.py

from app.infrastructure.database.neo4j.neo4j_connection import neo4j_conn

def create_projects_node_if_not_exists(user_id: int):
    query = """
    MERGE (u:User {userId: $userId})
    MERGE (u)-[:HAS]->(p:Projects)
    RETURN p
    """
    with neo4j_conn.session() as session:
        session.run(query, userId=user_id)