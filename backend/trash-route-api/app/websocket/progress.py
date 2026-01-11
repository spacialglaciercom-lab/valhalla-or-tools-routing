"""WebSocket handler for real-time progress updates"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import Set
import json
import logging
import asyncio

from ..models import ProgressEvent, Step
from ..services.progress_tracker import progress_tracker, JobStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws/trash-route", tags=["websocket"])


class ProgressWebSocketManager:
    """Manage WebSocket connections for progress updates"""
    
    def __init__(self):
        """Initialize WebSocket manager"""
        self.active_connections: Set[WebSocket] = set()
        self.job_connections: dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, job_id: str):
        """Connect WebSocket for a job"""
        await websocket.accept()
        self.active_connections.add(websocket)
        
        if job_id not in self.job_connections:
            self.job_connections[job_id] = set()
        self.job_connections[job_id].add(websocket)
        
        # Register callback for this job - broadcast to all connections for this job
        async def broadcast_to_job(event: ProgressEvent):
            """Broadcast progress event to all WebSocket connections for this job"""
            if job_id in self.job_connections:
                disconnected = set()
                for ws in self.job_connections[job_id]:
                    try:
                        await self.send_progress(ws, event)
                    except Exception as e:
                        logger.warning(f"Failed to send to WebSocket: {e}")
                        disconnected.add(ws)
                
                # Clean up disconnected connections
                for ws in disconnected:
                    self.job_connections[job_id].discard(ws)
                    self.active_connections.discard(ws)
        
        def callback(event: ProgressEvent):
            """Synchronous callback wrapper that creates async task"""
            asyncio.create_task(broadcast_to_job(event))
        
        progress_tracker.register_callback(job_id, callback)
        
        # Send initial status
        job_status = progress_tracker.get_status(job_id)
        if job_status:
            initial_event = ProgressEvent(
                step=job_status.get('step', Step.PARSING),
                progress=job_status.get('progress', 0),
                message=job_status.get('message', ''),
                stats=job_status.get('stats')
            )
            await self.send_progress(websocket, initial_event)
        
        logger.info(f"WebSocket connected for job {job_id}")
    
    def disconnect(self, websocket: WebSocket, job_id: str):
        """Disconnect WebSocket"""
        self.active_connections.discard(websocket)
        if job_id in self.job_connections:
            self.job_connections[job_id].discard(websocket)
            if not self.job_connections[job_id]:
                del self.job_connections[job_id]
                progress_tracker.unregister_callback(job_id)
        
        logger.info(f"WebSocket disconnected for job {job_id}")
    
    async def send_progress(self, websocket: WebSocket, event: ProgressEvent):
        """Send progress event to WebSocket"""
        try:
            await websocket.send_json(event.dict())
        except Exception as e:
            logger.warning(f"Failed to send progress to WebSocket: {e}")
            self.disconnect(websocket, job_id=None)


# Global WebSocket manager
ws_manager = ProgressWebSocketManager()


@router.websocket("/{job_id}")
async def websocket_progress(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time progress updates.
    
    Connects to job progress stream and sends updates as they occur.
    """
    # Verify job exists
    job_status = progress_tracker.get_status(job_id)
    if not job_status:
        await websocket.close(code=1008, reason=f"Job not found: {job_id}")
        return
    
    # Connect
    await ws_manager.connect(websocket, job_id)
    
    try:
        # Keep connection alive and handle messages
        while True:
            data = await websocket.receive_text()
            # Echo back for keep-alive (optional)
            if data == "ping":
                await websocket.send_text("pong")
    
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, job_id)
        logger.info(f"WebSocket disconnected: {job_id}")
    except Exception as e:
        logger.error(f"WebSocket error for {job_id}: {e}")
        ws_manager.disconnect(websocket, job_id)
