import pandas as pd

df = pd.read_csv("cleaned_wiki_movie_plots.csv")

# Compare original vs cleaned for the first few rows
for i in range(5):  # Check first 5 rows
    print(f"Original: {df['Plot'][i]}")
    print(f"\nCleaned:  {df['Cleaned_Plot'][i]}")
    print("="*80)