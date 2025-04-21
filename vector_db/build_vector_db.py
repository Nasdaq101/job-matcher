import chromadb
import pandas as pd
import pickle
import numpy as np
import os

def build_vector_database():
    print("Building vector database...")
    
    # Define database path - could be from environment variable for flexibility
    db_path = os.environ.get("CHROMA_DB_PATH", "./chroma_db")
    
    # Check if the database already exists
    if os.path.exists(db_path) and os.listdir(db_path):
        print("Database already exists. Skipping build.")
        return
    
    # Create directory if it doesn't exist
    os.makedirs(db_path, exist_ok=True)
    
    # Load your data with error handling
    try:
        print("Loading job data and embeddings...")
        df = pd.read_pickle('data/tmp/linkedin_jobs_with_embeddings.pkl')
    except Exception as e:
        print(f"Error loading data: {e}")
        raise

    # Initialize Chroma client
    print(f"Initializing Chroma database at {db_path}")
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # Create a collection for job listings
    try:
        collection = client.get_collection("job_listings")
        print("Collection 'job_listings' already exists")
    except Exception:
        print("Creating new collection 'job_listings'")
        collection = client.create_collection(
            name="job_listings",
            metadata={"hnsw:space": "cosine"}
        )
    
    # Prepare your data for insertion
    ids = [str(i) for i in range(len(df))]
    documents = df['combined_text'].tolist()
    metadatas = df[['job_id', 'company_name', 'title_clean', 'location', 'location_normalized', 'remote_allowed', 'combined_skills']].to_dict('records')
    
    # Get embeddings
    embeddings = np.array(df['embedding'].tolist())
    
    # Add documents in batches
    batch_size = 500
    total_batches = (len(df) - 1) // batch_size + 1
    
    for i in range(0, len(df), batch_size):
        end_idx = min(i + batch_size, len(df))
        batch_num = i // batch_size + 1
        
        print(f"Adding batch {batch_num}/{total_batches} ({end_idx-i} documents)...")
        
        try:
            collection.add(
                ids=ids[i:end_idx],
                embeddings=embeddings[i:end_idx].tolist(),
                documents=documents[i:end_idx],
                metadatas=metadatas[i:end_idx]
            )
            print(f"Successfully added batch {batch_num}")
        except Exception as e:
            print(f"Error adding batch {batch_num}: {e}")
            raise
        
    print(f"Successfully added {len(df)} documents to the database")

if __name__ == "__main__":
    build_vector_database()