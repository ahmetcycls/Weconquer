from neo4j import GraphDatabase

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def query(self, query, parameters=None, db=None):
        with self.driver.session(database=db) as session:
            return session.run(query, parameters)

# Example usage
neo4j_conn = Neo4jConnection("neo4j://localhost:7687", "username", "password")
