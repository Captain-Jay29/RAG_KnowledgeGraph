from neo4j import GraphDatabase
import json
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# Change these based on your setup
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# File paths
JSON_FILE = "cleaned_triplets.json"
CSV_FILE = "cleaned_wiki_movie_plots.csv"

# Load JSON data
with open(JSON_FILE, "r") as f:
    movie_data = json.load(f)

# Load CSV data
df = pd.read_csv(CSV_FILE)

# Convert CSV to a lookup dictionary for metadata
print(f'gathering metadata ....')
df_unique = df.drop_duplicates(subset="Title", keep="first")
csv_metadata = df_unique.set_index("Title")[["Release Year", "Director", "Genre"]].to_dict(orient="index")
print("done")

def upload_graph(tx, movie_title, triplets, metadata):
    """Creates nodes and relationships for a single movie in Neo4j, including summary and triplets."""
    query = """
    MERGE (m:Movie {title: $title, year: $year})
    MERGE (d:Director {name: $director})
    MERGE (m)-[:HAS_DIRECTOR]->(d)
    
    MERGE (g:Genre {name: $genre})
    MERGE (m)-[:BELONGS_TO_GENRE]->(g)
    
    // Create a summary node for the movie
    MERGE (s:Summary {title: $title})
    MERGE (m)-[:HAS_SUMMARY]->(s)
    
    WITH m, s
    UNWIND $triplets AS triplet
    MERGE (e1:Entity {name: triplet.subject})
    MERGE (e2:Entity {name: triplet.object})
    MERGE (e1)-[r:ACTS {relation: triplet.relation}]->(e2)
    
    // Link triplet entities to the summary
    MERGE (s)-[:CONTAINS]->(e1)
    MERGE (s)-[:CONTAINS]->(e2)
    """
    
    tx.run(query, title=movie_title, 
                  year=metadata["Release Year"], 
                  director=metadata["Director"], 
                  genre=metadata["Genre"], 
                  triplets=triplets)

def validate_triplets(triplets):
    """Filters out invalid triplets that don't have exactly 3 elements."""
    valid_triplets = []
    
    for triplet in triplets:
        if isinstance(triplet, list) and len(triplet) == 3:
            subject, relation, object_ = triplet
            if all(isinstance(x, str) and x.strip() for x in [subject, relation, object_]):
                valid_triplets.append({"subject": subject, "relation": relation, "object": object_})
    
    return valid_triplets

def main():
    """Main function to connect to Neo4j and upload the graph."""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    with driver.session() as session:
        for i, movie in enumerate(movie_data[:2000]):  # Only process first 2000 movies
            title = movie["Title"]
            raw_triplets = movie["Triplets"]
            
            if title in csv_metadata:
                metadata = csv_metadata[title]
                
                # Validate and filter triplets
                triplets = validate_triplets(raw_triplets)
                
                if triplets:
                    session.execute_write(upload_graph, title, triplets, metadata)
                    print(f"Uploaded {i+1}/2000: {title} ({len(triplets)} valid triplets)")
                else:
                    print(f"Skipping {title} (No valid triplets)")
            else:
                print(f"Skipping {title} (metadata not found in CSV)")

    driver.close()

if __name__ == "__main__":
    main()
