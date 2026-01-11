"""Progress tracking service for route generation jobs"""

import asyncio
import time
from typing import Dict, Optional, Callable
from datetime import datetime, timedelta
from ..models import JobStatus, ProgressEvent, Step

class ProgressTracker:
    """In-memory progress tracker for route generation jobs"""
    
    def __init__(self):
        """Initialize progress tracker"""
        self.jobs: Dict[str, Dict] = {}
        self.callbacks: Dict[str, Callable] = {}
        
    def create_job(self, job_id: str, upload_id: str, config: dict) -> None:
        """Create a new job entry"""
        self.jobs[job_id] = {
            'job_id': job_id,
            'upload_id': upload_id,
            'config': config,
            'status': JobStatus.PENDING,
            'progress': 0,
            'step': None,
            'message': 'Job created',
            'stats': {},
            'error': None,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
    
    def update_progress(self, job_id: str, step: Step, progress: int, 
                       message: str, stats: Optional[dict] = None) -> None:
        """Update job progress"""
        if job_id not in self.jobs:
            return
        
        self.jobs[job_id].update({
            'status': JobStatus.PROCESSING if step != Step.COMPLETE and step != Step.ERROR else 
                     (JobStatus.COMPLETE if step == Step.COMPLETE else JobStatus.ERROR),
            'progress': progress,
            'step': step,
            'message': message,
            'stats': stats or self.jobs[job_id].get('stats', {}),
            'updated_at': datetime.now()
        })
        
        # Notify callbacks
        if job_id in self.callbacks:
            try:
                event = ProgressEvent(
                    step=step,
                    progress=progress,
                    message=message,
                    stats=stats
                )
                self.callbacks[job_id](event)
            except Exception as e:
                print(f"Error in progress callback for {job_id}: {e}")
    
    def set_error(self, job_id: str, error: str) -> None:
        """Set job error"""
        if job_id not in self.jobs:
            return
        
        self.jobs[job_id].update({
            'status': JobStatus.ERROR,
            'progress': 0,
            'step': Step.ERROR,
            'message': f'Error: {error}',
            'error': error,
            'updated_at': datetime.now()
        })
    
    def get_status(self, job_id: str) -> Optional[dict]:
        """Get job status"""
        return self.jobs.get(job_id)
    
    def register_callback(self, job_id: str, callback: Callable) -> None:
        """Register callback for progress updates"""
        self.callbacks[job_id] = callback
    
    def unregister_callback(self, job_id: str) -> None:
        """Unregister callback"""
        if job_id in self.callbacks:
            del self.callbacks[job_id]
    
    def cleanup_old_jobs(self, retention_hours: int = 24) -> None:
        """Clean up old completed jobs"""
        cutoff = datetime.now() - timedelta(hours=retention_hours)
        jobs_to_remove = [
            job_id for job_id, job in self.jobs.items()
            if job['status'] in [JobStatus.COMPLETE, JobStatus.ERROR] and
               job['updated_at'] < cutoff
        ]
        for job_id in jobs_to_remove:
            self.unregister_callback(job_id)
            del self.jobs[job_id]


# Global instance
progress_tracker = ProgressTracker()
