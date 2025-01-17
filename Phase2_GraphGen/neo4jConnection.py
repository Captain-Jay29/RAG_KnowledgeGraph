from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

# Change these based on your setup
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def test_connection(tx):
    result = tx.run("MATCH (n) RETURN count(n) AS node_count")
    for record in result:
        print("Total Nodes:", record["node_count"])

# Test the connection
with driver.session() as session:
    session.execute_read(test_connection)