from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import os
from retrieval import JobRetriever
from vector_db.build_vector_db import build_vector_database

# Initialize FastAPI app
app = FastAPI(title="LinkedIn Job Search RAG")

# Set up templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize the job retriever
retriever = JobRetriever()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page with search form"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/search", response_class=HTMLResponse)
async def search(
    request: Request, 
    query: str = Form(...), 
    location: str = Form(None), 
    remote: bool = Form(False),
    skills: str = Form(None),
    num_results: int = Form(5)
):
    """Process search request and display results"""
    # Prepare filters
    filters = {}
    if location and location.strip():
        filters["location"] = location
    if remote:
        filters["remote"] = True
    if skills and skills.strip():
        filters["skills"] = skills
    
    # Get search results using your existing retriever
    results = retriever.search_jobs(query, filters, n_results=num_results)
    
    # Return results page
    return templates.TemplateResponse(
        "results.html", 
        {
            "request": request, 
            "results": results, 
            "query": query,
            "location": location,
            "remote": remote,
            "skills": skills
        }
    )

@app.get("/job/{job_id}", response_class=HTMLResponse)
async def job_details(request: Request, job_id: str):
    """Show detailed information for a specific job"""
    job = retriever.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return templates.TemplateResponse(
        "job_details.html", 
        {"request": request, "job": job}
    )

@app.on_event("startup")
async def startup_event():
    """Initialize the database on startup if needed"""
    db_path = "./chroma_db"
    if not os.path.exists(db_path) or not os.listdir(db_path):
        print("Building vector database on startup...")
        build_vector_database()

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)