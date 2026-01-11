"""File handling utilities"""

import os
import shutil
import uuid
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class FileHandler:
    """Handle temporary file storage and cleanup"""
    
    def __init__(self, uploads_dir: str, outputs_dir: str, 
                 max_file_size_bytes: int, retention_hours: int = 24):
        """
        Initialize file handler
        
        Args:
            uploads_dir: Directory for uploaded files
            outputs_dir: Directory for output files
            max_file_size_bytes: Maximum file size in bytes
            retention_hours: Hours to retain files before cleanup
        """
        self.uploads_dir = Path(uploads_dir)
        self.outputs_dir = Path(outputs_dir)
        self.max_file_size_bytes = max_file_size_bytes
        self.retention_hours = retention_hours
        
        # Ensure directories exist
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
    
    def save_upload(self, file_content: bytes, filename: str, 
                   job_id: Optional[str] = None) -> Tuple[str, str]:
        """
        Save uploaded file
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            job_id: Optional job ID (if None, generates one)
            
        Returns:
            Tuple of (job_id, file_path)
        """
        # Validate file size
        if len(file_content) > self.max_file_size_bytes:
            raise ValueError(f"File size {len(file_content)} exceeds maximum {self.max_file_size_bytes} bytes")
        
        # Generate job ID if not provided
        if job_id is None:
            job_id = str(uuid.uuid4())
        
        # Create job directory
        job_dir = self.uploads_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine file extension and save
        file_path = job_dir / "input.osm"
        if filename.endswith('.pbf'):
            file_path = job_dir / "input.pbf"
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        logger.info(f"Saved upload: {job_id} -> {file_path}")
        return job_id, str(file_path)
    
    def get_upload_path(self, job_id: str) -> Optional[str]:
        """Get upload file path for a job"""
        job_dir = self.uploads_dir / job_id
        # Try different extensions
        for ext in ['.osm', '.pbf', '.xml']:
            file_path = job_dir / f"input{ext}"
            if file_path.exists():
                return str(file_path)
        return None
    
    def save_output(self, job_id: str, gpx_content: bytes, filename: str = "route.gpx") -> str:
        """
        Save generated GPX file
        
        Args:
            job_id: Job ID
            gpx_content: GPX file content as bytes
            filename: Output filename
            
        Returns:
            Path to saved file
        """
        job_dir = self.outputs_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = job_dir / filename
        with open(file_path, 'wb') as f:
            f.write(gpx_content)
        
        logger.info(f"Saved output: {job_id} -> {file_path}")
        return str(file_path)
    
    def get_output_path(self, job_id: str, filename: str = "route.gpx") -> Optional[str]:
        """Get output file path for a job"""
        file_path = self.outputs_dir / job_id / filename
        if file_path.exists():
            return str(file_path)
        return None
    
    def cleanup_old_files(self) -> int:
        """
        Clean up old files
        
        Returns:
            Number of files/directories cleaned up
        """
        cutoff = datetime.now() - timedelta(hours=self.retention_hours)
        cleaned = 0
        
        # Clean uploads
        for job_dir in self.uploads_dir.iterdir():
            if job_dir.is_dir():
                mtime = datetime.fromtimestamp(job_dir.stat().st_mtime)
                if mtime < cutoff:
                    try:
                        shutil.rmtree(job_dir)
                        cleaned += 1
                    except Exception as e:
                        logger.warning(f"Failed to clean {job_dir}: {e}")
        
        # Clean outputs
        for job_dir in self.outputs_dir.iterdir():
            if job_dir.is_dir():
                mtime = datetime.fromtimestamp(job_dir.stat().st_mtime)
                if mtime < cutoff:
                    try:
                        shutil.rmtree(job_dir)
                        cleaned += 1
                    except Exception as e:
                        logger.warning(f"Failed to clean {job_dir}: {e}")
        
        logger.info(f"Cleaned up {cleaned} old job directories")
        return cleaned
