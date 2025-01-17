import openai
import spacy
import pandas as pd
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Ensure spaCy model is installed
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading 'en_core_web_sm' model...")
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# OpenAI API Key
key_RAG = os.getenv("OPENAI_API_KEY")  # Add your OpenAI API key here
client = openai.OpenAI(api_key=key_RAG)

# File paths
csv_file = "cleaned_wiki_movie_plots.csv"
output_file = "test.json"

# Function to extract structured triplets (Subject, Relation, Object) for a single text
def extract_triplets(text):
    prompt = f"""
Extract structured relational triplets (Subject, Relation, Object) from the following text.
Ensure that:
- Each triplet follows the format: (Subject, Relation, Object).
- No missing objects; infer a reasonable object if necessary.
- Relations are semantically meaningful (avoid generic verbs like 'is', 'has', 'appears').
- Redundant or duplicate triplets are removed.
- Output is strictly a newline-separated list of triplets.

Text: {text}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=512
        )

        # Extract triplet response
        triplets_text = response.choices[0].message.content.strip()
        triplets = list(set(triplets_text.split("\n")))
        return triplets

    except Exception as e:
        print(f"Error during OpenAI API call: {e}")
        return None

# Function to get last processed index from JSON file
def get_last_processed_index():
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        with open(output_file, "r") as f:
            try:
                data = json.load(f)
                if data:
                    last_title = data[-1]["Title"]
                    return last_title
            except json.JSONDecodeError:
                return None
    return None

# Load cleaned dataset
df = pd.read_csv(csv_file)

# Determine starting index
last_title = get_last_processed_index()
if last_title:
    last_index = df[df["Title"] == last_title].index.max() + 1
else:
    last_index = 0  # Start from the beginning

# Process in batches of 5
batch_size = 10
triplet_data = []

for index in range(last_index, len(df), batch_size):
    batch = df.iloc[index : index + batch_size]
    texts = batch["Cleaned_Plot"].tolist()
    titles = batch["Title"].tolist()

    # Process each text iteratively and collect results
    for title, text in zip(titles, texts):
        triplets = extract_triplets(text)
        if triplets:
            triplet_data.append({
                "Title": title,
                "Triplets": triplets
            })

    # Append results to JSON file after processing each batch
    if triplet_data:
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            with open(output_file, "r") as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []

        existing_data.extend(triplet_data)

        with open(output_file, "w") as f:
            json.dump(existing_data, f, indent=4)

        print(f"Saved {len(triplet_data)} triplets. Last processed row: {batch.iloc[-1]['Title']}")

        # Clear batch memory
        triplet_data = []

print(f"Triplet extraction completed. Results saved to {output_file}")
