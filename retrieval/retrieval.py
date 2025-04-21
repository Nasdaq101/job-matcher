import chromadb
import os
import shutil
import numpy as np
from sentence_transformers import SentenceTransformer
from vector_db.build_vector_db import build_vector_database
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from normalizers import (
    normalize_location,
    normalize_title,
    normalize_skill,
    get_related_skills
)

class JobRetriever:
    def __init__(self, db_path="./chroma_db"):
        """Initialize the retriever with the path to the Chroma database"""
        print("Initializing JobRetriever...")
        
        # Load the embedding model
        self.model = SentenceTransformer('TechWolf/JobBERT-v2')
        print("Loaded embedding model: TechWolf/JobBERT-v2")
        
        # Initialize TF-IDF vectorizer for skills
        self.skill_vectorizer = TfidfVectorizer(lowercase=True)
        
        # Connect to the Chroma database
        try:
            self.client = chromadb.PersistentClient(path=db_path)
            self.collection = self.client.get_collection("job_listings")
            count = self.collection.count()
            print(f"Connected to existing collection 'job_listings' with {count} documents")
        except Exception as e:
            print(f"Error connecting to collection: {e}")
            
            if os.path.exists(db_path):
                shutil.rmtree(db_path)
            
            # Rebuild the database
            build_vector_database()
            
            # Try connecting again
            self.client = chromadb.PersistentClient(path=db_path)
            self.collection = self.client.get_collection("job_listings")
            count = self.collection.count()
            print(f"Rebuilt collection 'job_listings' with {count} documents")
        
        
    
    def get_embedding(self, text: str) -> np.ndarray:
        """Convert text to embedding vector"""
        return self.model.encode(text)
    
    def compute_similarity_scores(
        self,
        query: str,
        query_skills: List[str],
        query_location: Optional[str],
        job_metadata: Dict[str, Any],
        job_doc: str,
        semantic_score: float
    ) -> Dict[str, float]:
        """
        Compute multi-factor similarity scores between query and job.
        
        Args:
            query: The search query
            query_skills: List of normalized skills from query
            query_location: Normalized location from query
            job_metadata: Job metadata
            job_doc: Job description
            semantic_score: Pre-computed semantic similarity score
            
        Returns:
            Dictionary of component scores
        """
        scores = {
            'semantic': semantic_score,
            'title': 0.0,
            'skills': 0.0,
            'location': 0.0
        }
        
        # Title similarity
        query_title = normalize_title(query)
        job_title = normalize_title(job_metadata['title_clean'])
        if query_title == job_title:
            scores['title'] = 1.0
        else:
            # Use semantic similarity for non-exact matches
            title_embedding = self.get_embedding(query_title)
            job_title_embedding = self.get_embedding(job_title)
            scores['title'] = cosine_similarity(
                title_embedding.reshape(1, -1),
                job_title_embedding.reshape(1, -1)
            )[0][0]
        
        # Skills similarity
        if query_skills:
            # Get job skills
            job_skills = normalize_skill(job_metadata['combined_skills'].split(','))
            
            # Calculate skill overlap
            common_skills = set(query_skills) & set(job_skills)
            if query_skills:
                scores['skills'] = len(common_skills) / len(query_skills)
            
            # Add partial credit for related skills
            if scores['skills'] < 1.0:
                related_matches = 0
                for skill in query_skills:
                    if skill not in common_skills:
                        related = get_related_skills(skill)
                        if any(r in job_skills for r in related):
                            related_matches += 0.5
                if query_skills:
                    scores['skills'] += (related_matches / len(query_skills))
                scores['skills'] = min(scores['skills'], 1.0)
        
        # Location matching
        if query_location:
            job_location = job_metadata['location_normalized']
            print(job_location, query_location)
            
            # Handle remote jobs first
            if job_metadata.get('remote_allowed', False):
                scores['location'] = 0.8  # High score for remote jobs
            else:
                # Use embedding similarity for location matching
                location_embedding = self.get_embedding(query_location)
                job_location_embedding = self.get_embedding(job_location)
                
                location_similarity = cosine_similarity(
                    location_embedding.reshape(1, -1),
                    job_location_embedding.reshape(1, -1)
                )[0][0]
                
                # Scale similarity and favor exact matches
                scores['location'] = location_similarity * 0.5
                
                # Boost score for exact matches
                if query_location == job_location:
                    scores['location'] = 1.0
        ## Debug purpose
        # print(scores)
        return scores
    
    def compute_final_score(self, scores: Dict[str, float], weights: Optional[Dict[str, float]] = None) -> float:
        """
        Compute final weighted score from component scores.
        
        Args:
            scores: Dictionary of component scores
            weights: Optional dictionary of weights for each component
            
        Returns:
            Final weighted score
        """
        if weights is None:
            weights = {
                'semantic': 0.1,
                'title': 0.3,
                'skills': 0.2,
                'location': 0.4
            }
        
        final_score = 0.0
        for component, score in scores.items():
            final_score += score * weights[component]
        
        return final_score
    
    def search_jobs(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        n_results: int = 5,
        weights: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for jobs based on query and optional filters.
        
        Args:
            query: Search query
            filters: Optional filters (location, skills, etc.)
            n_results: Number of results to return
            weights: Optional weights for scoring components
            
        Returns:
            List of ranked job results
        """
        print(f"Searching for: '{query}' with filters: {filters}")
        
        try:
            # Extract and normalize query components
            query_skills = []
            query_location = None
            if filters:
                if 'skills' in filters:
                    query_skills = normalize_skill(filters['skills'].split(','))
                if 'location' in filters:
                    query_location = normalize_location(filters['location'], enable_geolocator=True)

            # Get initial candidates using semantic search
            title_emb = self.get_embedding(query)
            location_emb = self.get_embedding(query_location)
            skills_emb = self.get_embedding(query_skills)

            TITLE_WEIGHT = 0.2
            LOCATION_WEIGHT = 0.7
            SKILLS_WEIGHT = 0.1

            # Compute weighted sum
            query_embedding = TITLE_WEIGHT * title_emb + LOCATION_WEIGHT * location_emb + SKILLS_WEIGHT * skills_emb

            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=100,  # Get more results initially for reranking
                include=["documents", "metadatas", "distances"]
            )
            
            # Process and rerank results
            candidates = []
            if results['ids'] and results['ids'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    # Apply hard filters first
                    if filters:
                        # Remote filter
                        if "remote" in filters and filters["remote"] and \
                        not metadata['remote_allowed']:
                            continue
                    
                    # Compute component scores
                    semantic_score = 1 - distance
                    ## Debug purpose
                    # print(metadata['location_normalized'])
                    scores = self.compute_similarity_scores(
                        query=query,
                        query_skills=query_skills,
                        query_location=query_location,
                        job_metadata=metadata,
                        job_doc=doc,
                        semantic_score=semantic_score
                    )
                    
                    # Compute final score
                    final_score = self.compute_final_score(scores, weights)
                    
                    # Add to candidates if score is good enough
                    if final_score > 0.3:  # Minimum threshold
                        job_url = f"https://www.linkedin.com/jobs/view/{metadata['job_id']}"
                        candidates.append({
                            "rank": len(candidates) + 1,
                            "title": metadata['title_clean'],
                            "company": metadata['company_name'],
                            "location": metadata['location'],
                            "remote": metadata['remote_allowed'],
                            "skills": metadata['combined_skills'],
                            "similarity": final_score,
                            "component_scores": scores,
                            "job_id": metadata['job_id'],
                            "job_url": job_url,
                            "document": doc
                        })
            
            # Sort by final score and apply diversity
            candidates.sort(key=lambda x: x['similarity'], reverse=True)
            diverse_results = self._ensure_diversity(candidates, n_results)
            
            print(f"Found {len(diverse_results)} matching jobs after filtering and diversity")
            return diverse_results
            
        except Exception as e:
            print(f"Error during search: {e}")
            return []
    
    def _ensure_diversity(
        self,
        candidates: List[Dict[str, Any]],
        n_results: int
    ) -> List[Dict[str, Any]]:
        """
        Ensure diversity in results by avoiding duplicate and too similar jobs.
        
        Args:
            candidates: List of candidate jobs
            n_results: Number of results desired
            
        Returns:
            Diverse subset of candidates
        """
        if len(candidates) <= n_results:
            return candidates
        
        diverse_results = []
        seen_job_ids = set()
        seen_titles = set()
        seen_companies = set()
        
        # Always include top result
        if candidates:
            diverse_results.append(candidates[0])
            seen_job_ids.add(candidates[0]['job_id'])
            seen_titles.add(normalize_title(candidates[0]['title']))
            seen_companies.add(candidates[0]['company'])
        
        # Add remaining results ensuring diversity
        for job in candidates[1:]:
            if len(diverse_results) >= n_results:
                break
                
            # Skip exact duplicate jobs
            if job['job_id'] in seen_job_ids:
                continue
            
            normalized_title = normalize_title(job['title'])
            
            # Skip if we have too many of same title or company
            if (
                sum(1 for t in seen_titles if t == normalized_title) >= 2 or
                sum(1 for c in seen_companies if c == job['company']) >= 2
            ):
                continue
            
            diverse_results.append(job)
            seen_job_ids.add(job['job_id'])
            seen_titles.add(normalized_title)
            seen_companies.add(job['company'])
        
        return diverse_results
    
    def get_job_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific job by its ID.
        
        Args:
            job_id: The LinkedIn job ID
            
        Returns:
            Job details or None if not found
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