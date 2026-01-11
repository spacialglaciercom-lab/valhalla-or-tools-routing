"""Pydantic models for Trash Route API"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class Step(str, Enum):
    """Progress step enum"""
    PARSING = "parsing"
    BUILDING = "building"
    ANALYZING = "analyzing"
    SOLVING = "solving"
    OPTIMIZING = "optimizing"
    WRITING = "writing"
    COMPLETE = "complete"
    ERROR = "error"


class JobStatus(str, Enum):
    """Job status enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    ERROR = "error"


class TrashRouteConfig(BaseModel):
    """Configuration for route generation"""
    ignore_oneway: bool = Field(True, description="Ignore oneway restrictions (Option A)")
    highway_include: List[str] = Field(
        default=["residential", "unclassified", "service", "tertiary", "secondary"],
        description="Highway types to include"
    )
    excluded_conditions: List[str] = Field(
        default=["service=parking_aisle", "service=parking", "highway=footway", 
                 "highway=cycleway", "highway=steps", "highway=path", 
                 "highway=track", "highway=pedestrian", "access=private"],
        description="Conditions to exclude"
    )
    start_node: Optional[int] = Field(None, description="Optional starting node ID")
    prefer_right_turns: bool = Field(True, description="Prefer right turns in route")
    turn_cost_multiplier: float = Field(1.0, description="Penalty multiplier for left turns")


class UploadResponse(BaseModel):
    """Response from file upload"""
    upload_id: str
    filename: str
    file_size: int
    message: str


class GenerateRequest(BaseModel):
    """Request to generate route"""
    upload_id: str
    config: TrashRouteConfig


class JobResponse(BaseModel):
    """Response from route generation request"""
    job_id: str
    status: JobStatus
    message: str


class ProgressEvent(BaseModel):
    """Progress event model"""
    step: Step
    progress: int = Field(..., ge=0, le=100, description="Progress percentage 0-100")
    message: str
    stats: Optional[Dict[str, Any]] = None


class JobStatusResponse(BaseModel):
    """Response for job status query"""
    job_id: str
    status: JobStatus
    progress: int = Field(..., ge=0, le=100)
    step: Optional[Step] = None
    message: str
    stats: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
