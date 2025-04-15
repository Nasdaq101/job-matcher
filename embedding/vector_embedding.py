import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle

# Load your cleaned data
df = pd.read_csv('data/jobs_sample.csv')

# Initialize the sentence transformer model
# This is a good general-purpose model for semantic search
model = SentenceTransformer('all-MiniLM-L6-v2')

# Create embeddings for each job listing
print("Creating embeddings for job listings...")
embeddings = model.encode(df['combined_text'].tolist(), 
                          show_progress_bar=True, 
                          batch_size=32)

# Save the embeddings to a file for later use
with open('job_embeddings.pkl', 'wb') as f:
    pickle.dump(embeddings, f)

print(f"Created and saved {len(embeddings)} embeddings with dimension {embeddings.shape[1]}")

# You can also add the embeddings to your dataframe if needed
# This converts the numpy arrays to lists for easier storage in a CSV
df['embedding'] = embeddings.tolist()

# Optional: Save the updated dataframe
df.to_pickle('linkedin_jobs_with_embeddings.pkl')

print("Process completed!")