import openai
from neo4j import GraphDatabase
import re
from dotenv import load_dotenv
import os
import reprlib

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
                - Ensure `OPTIONAL MATCH` is used correctly to avoid missing data issues.
                - Values for entities can be lower case or upper case, check for values in e1 and e2 both.

                 **Query Optimization Guidelines:**
                - Ensure the query returns only the necessary data without redundancy.
                - Use `OPTIONAL MATCH` for relationships to avoid null errors.
                - Avoid using `extract` inside `collect`; instead, directly retrieve the relationship attribute.
                - Optimize for single-hop and multi-hop queries.
                - Handle queries related to movie recommendations and thematic searches efficiently.
                - For summaries, retrieve all relevant triplet entities without exposing raw data.

                Ensure a correct working query is returned with valid Cypher syntax.  
                """
    response = client.chat.completions.create(
        # model="gpt-4o-realtime-preview-2024-12-17",
        model = "gpt-4o-mini",
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

        try:
            result = session.run(cypher_query)
        
        except Exception as e:
            print(f"An error occurred running the cypher query: {e}")
            return
        for record in result:
            results.append(record.values())
    driver.close()
    return results

def clean_retrieved_results(query, result):

    '''Gets the retrieved answer from Neo4j and passes back to the LLM to produce an intelligent output'''
    my_api = os.getenv("OPENAI_API_KEY")
    client = openai.OpenAI(api_key=my_api)
    prompt = f"""You are an intelligent movie knowledge assistant.
                 Based on the given query and the retrieved results from a Neo4j movie knowledge graph, format a clear and informative response.

                 **Query:** {query}
                 **Fetched Results:** {result}

                 **Response Guidelines:**
                 - If the query is about directors, list their movies concisely.
                 - If the query is about genres, provide relevant movie recommendations.
                 - If the query requests a summary, generate a well-structured paragraph describing the movie plot without exposing raw data.
                 - If the query is thematic, explain how the retrieved movies relate to the theme.
                 - Keep the response informative and engaging for the user.

                 Provide the structured response below: 
              """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert in Neo4j Cypher queries."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


def main():
    test_query1 = "Find all movies directed by Robert Z. Leonard."
    q2 = "Find out which movie did director Robert Z. Leonard direct in the year 1921"
    q3 = "Find out all movies directored by Robert Z. Leonard"
    q_multi2 = "List all directors which made more than 1 movies in the year 1925"
    q_recc = "Suggest top 5 WAR movies"
    q_sim = 'Suggest 5 movies similar to the movie The Black Viper'
    q_desc = 'Suggest movies which has an Irish man or Irish based theme'
    q_summ = "Summarize the movie Terrible Teddy, the Grizzly King"
    
    cypher_query = get_cypher_query(q_summ)

    print(f"\nUnstructured Query:\n{q_summ}")
    print(f"\nGenerated Cypher Query:\n{cypher_query}")
    
    results = execute_cypher_query(cypher_query)
    final_response = clean_retrieved_results(q_summ, results) if results else "No results found"

    print("\nQuery Results:")
    print(reprlib.repr(results))

    print(f'\n****** Final Output ******')
    print(final_response)


if __name__ == "__main__":
    main()
