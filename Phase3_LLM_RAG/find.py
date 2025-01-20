import pandas as pd

def find_short_plots(csv_file, max_tokens=512, num_movies=20):
    
    # Load the CSV file
    df = pd.read_csv(csv_file)

    # Check if the required column exists
    if 'Cleaned_Plot' not in df.columns:
        raise ValueError("Column 'Cleaned_Plot' not found in the CSV file.")

    # Filter plots with token count <= max_tokens
    short_plots = df[df['Cleaned_Plot'].apply(lambda x: len(str(x).split()) <= max_tokens)]

    # Select the first num_movies movies from the filtered results
    selected_movies = short_plots[['Title', 'Cleaned_Plot']].head(num_movies)

    if selected_movies.empty:
        print("No movies found with plots under the token limit.")
    else:
        print(f"Found {len(selected_movies)} movies with plots ≤ {max_tokens} tokens:\n")
        for index, row in selected_movies.iterrows():
            print(f"Title: {row['Title']}\nPlot Length: {len(str(row['Cleaned_Plot']).split())} tokens\n")
    
    return selected_movies

# Run the function with your file
csv_file_path = "/Users/jay/Desktop/The File/Learn/RAG/Recommender/cleaned_wiki_movie_plots.csv"  # Update with the correct path if needed
short_movies = find_short_plots(csv_file_path)

# Save the results to a new CSV
if not short_movies.empty:
    short_movies.to_csv("short_movie_plots.csv", index=False)
    print("\nShort movie plots saved to 'short_movie_plots.csv'.")
