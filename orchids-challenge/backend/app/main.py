from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
import asyncio
import uuid
import os
from datetime import datetime
import json
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .scraper import WebsiteScraper
from .llm_clone import WebsiteCloner

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI instance
app = FastAPI(
    title="Website Cloning API",
    description="API for cloning websites using AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories for storing jobs and results
os.makedirs("jobs", exist_ok=True)
os.makedirs("cache", exist_ok=True)

# In-memory job storage
jobs = {}

# Initialize scraper and cloner
scraper = WebsiteScraper()
cloner = WebsiteCloner()

# Pydantic models
class CloneRequest(BaseModel):
    url: HttpUrl
    model: Optional[str] = None  # Can be "claude" or "gemini"

class CloneResponse(BaseModel):
    job_id: str
    status: str
    message: str

class JobStatus(BaseModel):
    job_id: str
    status: str
    message: str
    result: Optional[Dict[str, Any]] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Website Cloning API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "website-cloning-api"}

@app.post("/clone", response_model=CloneResponse)
async def clone_website(request: CloneRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    
    # Store job info
    jobs[job_id] = {
        "status": "pending",
        "url": str(request.url),
        "model": request.model,
        "started_at": datetime.now().isoformat(),
        "message": "Job created, starting processing"
    }
    
    # Start processing in background
    background_tasks.add_task(process_clone_job, job_id, str(request.url), request.model)
    
    return {
        "job_id": job_id,
        "status": "pending",
        "message": "Website cloning job started"
    }

@app.get("/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return {
        "job_id": job_id,
        **jobs[job_id]
    }

@app.get("/jobs")
async def get_all_jobs():
    return {"jobs": [
        {"job_id": job_id, **job_info}
        for job_id, job_info in jobs.items()
    ]}

async def process_clone_job(job_id: str, url: str, model: Optional[str] = None):
    try:
        # Update job status
        jobs[job_id]["status"] = "scraping"
        jobs[job_id]["message"] = "Scraping website content"
        
        # Check cache first
        cached_data = scraper.get_cached_website_data(url)
        
        if cached_data:
            design_context = cached_data
            jobs[job_id]["message"] = "Using cached website data"
        else:
            # Scrape website
            design_context = await scraper.scrape_website(url)
            # Save to cache for future use
            scraper.save_to_cache(url, design_context)
        
        # Update job status
        jobs[job_id]["status"] = "generating"
        jobs[job_id]["message"] = "Generating website clone using AI"
        
        # Generate clone using LLM
        result = await cloner.generate_clone(design_context, model)
        
        # Save result
        job_result_path = os.path.join("jobs", f"{job_id}.json")
        with open(job_result_path, "w") as f:
            json.dump({
                "html": result["generated_html"],
                "model_used": result["model_used"],
                "url": url,
                "completed_at": datetime.now().isoformat()
            }, f)
        
        # Update job status
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["message"] = "Website clone generated successfully"
        jobs[job_id]["completed_at"] = datetime.now().isoformat()
        jobs[job_id]["result"] = {
            "html": result["generated_html"][:500] + "...",  # Preview only
            "model_used": result["model_used"]
        }
        
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["message"] = f"Failed to clone website: {str(e)}"
        jobs[job_id]["completed_at"] = datetime.now().isoformat()

@app.get("/clone/{job_id}/html")
async def get_cloned_html(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    if jobs[job_id]["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"Job {job_id} is not completed yet")
    
    job_result_path = os.path.join("jobs", f"{job_id}.json")
    
    if not os.path.exists(job_result_path):
        raise HTTPException(status_code=404, detail=f"Result file for job {job_id} not found")
    
    with open(job_result_path, "r") as f:
        result = json.load(f)
    
    return {"html": result["html"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
