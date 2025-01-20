import pandas as pd
import numpy as np
import openai
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rouge_score import rouge_scorer

# Load the cleaned wiki movie plot dataset
def load_movie_data(file_path):
    """Load the CSV file containing movie plots."""
    df = pd.read_csv(file_path)
    return df[['Title', 'Plot']]

# Function to retrieve the original plot for a given movie title
def get_original_plot(title, df):
    """Retrieve the original cleaned plot for a given movie title."""
    row = df[df['Title'].str.lower() == title.lower()]
    if not row.empty:
        return row.iloc[0]['Plot']
    else:
        return None

# Function to calculate TF-IDF cosine similarity
def calculate_similarity(original_plot, generated_plot):
    """Calculate cosine similarity between original and generated plots."""
    vectorizer = TfidfVectorizer(stop_words='english')
    vectors = vectorizer.fit_transform([original_plot, generated_plot])
    similarity = cosine_similarity(vectors[0], vectors[1])
    return similarity[0][0]

# Function to calculate ROUGE scores
def calculate_rouge(original_plot, generated_plot):
    """Calculate ROUGE-1, ROUGE-2, and ROUGE-L scores for summary evaluation."""
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    scores = scorer.score(original_plot, generated_plot)
    rouge_scores = {
        'ROUGE-1': scores['rouge1'].fmeasure,
        'ROUGE-2': scores['rouge2'].fmeasure,
        'ROUGE-L': scores['rougeL'].fmeasure
    }
    return rouge_scores

# Main function to compare LLM output with original plots
def compare_plots(movie_title, generated_plot, csv_path):
    """Compare LLM-generated plot with the original movie plot from dataset."""
    df = load_movie_data(csv_path)
    original_plot = get_original_plot(movie_title, df)
    
    if original_plot is None:
        return f"Movie '{movie_title}' not found in the dataset."

    # Calculate similarity metrics
    similarity_score = calculate_similarity(original_plot, generated_plot)
    rouge_scores = calculate_rouge(original_plot, generated_plot)

    results = {
        "Movie Title": movie_title,
        "Cosine Similarity": round(similarity_score, 4),
        "ROUGE-1 Score": round(rouge_scores['ROUGE-1'], 4),
        "ROUGE-2 Score": round(rouge_scores['ROUGE-2'], 4),
        "ROUGE-L Score": round(rouge_scores['ROUGE-L'], 4)
    }

    print(f'\nlen of orig plot: {len(original_plot)}, len of orig plot: {len(generated_plot)}\n\n')

    print(f"Original Plot:\n{original_plot}\n")
    print(f"Generated Plot:\n{generated_plot}\n")

    return results

# Example usage
if __name__ == "__main__":
    # Example movie title and LLM-generated plot
    movie_title = "Terrible Teddy, the Grizzly King"
    generated_plot = f"" # Add your generated plot here
    csv_file_path = "/Users/jay/Desktop/The File/Learn/RAG/Recommender/wiki_movie_plots.csv"
    comparison_results = compare_plots(movie_title, generated_plot, csv_file_path)
    
    print("Comparison Results:")
    for key, value in comparison_results.items():
        print(f"{key}: {value}")
