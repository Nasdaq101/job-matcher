# app.py (FastAPI backend)
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Union
import uvicorn
from retrieval.retrieval import JobRetriever
from agent.gemini_client import GeminiService
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Define data models
class JobSearchRequest(BaseModel):
    query: str
    location: Optional[str] = None
    remote: Optional[bool] = False
    skills: Optional[str] = None
    num_results: Optional[int] = 5

class JobResult(BaseModel):
    title: str
    company: str
    location: str
    remote: bool
    skills: str
    similarity: float
    job_id: Union[str, int]
    job_url: str
    document: str
    explanation: Optional[str] = None

# Initialize FastAPI app
app = FastAPI(title="LinkedIn Job Search API")

# Initialize the job retriever
retriever = JobRetriever()
gemini_service = GeminiService()

# Define API endpoints
@app.post("/search", response_model=List[JobResult])
async def search_jobs(request: JobSearchRequest):
    """Search for jobs based on query and filters"""
    filters = {}
    if request.location:
        filters["location"] = request.location
    if request.remote:
        filters["remote"] = request.remote
    if request.skills:
        filters["skills"] = request.skills
    
    results = retriever.search_jobs(
        request.query, 
        filters, 
        n_results=request.num_results
    )

        # Convert job_id to string in each result
    for result in results:
        result["job_id"] = str(result["job_id"])
    
    # Get explanations from Gemini
    if results:
        explanations = gemini_service.explain_job_matches(
            query=request.query,
            jobs=results,
            skills=request.skills
        )
        
        # Add explanations to results
        for result in results:
            job_id = result["job_id"]
            if job_id in explanations:
                result["explanation"] = explanations[job_id]
    
    return results

@app.get("/job/{job_id}")
async def get_job(job_id: str):
    """Get details for a specific job"""
    job = retriever.get_job_by_id(job_id)
    if not job:
        return {"error": "Job not found"}
    return job

@app.get("/")
async def root():
    """Root endpoint to verify API is working"""
    return {"message": "LinkedIn Job Search API is running. Use /search endpoint to find jobs."}

# Run the API server when the script is executed
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
