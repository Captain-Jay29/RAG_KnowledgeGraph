import openai
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import pickle
import os
from dotenv import load_dotenv
import fickling

load_dotenv()

# Load your movie dataset (assuming it's already cleaned)
movie_df = pd.read_csv("cleaned_wiki_movie_plots.csv")
my_api = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=my_api)

# Function to generate embeddings for the cleaned plot
def generate_embeddings(df, column_name="Cleaned_Plot"):
    """
    Generate embeddings for the specified column in the DataFrame.
    
    Args:
        df (pd.DataFrame): The movie DataFrame.
        column_name (str): The column to generate embeddings for.
    
    Returns:
        list: List of embeddings for the specified column.
    """
    # Use OpenAI embeddings to generate embedding for each movie plot
    embeddings = []
    for plot in df[column_name]:
        embedding = client.embeddings.create(input=[plot], model="text-embedding-ada-002")
        embeddings.append(embedding.data[0].embedding)
    
    return np.array(embeddings)

# Save embeddings to a file
def save_embeddings(embeddings, filename="movie_embeddings.pkl"):
    """
    Save the generated embeddings to a file for later use.
    
    Args:
        embeddings (np.ndarray): The generated embeddings.
        filename (str): The file to save embeddings.
    """
    with open(filename, "wb") as f:
        pickle.dump(embeddings, f)

# Load the pre-saved embeddings from file
def load_embeddings(filename="movie_embeddings.pkl"):
    """
    Load embeddings from a saved file.
    
    Args:
        filename (str): The file containing saved embeddings.
    
    Returns:
        np.ndarray: Loaded embeddings.
    """
    with open(filename, "rb") as f:
        embeddings = fickling.load(f)
    return embeddings

# Perform semantic search based on a query
def semantic_search(query, embeddings, movie_df, top_k=5):
    """
    Perform semantic search on the movie dataset based on a query.
    
    Args:
        query (str): The natural language query.
        embeddings (np.ndarray): The movie plot embeddings.
        movie_df (pd.DataFrame): The movie DataFrame.
        top_k (int): Number of top similar results to return.
    
    Returns:
        list: List of top-k most relevant movie titles and their similarity scores.
    """
    # Generate embedding for the query
    query_embedding = openai.Embedding.create(input=[query], model="text-embedding-ada-002")["data"][0]["embedding"]
    
    # Calculate cosine similarity between query embedding and movie plot embeddings
    similarities = cosine_similarity([query_embedding], embeddings)
    
    # Get top-k most similar movies
    top_k_indices = similarities[0].argsort()[-top_k:][::-1]
    
    # Return the movie titles and similarity scores
    return movie_df.iloc[top_k_indices][["Title", "Release Year", "Director", "Genre"]], similarities[0][top_k_indices]

def filter_directors_by_year(year, top_k=5):
    """
    Find directors who made more than one movie in a specific year by performing 
    semantic search and filtering the results.
    
    Args:
        year (int): The year for which to retrieve relevant directors.
        top_k (int): Number of top similar results to retrieve.

    Returns:
        list: Directors who made more than 1 movie in the specified year.
    """
    # Create a query for the specific year
    query = f"List all directors who made movies in the year {year}"
    
    # Perform semantic search
    relevant_movies, _ = semantic_search(query, embeddings, movie_df, top_k)
    
    # Filter movies for the specified year
    relevant_movies_year = relevant_movies[relevant_movies['Release Year'] == year]
    
    # Extract the directors from the filtered data
    directors = relevant_movies_year['Director'].tolist()
    
    # Count the number of movies for each director
    director_count = Counter(directors)
    
    # Find directors who made more than 1 movie in the specified year
    multi_movie_directors = [director for director, count in director_count.items() if count > 1]
    
    return multi_movie_directors

if __name__ == "__main__":
    # Generate embeddings and save them (only once)
    embeddings = generate_embeddings(movie_df)
    save_embeddings(embeddings)  # Save to file
    
    # Load the saved embeddings
    embeddings = load_embeddings()
    
    # Example query for directors who made more than one movie in the year 1925
    year = 1925
    directors_in_year = filter_directors_by_year(year)
    print(f"Directors who made more than 1 movie in {year}: {directors_in_year}")
