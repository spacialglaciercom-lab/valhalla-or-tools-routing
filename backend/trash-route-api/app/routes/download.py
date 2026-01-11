"""Route download endpoints"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import logging

from ..config import settings
from ..utils.file_handler import FileHandler
from ..services.progress_tracker import progress_tracker, JobStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/trash-route", tags=["trash-route"])
file_handler = FileHandler(
    uploads_dir=settings.uploads_dir,
    outputs_dir=settings.outputs_dir,
    max_file_size_bytes=settings.max_file_size_bytes,
    retention_hours=settings.TEMP_FILE_RETENTION_HOURS
)


@router.get("/download/{job_id}")
async def download_gpx(job_id: str):
    """
    Download generated GPX file.
    
    Returns GPX file for the completed job.
    """
    try:
        # Check job status
        job_status = progress_tracker.get_status(job_id)
        if not job_status:
            raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
        
        if job_status['status'] != JobStatus.COMPLETE:
            raise HTTPException(
                status_code=400,
                detail=f"Job not complete. Status: {job_status['status']}"
            )
        
        # Get output file path
        gpx_path = file_handler.get_output_path(job_id, "route.gpx")
        if not gpx_path or not Path(gpx_path).exists():
            raise HTTPException(status_code=404, detail=f"GPX file not found for job: {job_id}")
        
        logger.info(f"Downloading GPX file: {job_id} -> {gpx_path}")
        
        return FileResponse(
            path=gpx_path,
            filename="trash_collection_route.gpx",
            media_type="application/gpx+xml"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download failed for {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """
    Get job status and progress.
    
    Returns current status, progress percentage, and step information.
    """
    try:
        job_status = progress_tracker.get_status(job_id)
        if not job_status:
            raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
        
        from ..models import JobStatusResponse, Step
        
        return JobStatusResponse(
            job_id=job_id,
            status=job_status['status'],
            progress=job_status['progress'],
            step=job_status.get('step'),
            message=job_status['message'],
            stats=job_status.get('stats'),
            error=job_status.get('error')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")
