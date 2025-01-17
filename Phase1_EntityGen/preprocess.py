import pandas as pd
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download necessary NLTK data
nltk.download("punkt")
nltk.download("stopwords")

# Load stopwords once as a set (much faster lookup)
stop_words = set(stopwords.words("english"))

def clean_text(text):
    """
    Cleans text by:
    - Converting to lowercase
    - Removing special characters
    - Tokenizing into words
    - Removing stopwords
    """
    text = str(text).lower().strip()  # Lowercase and trim spaces
    text = re.sub(r'\W+', ' ', text)  # Remove special characters
    tokens = word_tokenize(text)  # Tokenization
    tokens = [word for word in tokens if word not in stop_words]  # Remove stopwords efficiently
    return " ".join(tokens)

# Load dataset
df = pd.read_csv("wiki_movie_plots.csv")

# Handle missing values
df["Cast"].fillna("Unknown", inplace=True)

# Apply text cleaning (using swifter for speed-up)
try:
    import swifter  # Install if not available
    df["Cleaned_Plot"] = df["Plot"].swifter.apply(clean_text)
except ImportError:
    print("Swifter not installed. Using standard apply (slower). Install with: pip install swifter")
    df["Cleaned_Plot"] = df["Plot"].apply(clean_text)

# Save cleaned dataset
df.to_csv("cleaned_wiki_movie_plots.csv", index=False)

print("Preprocessing complete! Cleaned data saved as 'cleaned_wiki_movie_plots.csv'.")