import json

def count_movies(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        movies = json.load(file)
    return len(movies)

# Example usage
json_file = "extracted_triplets.json"  # Replace with your actual JSON file path
print("Number of movies:", count_movies(json_file))