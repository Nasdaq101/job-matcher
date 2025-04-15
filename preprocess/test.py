import pandas as pd
import numpy as np

df = pd.read_csv('data/raw_data/postings.csv', quoting=1)
# Inspect the saved CSV file
saved_df = pd.read_csv('data/jobs_sample.csv')

print("\n--- SAVED DATA INSPECTION ---")
print(f"Total rows: {len(saved_df)}")
print(f"Columns: {saved_df.columns.tolist()}")

# Check if any columns were dropped during saving
if set(df_sample.columns) != set(saved_df.columns):
    print("Warning: Some columns missing in saved data!")
    print(f"Missing: {set(df_sample.columns) - set(saved_df.columns)}")

# Check if lists were properly saved (they might be converted to strings)
if 'extracted_skills' in saved_df.columns:
    sample_skills = saved_df['extracted_skills'].iloc[0]
    print(f"\nSample extracted_skills: {sample_skills}")
    print(f"Type: {type(sample_skills)}")
    
    # If they're saved as strings but should be lists, you might need to convert:
    if isinstance(sample_skills, str):
        print("Note: Skills saved as strings, not lists. You may need to convert them back to lists.")