import openai
from neo4j import GraphDatabase
import re
from dotenv import load_dotenv
import os

load_dotenv()

# Change these based on your setup
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

def get_cypher_query(nl_query):
    """Uses GPT-4 to convert natural language query to Cypher."""

    my_api = os.getenv("OPENAI_API_KEY")
    client = openai.OpenAI(api_key=my_api)
    prompt = f"""Convert the following natural language query into a Cypher query based on a movie knowledge graph:  
                '{nl_query}'  

                Ensure the schema of this graph is followed:
                - Movies are linked to directors: `(m:Movie)-[:HAS_DIRECTOR]->(d:Director)`
                - Movie node has attributes year and title
                - Movies are linked to genres: `(m:Movie)-[:BELONGS_TO_GENRE]->(g:Genre)`
                - All genres have names in lowercase
                - Movies are linked to a summary containing extracted knowledge triplets: `(m)-[:HAS_SUMMARY]->(s:Summary)`
                - Each summary node is connected to triplet entities: `(s)-[:CONTAINS]->(e1)` and `(s)-[:CONTAINS]->(e2)`
                - Triplet entities are connected through relationships labeled `ACTS` with an attribute `relation` representing the connection between them:  
                `(e1)-[:ACTS relation: <relation_value>]->(e2)`
                - Values for entities can be lower case or upper case, check for values in e1 and e2 both. 

                Generate a correct Cypher query that follows this schema. 
                """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert in Neo4j Cypher queries."},
            {"role": "user", "content": prompt}
        ]
    )
    llm_response = response.choices[0].message.content
    match = re.search(r"```cypher\n(.*?)\n```", llm_response, re.DOTALL)

    if match:
        cypher_query = match.group(1).strip()
    else:
        raise ValueError("Failed to extract Cypher query from LLM response.")

    return cypher_query

def execute_cypher_query(cypher_query):
    """Executes a Cypher query on Neo4j."""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    results = []
    with driver.session() as session:
        result = session.run(cypher_query)
        for record in result:
            results.append(record.values())
    driver.close()
    return results

def main():
    test_query1 = "Find all movies directed by Robert Z. Leonard."
    q2 = "Find out which movie did director Robert Z. Leonard direct in the year 1921"
    q3 = "Find out all movies directored by Robert Z. Leonard"
    q_multi2 = "List all directors which made more than 1 movies in the year 1925"
    q_recc = "Suggest top 5 WAR movies"
    q_sim = 'Suggest 5 movies similar to the movie The Black Viper'
    q_desc = 'Suggest movies which has an Irish man or Irish based theme'
    
    
    cypher_query = get_cypher_query(q_desc)

    print(f"\nUnstructured Query:\n{q_desc}")

    print(f"\nGenerated Cypher Query:\n{cypher_query}")
    
    results = execute_cypher_query(cypher_query)
    print("\nQuery Results:")
    ind = 1
    for i, j in results:
        print(f'{ind}. {i} in {j}')
        ind += 1
    print()

if __name__ == "__main__":
    main()
