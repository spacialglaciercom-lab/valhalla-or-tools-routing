"""Route generation endpoint"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
import logging
import uuid
import asyncio
from pathlib import Path

from ..models import GenerateRequest, JobResponse, JobStatus, Step
from ..config import settings
from ..utils.file_handler import FileHandler
from ..services.route_generator import RouteGeneratorService
from ..services.progress_tracker import progress_tracker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/trash-route", tags=["trash-route"])
file_handler = FileHandler(
    uploads_dir=settings.uploads_dir,
    outputs_dir=settings.outputs_dir,
    max_file_size_bytes=settings.max_file_size_bytes,
    retention_hours=settings.TEMP_FILE_RETENTION_HOURS
)


async def generate_route_task(job_id: str, upload_id: str, config: dict):
    """Background task for route generation"""
    try:
        # Get upload file path
        osm_file = file_handler.get_upload_path(upload_id)
        if not osm_file:
            progress_tracker.set_error(job_id, f"Upload file not found: {upload_id}")
            return
        
        # Create output directory for this job
        output_dir = Path(settings.outputs_dir) / job_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create route generator service
        generator_service = RouteGeneratorService(
            job_id=job_id,
            osm_file=osm_file,
            output_dir=str(output_dir),
            config=config
        )
        
        # Generate route
        gpx_path, report_path = generator_service.generate(
            output_gpx="route.gpx",
            output_report="report.md",
            start_node=config.get('start_node')
        )
        
        # Get summary stats
        summary = generator_service.get_summary()
        
        # Final progress update
        progress_tracker.update_progress(
            job_id=job_id,
            step=Step.COMPLETE,
            progress=100,
            message="Route generation complete",
            stats={
                'gpx_path': gpx_path,
                'report_path': report_path,
                'summary': summary
            }
        )
        
        logger.info(f"Route generation complete: {job_id}")
        
    except Exception as e:
        logger.error(f"Route generation failed for {job_id}: {e}")
        progress_tracker.set_error(job_id, str(e))


@router.post("/generate", response_model=JobResponse)
async def generate_route(request: GenerateRequest, background_tasks: BackgroundTasks):
    """
    Generate trash collection route from uploaded OSM file.
    
    Returns job_id for tracking progress.
    """
    try:
        # Validate upload exists
        osm_file = file_handler.get_upload_path(request.upload_id)
        if not osm_file:
            raise HTTPException(
                status_code=404,
                detail=f"Upload not found: {request.upload_id}"
            )
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Create job entry
        config_dict = request.config.model_dump()
        progress_tracker.create_job(job_id, request.upload_id, config_dict)
        
        # Start background task
        background_tasks.add_task(
            generate_route_task,
            job_id=job_id,
            upload_id=request.upload_id,
            config=config_dict
        )
        
        logger.info(f"Route generation started: {job_id} for upload {request.upload_id}")
        
        return JobResponse(
            job_id=job_id,
            status=JobStatus.PENDING,
            message="Route generation started"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start route generation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start generation: {str(e)}")
