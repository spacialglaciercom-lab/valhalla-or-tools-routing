"""Job status endpoint"""

from fastapi import APIRouter, HTTPException
from app.models import JobStatus
from app.services.progress_tracker import progress_tracker

router = APIRouter(prefix="/status", tags=["status"])

@router.get("/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """
    Get status of a route generation job.
    
    Args:
        job_id: Job ID
        
    Returns:
        JobStatus
    """
    job = await progress_tracker.get_status(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )
    
    return job
