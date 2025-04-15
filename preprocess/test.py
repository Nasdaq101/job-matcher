import pandas as pd
import numpy as np

df = pd.read_csv('data/raw_data/postings.csv', quoting=1)
# Inspect the saved CSV file
saved_df = pd.read_csv('data/jobs_sample.csv')

print("\n--- SAVED DATA INSPECTION ---")
print(f"Total rows: {len(saved_df)}")
print(f"Columns: {saved_df.columns.tolist()}")