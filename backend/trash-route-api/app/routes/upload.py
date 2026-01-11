"""File upload route"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional
import logging

from ..models import UploadResponse
from ..config import settings
from ..utils.file_handler import FileHandler

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/trash-route", tags=["trash-route"])
file_handler = FileHandler(
    uploads_dir=settings.uploads_dir,
    outputs_dir=settings.outputs_dir,
    max_file_size_bytes=settings.max_file_size_bytes,
    retention_hours=settings.TEMP_FILE_RETENTION_HOURS
)


@router.post("/upload", response_model=UploadResponse)
async def upload_osm_file(file: UploadFile = File(...)):
    """
    Upload OSM file for route generation.
    
    Supports .osm, .xml, and .pbf formats.
    """
    try:
        # Validate file extension
        filename = file.filename or ""
        if not filename.lower().endswith(('.osm', '.xml', '.pbf')):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Supported formats: .osm, .xml, .pbf"
            )
        
        # Read file content
        content = await file.read()
        
        # Validate file size
        if len(content) > settings.max_file_size_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum of {settings.MAX_FILE_SIZE_MB}MB"
            )
        
        # Save file
        upload_id, file_path = file_handler.save_upload(content, filename)
        
        logger.info(f"File uploaded: {filename} -> {upload_id}")
        
        return UploadResponse(
            upload_id=upload_id,
            filename=filename,
            file_size=len(content),
            message="File uploaded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
