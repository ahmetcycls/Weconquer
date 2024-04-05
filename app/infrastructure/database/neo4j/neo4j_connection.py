from neo4j import GraphDatabase
from neo4j import AsyncGraphDatabase
class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def query(self, query, parameters=None, db=None):
        with self.driver.session(database=db) as session:
            result = session.run(query, parameters)
            # Fetch and return list of records within the session context
            return [record for record in result]

class AsyncNeo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def close(self):
        await self.driver.close()

    async def query(self, query, parameters=None, db=None):
        async with self.driver.session(database=db) as session:
            result = await session.run(query, parameters)
            return [record async for record in result]

# Example usage
neo4j_conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "Qgqus4uq")
