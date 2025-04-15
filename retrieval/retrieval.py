import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np
import os

class JobRetriever:
    def __init__(self, db_path="./chroma_db"):
        """Initialize the retriever with the path to the Chroma database"""
        print("Initializing JobRetriever...")
        
        # Load the embedding model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Loaded embedding model: all-MiniLM-L6-v2")
        
        # Connect to the Chroma database
        self.client = chromadb.PersistentClient(path=db_path)
        try:
            self.collection = self.client.get_collection("job_listings")
            count = self.collection.count()
            print(f"Connected to existing collection 'job_listings' with {count} documents")
        except Exception as e:
            print(f"Error connecting to collection: {e}")
            raise
    
    def get_embedding(self, text):
        """Convert text to embedding vector"""
        return self.model.encode(text)
    
    def search_jobs(self, query, filters=None, n_results=5):
        """Search for jobs based on query and optional filters"""
        print(f"Searching for: '{query}' with filters: {filters}")
        
        # Create embedding for the query
        query_embedding = self.get_embedding(query)
        
        try:
            # Start with a basic query
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=100,  # Get more results initially to filter
                include=["documents", "metadatas", "distances"]
            )
            
            # Format and filter the results
            formatted_results = []
            if results['ids'] and results['ids'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    # Apply manual filtering
                    if filters:
                        # Location filter
                        if "location" in filters and filters["location"]:
                            location_terms = filters["location"].lower().split()
                            location_matches = False
                            for term in location_terms:
                                if term in metadata['location'].lower():
                                    location_matches = True
                                    break
                            if not location_matches:
                                continue
                        
                        # Remote filter
                        if "remote" in filters and filters["remote"] and \
                        not metadata['remote_allowed']:
                            continue
                        
                        # Skills filter - match multiple skills
                        if "skills" in filters and filters["skills"]:
                            required_skills = [s.strip().lower() for s in filters["skills"].split(',')]
                            job_skills = metadata['combined_skills'].lower()
                            
                            # Count how many required skills the job has
                            skill_matches = sum(1 for skill in required_skills if skill in job_skills)
                            skill_match_ratio = skill_matches / len(required_skills)
                            
                            # Require at least 50% of skills to match
                            if skill_match_ratio < 0.5:
                                continue
                    
                    similarity_score = 1 - distance
                    job_url = f"https://www.linkedin.com/jobs/view/{metadata['job_id']}"
                    
                    formatted_results.append({
                        "rank": len(formatted_results) + 1,
                        "title": metadata['title_clean'],
                        "company": metadata['company_name'],
                        "location": metadata['location'],
                        "remote": metadata['remote_allowed'],
                        "skills": metadata['combined_skills'],
                        "similarity": similarity_score,
                        "job_id": metadata['job_id'],
                        "job_url": job_url,
                        "document": doc
                    })
                    
                    # Stop once we have enough results
                    if len(formatted_results) >= n_results:
                        break
            
            print(f"Found {len(formatted_results)} matching jobs after filtering")
            return formatted_results
        
        except Exception as e:
            print(f"Error during search: {e}")
            return []
    
    def get_job_by_id(self, job_id):
        """
        Retrieve a specific job by its ID
        
        Parameters:
        - job_id (str): The LinkedIn job ID
        
        Returns:
        - dict: Job details or None if not found
        """
        try:
            results = self.collection.query(
                query_embeddings=None,
                where={"job_id": job_id},
                include=["documents", "metadatas"],
                n_results=1
            )
            
            if results['ids'][0]:
                metadata = results['metadatas'][0][0]
                doc = results['documents'][0][0]
                
                return {
                    "title": metadata['title_clean'],
                    "company": metadata['company_name'],
                    "location": metadata['location'],
                    "remote": metadata['remote_allowed'],
                    "skills": metadata['combined_skills'],
                    "job_id": metadata['job_id'],
                    "document": doc
                }
            return None
        except Exception as e:
            print(f"Error retrieving job {job_id}: {e}")
            return None

# Simple test code
if __name__ == "__main__":
    retriever = JobRetriever()
    results = retriever.search_jobs("Python developer with AWS experience")
    for job in results:
        print(f"{job['rank']}. {job['title']} at {job['company']} - Match: {job['similarity']:.2f}")
        print(f"   Skills: {job['skills']}")
        print(f"   Location: {job['location']}, Remote: {job['remote']}")
        print()