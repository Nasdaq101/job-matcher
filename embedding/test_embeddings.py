import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle

# Load your dataset
df = pd.read_csv('data/jobs_sample.csv')

# Load the embeddings you previously created
with open('job_embeddings.pkl', 'rb') as f:
    embeddings = pickle.load(f)

# Make sure embeddings and dataframe align
assert len(df) == len(embeddings), "Number of embeddings doesn't match number of rows in dataframe"

# Get a sample job (the .NET Developer)
sample_job_idx = 5  # Index of .NET Developer job in your example
sample_job = df.iloc[sample_job_idx]
sample_embedding = embeddings[sample_job_idx]

# Calculate cosine similarity with all other jobs
similarities = cosine_similarity([sample_embedding], embeddings)[0]

# Get the top 5 most similar jobs (excluding itself)
similar_indices = np.argsort(similarities)[::-1][1:6]  # Top 5 excluding itself
similar_jobs = df.iloc[similar_indices]

print(f"Sample job: {sample_job['title_clean']} at {sample_job['company_name']}")
print("\nTop 5 similar jobs:")
for i, job in similar_jobs.iterrows():
    sim_score = similarities[i]
    print(f"{job['title_clean']} at {job['company_name']} (Similarity: {sim_score:.4f})")