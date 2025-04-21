import os
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle

# Load your cleaned data
df = pd.read_csv('data/jobs_sample.csv')

# Initialize the sentence transformer model
# This is a good general-purpose model for semantic search
model = SentenceTransformer('TechWolf/JobBERT-v2')

# Create individual embeddings
print("Creating embeddings...")

title_emb = model.encode(df['title_normalized'].tolist(), 
                         show_progress_bar=True, batch_size=32)
location_emb = model.encode(df['location_normalized'].tolist(), 
                            show_progress_bar=True, batch_size=32)
skills_emb = model.encode(df['combined_skills'].tolist(), 
                          show_progress_bar=True, batch_size=32)


# Define weights
TITLE_WEIGHT = 0.2
LOCATION_WEIGHT = 0.7
SKILLS_WEIGHT = 0.1

# Compute weighted sum
embeddings = TITLE_WEIGHT * title_emb + LOCATION_WEIGHT * location_emb + SKILLS_WEIGHT * skills_emb

# Save the embeddings to a file for later use
os.makedirs('data/tmp', exist_ok=True)
with open('data/tmp/job_embeddings.pkl', 'wb') as f:
    pickle.dump(embeddings, f)

print(f"Created and saved {len(embeddings)} embeddings with dimension {embeddings.shape[1]}")

# You can also add the embeddings to your dataframe if needed
# This converts the numpy arrays to lists for easier storage in a CSV
df['embedding'] = embeddings.tolist()

# Optional: Save the updated dataframe
df.to_pickle('data/tmp/linkedin_jobs_with_embeddings.pkl')

print("Process completed!")